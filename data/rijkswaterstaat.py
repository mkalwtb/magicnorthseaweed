import pandas as pd
from pathlib import Path
import time
import os
from tabulate import tabulate
from matplotlib import pyplot as plt

import ssl
import urllib.request

# data urls: https://docs.google.com/spreadsheets/d/1lLeKB43NvH5RlZwttCvSsepe5EiucqqTCpcbK5AbbG4/edit#gid=0
urls = {"Hs": r"https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Significante___20golfhoogte___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20cm&locationSlug=IJgeul(IJGL)&timehorizon=-48,48",
        "Tp": r"https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Significante___20golfhoogte___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20cm&locationSlug=IJgeul(IJGL)&timehorizon=-48,48",
        # "v0": r"https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs&locationSlug=IJmuiden-Buitenhaven(IJMH)&timehorizon=-48,48"
        }
ssl._create_default_https_context = ssl._create_unverified_context
date_time_str = "%Y%m%d-%H%M%S"
timestr = time.strftime(date_time_str)


def read_data(file: str) -> pd.DataFrame:
    return pd.read_csv(file, sep=";", parse_dates={"Datetime": [0, 1]}, dayfirst=True, index_col="Datetime")


def strip_data(old: pd.DataFrame, data_name: str) -> pd.DataFrame:
    waarde = old["Waarde"].loc[old["Waarde"].notna()]
    verwachting = old["Verwachting"].loc[old["Verwachting"].notna()]
    both = pd.concat([waarde, verwachting])
    new = pd.DataFrame(both, columns=[data_name])
    return new


def download_file(url: str, file_name):
    urllib.request.urlretrieve(url, file_name)


def download_df(url: str, data_name) -> pd.DataFrame:
    file_name = f"{data_name}_{timestr}.csv"
    download_file(url, file_name)
    raw = read_data(file_name)
    data = strip_data(raw, data_name=data_name)
    os.remove(file_name)
    return data


def download_wave_data():
    results = pd.DataFrame()
    for name, url in urls.items():
        result = download_df(url, data_name=name)
        print(result)
        results = pd.concat([results, result], axis=1)
    return results

if __name__ == '__main__':
    df = download_wave_data()
    print(df)
    print(tabulate(df, headers=df.columns))
    df.plot(subplots=True)
    plt.show()
