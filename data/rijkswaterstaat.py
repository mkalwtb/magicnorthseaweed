from dataclasses import dataclass
import pandas as pd
from typing import List
import time
import os

import ssl
from urllib import request, error

# data urls: https://docs.google.com/spreadsheets/d/1lLeKB43NvH5RlZwttCvSsepe5EiucqqTCpcbK5AbbG4/edit#gid=0
ssl._create_default_https_context = ssl._create_unverified_context
date_time_str = "%Y%m%d-%H%M%S"
timestr = time.strftime(date_time_str)


def _read_rijkswaterstaat_csv(file: str, skip_rows: int = 0) -> pd.DataFrame:
    return pd.read_csv(file, sep=";", parse_dates={"Datetime": [0, 1]}, dayfirst=True, index_col="Datetime", skiprows=skip_rows)


def _locate_waarde(old: pd.DataFrame, data_name: str, value_col: str) -> pd.DataFrame:
    if not value_col in old.columns:
        raise NotImplementedError("Column")
    value = old[value_col].loc[old[value_col].notna()]
    both = pd.concat([value])
    new = pd.DataFrame(both)
    new.columns = [data_name]
    return new

@dataclass
class BoeiData:
    """
    Om de boei data op te zoeken:
    1. Ga naar https://waterinfo.rws.nl/#!/details/publiek/waterhoogte/
    2. Selecteer de boei & data die je wil
    3. click Export/Delen
    4. Right click op CSV
    5. copy link adress
    6. Extract de parameter=... en location_slug=... en time_horizon=...
    7. Indien nodig, open de csv file en kijk hoe de colom heet. Normaal is dit Waarde
    """
    name: str
    parameter: str
    locoation_slug: str
    time_horizon: str
    col_past: str = "Waarde"
    col_future: str = "verwachting"

    @property
    def url(self):
        return f"https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter={self.parameter}&locationSlug={self.locoation_slug}&timehorizon={self.time_horizon}"

    def _download_file(self, file_name):
        try:
            request.urlretrieve(self.url, file_name)
        except error.HTTPError as e:
            print(f"Could not read '{file_name}'")
            print(self.url)
            raise e

    def download(self) -> pd.DataFrame:
        file_name = f"{self.name}_{timestr}.csv"
        self._download_file(file_name)
        data_csv = _read_rijkswaterstaat_csv(file_name)
        data_clean = _locate_waarde(data_csv, data_name=self.name, value_col=self.col_past)
        os.remove(file_name)
        return data_clean

@dataclass
class Boei:
    data: List[BoeiData]
    locationSlug: str

    def download(self):
        results = pd.DataFrame()
        for boei_data in self.data:
            result = boei_data.download()
            results = pd.concat([results, result], axis=1)
        return results
