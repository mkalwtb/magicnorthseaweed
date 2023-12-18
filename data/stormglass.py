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
from random import randrange


# todo try new model: using primary & secondary swells
channels = ['waveDirection', 'wavePeriod', "waveHeight", "windSpeed", 'windDirection', "windWaveHeight", "currentSpeed"]  # "currentSpeed"  # todo add seaLevel
channels_training = ['waveOnshore', 'wavePeriod', "waveHeight", "windSpeed", 'windOnshore', "windWaveHeight", "currentSpeed"]  # "currentSpeed"  # todo add seaLevel

keys = [
    '1feeb6a8-5bc9-11ee-a26f-0242ac130002-1feeb702-5bc9-11ee-a26f-0242ac130002',
    '5bf98f1a-2979-11ee-8d52-0242ac130002-5bf98f88-2979-11ee-8d52-0242ac130002',
    'a5396776-5d64-11ee-8b7f-0242ac130002-a53967da-5d64-11ee-8b7f-0242ac130002',
    '25c9c3a8-5e29-11ee-92e6-0242ac130002-25c9c40c-5e29-11ee-92e6-0242ac130002',
    'e2f68d4e-5eab-11ee-8d52-0242ac130002-e2f68e2a-5eab-11ee-8d52-0242ac130002',
    '9bb1648a-5ee8-11ee-a26f-0242ac130002-9bb164e4-5ee8-11ee-a26f-0242ac130002'
]
N_KEYS = len(keys)



data_sources = {"waveDirection": "icon",
               "wavePeriod": "icon",
               "waveHeight": "icon",
               "windSpeed": "icon",
               "windDirection": "icon",
               "windWaveHeight": "icon",
               "currentSpeed": "sg",
                "seaLevel": "sg"
                }


# Get first hour of today
def download_json(lat, long, start, end, cache=False, end_point="weather"):
  response_type = end_point
  if "/" in response_type:
        response_type = end_point.replace("/", "_")
  cache_file = Path(f'stormglass/stormglass_response_{response_type}_{lat}_{long}.json')

  if cache_file.is_file() and cache:
    print(f"cashing {end_point} from {start} to {end}")
    with open(cache_file, 'r') as f:
      json_data = json.load(f)
  else:
    print(f"Scraping {end_point} from {start} to {end}")
    params = {
        'lat': lat,
        'lng': long,
        'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
        'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
    }
    if end_point == "weather":
        params['params'] = ','.join(channels)

    i_key = randrange(N_KEYS)
    response = requests.get(
      f'https://api.stormglass.io/v2/{end_point}/point',
      params=params,
      headers={
        'Authorization': keys[i_key]
      }
    )


    json_data = response.json()
    if "errors" in json_data:
        raise FileNotFoundError(json_data["errors"]["key"])
    with open(cache_file, 'w') as f:
      json.dump(json_data, f)  # dumps response from API in response.json (cache_file)

  return json_data

def json_to_df(json_data, manual_source=True):
  hourly_data = {}
  if 'hours' not in json_data:
      raise FileNotFoundError('Something went wrong with the stormglass API request')

  for entry in json_data['hours']:
      name = entry['time']
      hourly_data[name] = {}
      for channel in channels:
            source = "sg" if not manual_source else data_sources[channel]
            hourly_data[name][channel] = entry[channel][source]

  # Create a Pandas DataFrame
  df = pd.DataFrame.from_dict(hourly_data, orient='index')
  df.index = pd.to_datetime(df.index)
  df.index = df.index.tz_convert(pytz.timezone('CET')) # todo 1 hour wrong?
  return df


def download_weather(lat, long, start, end, manual_source, cache=False):
    json_data = download_json(lat=lat, long=long, start=start, end=end, cache=cache, end_point="weather")
    data_new = json_to_df(json_data, manual_source=manual_source)
    return data_new


def download_tide(lat, long, start, end, cache=False):
    json_data = download_json(lat=lat, long=long, start=start, end=end, cache=cache, end_point="tide/sea-level")
    if 'data' not in json_data:
        raise FileNotFoundError('Something went wrong with the stormglass API request')
    data_list = json_data["data"]
    df = pd.DataFrame(data_list)
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    df.columns = ["NAP"]
    return df


