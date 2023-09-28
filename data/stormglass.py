from pathlib import Path
import pandas as pd
import numpy as np
import arrow
import requests
import json
from tabulate import tabulate
from matplotlib import pyplot as plt
from datetime import datetime
import pytz

file = Path('data.pkl')
channels = ['waveDirection', 'wavePeriod', "waveHeight", "windSpeed", 'windDirection',
            "seaLevel", "windWaveHeight"]  # "currentSpeed"

# Get first hour of today
def download_json(lat, long, start, end, cache=False):
  cache_file = Path('response.json')

  if cache_file.is_file() and cache:
    print("Cached")
    with open(cache_file, 'r') as f:
      json_data = json.load(f)
  else:
    print(f"Scraping from {start} to {end} with cache={cache}")
    response = requests.get(
      'https://api.stormglass.io/v2/weather/point',
      params={
        'lat': lat,
        'lng': long,
        'params': ','.join(channels),
        'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
        'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
      },
      headers={
        # 'Authorization': '1feeb6a8-5bc9-11ee-a26f-0242ac130002-1feeb702-5bc9-11ee-a26f-0242ac130002'
        # 'Authorization': '5bf98f1a-2979-11ee-8d52-0242ac130002-5bf98f88-2979-11ee-8d52-0242ac130002'
        'Authorization': 'a5396776-5d64-11ee-8b7f-0242ac130002-a53967da-5d64-11ee-8b7f-0242ac130002'
      }
    )

    json_data = response.json()
    with open(cache_file, 'w') as f:
      json.dump(json_data, f)  # dumps response from API in response.json (cache_file)

  return json_data

def json_to_df(json_data):
  hourly_data = {}
  if 'hours' not in json_data:
      raise Exception('Something went wrong with the stormglass API request')

  for entry in json_data['hours']:
      name = entry['time']
      hourly_data[name] = {}
      for channel in channels:
          hourly_data[name][channel] = entry[channel]['sg']

  # Create a Pandas DataFrame
  df = pd.DataFrame.from_dict(hourly_data, orient='index')
  df.index = pd.to_datetime(df.index)
  df.index = df.index.tz_convert(pytz.timezone('CET'))
  return df


def download_and_save_data(lat, long, start, end, cache=False):
    json_data = download_json(lat=lat, long=long, start=start, end=end, cache=cache)
    data_new = json_to_df(json_data)
    if file.is_file():
        data_db = pd.read_pickle(file)
        data_new = pd.concat([data_db, data_new], axis=0)
    if len(data_new) > 0:  # save data
        data_new.to_pickle(file)
    return data_new

def load_data(lat, long):
    if file.is_file():
        data_db = pd.read_pickle(file)
    else:
        data_db = pd.DataFrame()
    return data_db


def load_and_download_data(lat, long, start, end, cache=False):
    # Timing
    now = datetime.now()
    data_db = load_data(lat, long)


    start_in_df = arrow.get(data_db.index.min()) <= start
    end_in_df = arrow.get(data_db.index.max()) >= end
    if not start_in_df or not end_in_df:
        print("Scraping new data")
        json_data = download_json(lat=lat, long=long, start=start, end=end, cache=cache)
        data_new = json_to_df(json_data)
        tz = data_new.index.tz
        now_pd = pd.to_datetime(now, utc=tz)
        data_new_historical = data_new[data_new.index <= now_pd]
        if len(data_new_historical) > 0:  # save data
            data_db = pd.concat([data_db, data_new_historical], axis=0)
            data_db.to_pickle(file)
        result = pd.concat([data_db, data_new], axis=0)
    else:
        result = data_db

    tz = result.index.tz
    start_pd = pd.to_datetime(start.datetime, utc=tz)
    end_pd = pd.to_datetime(end.datetime, utc=tz)
    result_range = result[(result.index >=start_pd) & (result.index <= end_pd)]
    return result_range


def append_x_days_upfront(lat, long, days, cache=False):
    data = load_data(lat, long)
    oldest = arrow.get(min(data.index))
    new_oldest = oldest.shift(days=-days)
    return download_and_save_data(lat, long, new_oldest, oldest, cache=cache)


if __name__ == '__main__':
    lat = 52.464295
    long = 4.532720
    now = arrow.now('Europe/Amsterdam')
    start = now.shift(hours=0)
    end = now.shift(hours=48)
    cache=False

    # Forecast
    # json_data = download_json(lat, long, start, end, cache=True)
    # df = json_to_df(json_data)

    # Historical
    # download_and_save_data(lat, long, start, end, cache=cache)

    df = append_x_days_upfront(lat, long, 10, cache=cache)
    # df = load_data(lat, long)
    # df = load_from_file_or_download(lat, long, start, end, cache=cache)

    # Plot
    # print(tabulate(df, headers='keys', tablefmt='psql'))
    df.plot(subplots=True, grid=True)
    plt.show()