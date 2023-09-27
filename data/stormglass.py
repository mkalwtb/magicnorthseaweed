from pathlib import Path
import pandas as pd
import numpy as np
import arrow
import requests
import json
from tabulate import tabulate
from matplotlib import pyplot as plt


# Get first hour of today
def download_json(lat, long, moment=None, back=48, forward=48, cache=False):
  if moment is None:
    moment = arrow.now('Europe/Amsterdam')  # todo fix timezone?
  end = moment .shift(hours=forward)
  start = moment .shift(hours=-back)
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
        'params': ','.join(['waveDirection', 'windDirection', 'wavePeriod', "waveHeight", "windSpeed"]),
        'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
        'end': end.to('UTC').timestamp()  # Convert to UTC timestamp
      },
      headers={
        'Authorization': '1feeb6a8-5bc9-11ee-a26f-0242ac130002-1feeb702-5bc9-11ee-a26f-0242ac130002'
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
          'windDirection_icon': entry['windDirection']['sg'],
          # 'windDirection_noaa': entry['windDirection']['noaa'],
          # 'windDirection_sg': entry['windDirection']['sg'],
          # 'windDirection_smhi': entry['windDirection']['smhi'],
          # 'waveDirection_dwd': entry['waveDirection']['fcoo'],
          # 'waveDirection_icon': entry['waveDirection']['icon'],
          # 'waveDirection_meteo': entry['waveDirection']['meteo'],
          'waveDirection': entry['waveDirection']['sg'],
          "wavePeriod": entry["wavePeriod"]["sg"],
          "waveHeight": entry["waveHeight"]["sg"],
          "windSpeed": entry["windSpeed"]["sg"],
      }
      hourly_data.append(row)

  # Create a Pandas DataFrame
  df = pd.DataFrame(hourly_data)

  # Convert the 'time' column to a proper datetime format
  df.index = pd.to_datetime(df['time'])
  return df

if __name__ == '__main__':
    df_all = pd.read_pickle("data.pkl")

    oldest = arrow.get(min(df_all["time"]))
    range = 10
    days = np.arange(start=-1000, stop=0, step=range).tolist()
    add_new_data = False

    if add_new_data:
        for day in days:
            print(day)
            moment = oldest.shift(days=day)
            json_data = download_json(lat=52.464295, long=4.532720, moment=moment, back=range*24, forward=0, cache=False)
            df = json_to_df(json_data)
            if not df_all is None and len(df_all) > 0:
                df_all = pd.concat([df_all, df], axis=0, ignore_index=True)
            else:
                df_all = df
            print(tabulate(df, headers='keys', tablefmt='psql'))
        df_all.to_pickle("data.pkl")

    columns = ["waveHeight", "wavePeriod", "windSpeed"]
    print(tabulate(df_all, headers='keys', tablefmt='psql'))
    fig, axs = plt.subplots(len(columns),1)
    for ax, column in zip(axs, columns):
        ax.plot(df_all.index, df_all[column])
        # plt.plot(df_all["time"], df_all['waveHeight'])
        # plt.grid()
    plt.show()