def download_weather_and_tide(lat, long, start, end, cache=False):
    data_new = download_weather(lat, long, start, end, cache=cache, manual_source=True)
    data_tide = download_tide(lat, long, start, end, cache=cache)
    data_new = pd.concat([data_new, data_tide], axis=1)
    return data_new

def download_and_save_data(name, lat, long, start, end, cache=False):
    data_new = download_weather_and_tide(lat, long, start, end, cache=cache)
    append_historical_data(name, lat, long, data_new)
    return data_new

def load_data(name: str):
    file = Path(f'stormglass/data_{name}.pkl')
    if file.is_file():
        data_db = pd.read_pickle(file)
    else:
        data_db = pd.DataFrame()
    return data_db

def append_historical_data(name, lat, long, data_new):
    """Only function with writing acces"""
    file = Path(f'stormglass/data_{lat}_{long}.pkl')
    now = datetime.now()
    data_db = load_data(name)
    tz = data_new.index.tz
    now_pd = pd.to_datetime(now, utc=tz)
    data_new_historical = data_new[data_new.index <= now_pd]
    data = pd.concat([data_db, data_new_historical], axis=0)
    if len(data_new) > 0:  # save data
        data.to_pickle(file)
    return data_new


def smart_data(name, lat, long, start, end, cache=False):
    data_db = load_data(name)
    start_in_df = arrow.get(data_db.index.min()) <= start
    end_in_df = arrow.get(data_db.index.max()) >= end
    request_is_fully_in_df = start_in_df and end_in_df

    if request_is_fully_in_df:
        print("Data solely from database")
        result = data_db
    else:
        data_new = download_weather_and_tide(lat, long, start, end, cache=cache)
        result = append_historical_data(name, lat, long, data_new)

    #Requested time range of the data
    tz = result.index.tz
    start_pd = pd.to_datetime(start.datetime, utc=tz)
    end_pd = pd.to_datetime(end.datetime, utc=tz)
    result_range = result[(result.index >=start_pd) & (result.index <= end_pd)]
    return result_range


def append_x_days_back(name, lat, long, days: float, cache=False):
    data = load_data(name)
    if len(data) > 0:
        oldest = arrow.get(min(data.index))
    else:
        oldest = arrow.now('Europe/Amsterdam')
    new_oldest = oldest.shift(days=-days)
    return download_and_save_data(lat, long, new_oldest, oldest, cache=cache)

def append_x_days_upfront(name, lat, long, days: float, cache=False):
    data = load_data(name)
    if len(data) > 0:
        oldest = arrow.get(max(data.index))
    else:
        oldest = arrow.now('Europe/Amsterdam')
    new_oldest = oldest.shift(days=days)
    return download_and_save_data(name, lat, long, oldest,new_oldest, cache=cache)


def forecast(lat, long, hours, cache=False):
    now = arrow.now('Europe/Amsterdam')
    start = now.shift(hours=0)
    end = now.shift(hours=hours)
    data_new = download_weather_and_tide(lat, long, start, end, cache=cache)
    return data_new

def keep_scraping_untill_error(name, back=False):
    while True:
        try:
            if back:
                append_x_days_back(name, lat, long, 10, cache=False)
            else:
                append_x_days_upfront(name, lat, long, 10, cache=False)
        except FileNotFoundError as e:
            print(e)
            df = load_data(name)
            break
    return df


if __name__ == '__main__':
    name = "ZV"
    lat = 52.474773
    long = 4.535204
    now = arrow.now('Europe/Amsterdam')
    start = now.shift(hours=-24*9*5)
    end = now.shift(hours=0)
    cache=False

    # df = append_x_days_upfront(lat, long, 10, cache=cache)
    df = keep_scraping_untill_error(name, back=False)
    # df = smart_data(name, lat, long, start, end, cache=cache)

    # df = load_data(lat, long)
    # df = forecast(lat, long, 48, cache=False)
    # df = download_weather_and_tide(lat, long, start, end, cache=cache)

    # Plot
    # print(tabulate(df, headers='keys', tablefmt='psql'))
    df.plot(subplots=True, grid=True)
    plt.show()