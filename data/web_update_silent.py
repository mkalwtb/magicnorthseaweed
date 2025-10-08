import sys
import os
from pathlib import Path

import alert

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from matplotlib import pyplot as plt

from data.models import MODELS
from plotting import plot_forecast, save_to_web, plot_all
import webtables
from spots import SPOTS, texel_paal17, ijmuiden, ZV, schev, NW
from tabulate import tabulate
import pandas as pd
import json
import pickle
import threading
import time

CACHE_MAX_AGE_SECONDS = 60 * 60 * 12  # 12 hours
_CACHE_LOCK = threading.Lock()
_CACHE_STATE_FILE = Path(__file__).resolve().parent / 'site_cache_state.json'
_CACHE_CONTENT_FILE = Path(__file__).resolve().parent / 'site_cache_content.pkl'


def generate_site_content():
	"""Generate HTML content for the website without writing to disk.

	Returns a dict with keys:
	- 'week_overview': str
	- 'spot_tables': Dict[spot_name, str]
	- 'spot_widgets': Dict[spot_name, str]
	"""
	# Ensure relative cache paths used by stormglass resolve under the data folder
	data_dir = Path(__file__).resolve().parent
	old_cwd = Path.cwd()
	os.chdir(data_dir)
	try:
		# Ensure stormglass cache directory exists
		(data_dir / 'stormglass').mkdir(exist_ok=True)
		datas = []
		spot_tables = {}
		spot_widgets = {}
		for spot in SPOTS:
			# Never use spot.surf_rating(cache=True); always compute fresh
			data = spot.surf_rating(cache=False, models=MODELS)
			data.name = spot.name
			datas.append(data)
			spot_tables[spot.name] = webtables.table_per_day(data, spot, webtables.table_html)
			spot_widgets[spot.name] = webtables.table_html_simple(data, spot)

		# Build week overview HTML (webtables.weekoverzicht writes to disk), so emulate here
		n_hours_av = 3
		datas_daily = [spot_df.rolling(n_hours_av).mean().resample('D').max() for spot_df in datas]
		for data_daily, data in zip(datas_daily, datas):
			data_daily["hoogte-v2"] = data["hoogte-v2"].rolling(n_hours_av).mean().resample('D').mean()
		names = [spot_df.name for spot_df in datas]
		rating = pd.concat([spot_df["rating"] for spot_df in datas_daily], axis=1, keys=names)
		hoogte = pd.concat([spot_df["hoogte-v2"] for spot_df in datas_daily], axis=1, keys=names)
		html = webtables.head
		html += "<table>\n<tr>\n<th></th>\n" + "".join(f"<th>{n}</th>\n" for n in names) + "</tr>\n"
		for (index, row_rating), (_, row_hoogte) in zip(rating.iterrows(), hoogte.iterrows()):
			html += "<tr>\n"
			html += f"\t<td>{index.strftime('%A, %d-%m')}</td>\n"
			for name in names:
				color = webtables.get_color(row_rating[name])
				hv = webtables.height_label(row_hoogte[name], simple=True) if row_hoogte[name] > 0 else "geen data"
				color_bar = f"<div class='rounded-span'  style='background-color: {color}'></div>"
				html += f"\t<td style='text-align: left;'>{color_bar} <h3>{row_rating[name]:.1f}</h3> {hv}</td>\n"
			html += "</tr>\n"
		html += "</table>\n"

		return {
			"week_overview": html,
			"spot_tables": spot_tables,
			"spot_widgets": spot_widgets,
		}
	finally:
		os.chdir(old_cwd)


def _load_cached_content():
	try:
		import django
		import os
		from datetime import datetime
		
		# Setup Django if not already done
		if not django.apps.apps.ready:
			os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mswsite.settings')
			django.setup()
		
		from forecast.models import SiteCache
		
		# Try to load from database
		cache_key = "main_site_content"
		cache_obj = SiteCache.objects.filter(
			cache_key=cache_key,
			expires_at__gt=datetime.now()
		).first()
		
		if cache_obj:
			return cache_obj.content
		
		return None
		
	except Exception as e:
		print(f"Error loading cached content from database: {e}")
		# Fallback to pickle file
		if _CACHE_CONTENT_FILE.is_file():
			with open(_CACHE_CONTENT_FILE, 'rb') as f:
				return pickle.load(f)
		return None


def _save_cached_content(content):
	try:
		import django
		import os
		from datetime import datetime, timedelta
		
		# Setup Django if not already done
		if not django.apps.apps.ready:
			os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mswsite.settings')
			django.setup()
		
		from forecast.models import SiteCache
		
		# Save to database
		cache_key = "main_site_content"
		expires_at = datetime.now() + timedelta(days=1)  # Cache expires in 1 day
		
		SiteCache.objects.update_or_create(
			cache_key=cache_key,
			defaults={
				'content': str(content),
				'expires_at': expires_at
			}
		)
		
	except Exception as e:
		print(f"Error saving cached content to database: {e}")
		# Fallback to pickle file
		with open(_CACHE_CONTENT_FILE, 'wb') as f:
			pickle.dump(content, f)


def _get_last_update_ts():
	if _CACHE_STATE_FILE.is_file():
		with open(_CACHE_STATE_FILE, 'r') as f:
			try:
				state = json.load(f)
				return float(state.get('last_update_ts', 0))
			except Exception:
				return 0.0
	return 0.0


def _set_last_update_ts(ts: float):
	with open(_CACHE_STATE_FILE, 'w') as f:
		json.dump({'last_update_ts': ts}, f)


def _refresh_cache_background():
	try:
		content = generate_site_content()
		_save_cached_content(content)
		_set_last_update_ts(time.time())
	except Exception:
		# best-effort; keep old cache on error
		pass


def get_cached_site_content():
	"""Return cached content; if older than 12h, trigger background refresh.

	If no cache exists yet, compute synchronously once and save.
	"""
	with _CACHE_LOCK:
		last_ts = _get_last_update_ts()
		age = time.time() - last_ts
		content = _load_cached_content()
		if content is None:
			# First-time compute synchronously
			content = generate_site_content()
			_save_cached_content(content)
			_set_last_update_ts(time.time())
			return content
		if age > CACHE_MAX_AGE_SECONDS:
			# kick off background refresh if not already running
			threading.Thread(target=_refresh_cache_background, daemon=True).start()
		return content

if __name__ == '__main__':
	# Preserve legacy behavior: generate and write outputs
	datas = []
	for spot in SPOTS:  # [ijmuiden]:
		data = spot.surf_rating(cache=False, models=MODELS)
		data.name = spot.name
		datas.append(data)
		# alert.check(data, spot, alert_filters=alert.FILTERS)
		webtables.write_table_per_day(data, spot)
		webtables.write_simple_table(data, spot)
		# plot_forecast(data, spot, perks_plot=True)
		save_to_web(spot.name)

	if len(datas) == len(SPOTS):
		webtables.weekoverzicht(datas)

	ZV = [data for data in datas if data.name == "ZV"][0]
	ZV_simple = ZV.resample('D').max()
	# print(tabulate(ZV_simple[["rating", "hoogte-v2"]], headers='keys', floatfmt=".1"))

	# plt.show()