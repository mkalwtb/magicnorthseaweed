from dataclasses import dataclass
import pandas as pd
from typing import List
import time
import os

import ssl
import urllib.request

# data urls: https://docs.google.com/spreadsheets/d/1lLeKB43NvH5RlZwttCvSsepe5EiucqqTCpcbK5AbbG4/edit#gid=0
ssl._create_default_https_context = ssl._create_unverified_context
date_time_str = "%Y%m%d-%H%M%S"
timestr = time.strftime(date_time_str)




def read_data(file: str) -> pd.DataFrame:
    return pd.read_csv(file, sep=";", parse_dates={"Datetime": [0, 1]}, dayfirst=True, index_col="Datetime")


def locate_waarde(old: pd.DataFrame, data_name: str) -> pd.DataFrame:
    waarde = old["Waarde"].loc[old["Waarde"].notna()]
    both = pd.concat([waarde])
    new = pd.DataFrame(both)
    new.columns = [data_name]
    return new

@dataclass
class BoeiData:
    name: str
    col_past: str
    col_future: str
    parameter: str
    locoation_slug: str
    time_horizon: str

    @property
    def url(self):
        return f"https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter={self.parameter}&locationSlug={self.locoation_slug}&timehorizon={self.time_horizon}"

    def download_file(self, file_name):
        urllib.request.urlretrieve(self.url, file_name)

    def download_df(self) -> pd.DataFrame:
        file_name = f"{self.name}_{timestr}.csv"
        self.download_file(file_name)
        raw = read_data(file_name)
        data = locate_waarde(raw, data_name=self.name)
        os.remove(file_name)
        return data

@dataclass
class Boei:
    data: List[BoeiData]
    locationSlug: str

    def download(self):
        results = pd.DataFrame()
        for boei_data in self.data:
            result = boei_data.download_df()
            results = pd.concat([results, result], axis=1)
        return results
