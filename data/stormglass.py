from pathlib import Path
import pandas as pd
import arrow
import requests
import json

# Get first hour of today
def download_json(lat, long, hours=48, cache=False):
  start = arrow.now('Europe/Amsterdam')  # todo fix timezone?
  end = start .shift(hours=hours)
  cache_file = Path('response.json')

  if cache_file.is_file() and cache:
    print("Cached")
    with open(cache_file, 'r') as f:
      json_data = json.load(f)
  else:
    print("Scraping")
    response = requests.get(
      'https://api.stormglass.io/v2/weather/point',
      params={
        'lat': lat,
        'lng': long,
        'params': ','.join(['waveDirection', 'windDirection']),
        'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
        'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
      },
      headers={
        'Authorization': '5bf98f1a-2979-11ee-8d52-0242ac130002-5bf98f88-2979-11ee-8d52-0242ac130002'
      }
    )

    json_data = response.json()
    with open(cache_file, 'w') as f:
      json.dump(json_data, f)  # dumps response from API in response.json (cache_file)

  return json_data

def json_to_df(json_data):
  # To json
  # Extract the relevant data from the 'hours' list
  hourly_data = []
  for entry in json_data['hours']:
      row = {
          'time': entry['time'],
          'windDirection_icon': entry['windDirection']['icon'],
          'windDirection_noaa': entry['windDirection']['noaa'],
          'windDirection_sg': entry['windDirection']['sg'],
          # 'windDirection_smhi': entry['windDirection']['smhi'],
          # 'waveDirection_dwd': entry['waveDirection']['fcoo'],
          'waveDirection_icon': entry['waveDirection']['icon'],
          # 'waveDirection_meteo': entry['waveDirection']['meteo'],
          'waveDirection_noaa': entry['waveDirection']['noaa'],
          'waveDirection_sg': entry['waveDirection']['sg'],
      }
      hourly_data.append(row)

  # Create a Pandas DataFrame
  df = pd.DataFrame(hourly_data)

  # Convert the 'time' column to a proper datetime format
  df.index = pd.to_datetime(df['time'])
  return df

if __name__ == '__main__':
  json_data = download_json(lat=53.586792, long=3.075473, cache=True)
  df = json_to_df(json_data)
  print(df[['windDirection_icon', 'waveDirection_icon']])