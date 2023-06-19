import pandas as pd
from pathlib import Path
import time
import os
from tabulate import tabulate
from functools import cache
from matplotlib import pyplot as plt
import boeien

import ssl
import urllib.request

# data urls: https://docs.google.com/spreadsheets/d/1lLeKB43NvH5RlZwttCvSsepe5EiucqqTCpcbK5AbbG4/edit#gid=0
ssl._create_default_https_context = ssl._create_unverified_context
date_time_str = "%Y%m%d-%H%M%S"
timestr = time.strftime(date_time_str)



def read_data(file: str) -> pd.DataFrame:
    return pd.read_csv(file, sep=";", parse_dates={"Datetime": [0, 1]}, dayfirst=True, index_col="Datetime")


def locate_waarde(old: pd.DataFrame, data_name: str, add_future = False) -> pd.DataFrame:
    waarde = old["Waarde"].loc[old["Waarde"].notna()]
    if add_future:
        verwachting = old["Verwachting"].loc[old["Verwachting"].notna()]
        both = pd.concat([waarde, verwachting])
        new = pd.DataFrame(both, columns=[data_name])
    else:
        both = pd.concat([waarde])
        new = pd.DataFrame(both)
        new.columns = [data_name]
    return new



def download_file(url: str, file_name):
    urllib.request.urlretrieve(url, file_name)


# @cache
def download_df(boei_data: boeien.BoeiData) -> pd.DataFrame:
    file_name = f"{boei_data.name}_{timestr}.csv"
    download_file(boei_data.url, file_name)
    raw = read_data(file_name)
    data = locate_waarde(raw, data_name=boei_data.name)
    os.remove(file_name)
    return data


def download_wave_data(boei: boeien.Boei):
    results = pd.DataFrame()
    for boei_data in boei.data:
        result = download_df(boei_data)
        results = pd.concat([results, result], axis=1)
    return results

if __name__ == '__main__':
    df = download_wave_data(boeien.ijmuiden)
    print(df)
    # print(tabulate(df, headers=df.columns))
    df.plot(subplots=True)
    plt.show()
