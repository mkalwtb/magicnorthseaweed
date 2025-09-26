from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.safestring import mark_safe

import os
import sys
from pathlib import Path

# Ensure the project's root is on sys.path so data.* modules import correctly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
DATA_DIR = PROJECT_ROOT / 'data'
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

# Import existing domain logic after path fix
from data.spots import SPOTS
from data.webtables import weekoverzicht, table_per_day, table_html, table_html_simple
from data.models import MODELS
from data.web_update_silent import get_cached_site_content


def _get_spot_by_name(spot_name: str):
    for spot in SPOTS:
        if spot.name.lower() == spot_name.lower():
            return spot
    return None


def home(request):
    return render(request, 'forecast/home.html', {})


def week_overview(request):
    content = get_cached_site_content()
    return render(request, 'forecast/embed.html', { 'content': mark_safe(content['week_overview']) })


def spot_table(request, spot_name: str):
    content = get_cached_site_content()
    if spot_name not in content['spot_tables']:
        spot = _get_spot_by_name(spot_name)
        if spot is None:
            raise Http404("Spot not found")
    html = content['spot_tables'].get(spot_name)
    return render(request, 'forecast/embed.html', { 'content': mark_safe(html) })


def spot_widget(request, spot_name: str):
    content = get_cached_site_content()
    if spot_name not in content['spot_widgets']:
        spot = _get_spot_by_name(spot_name)
        if spot is None:
            raise Http404("Spot not found")
    html = content['spot_widgets'].get(spot_name)
    return render(request, 'forecast/embed.html', { 'content': mark_safe(html) })

# Create your views here.
