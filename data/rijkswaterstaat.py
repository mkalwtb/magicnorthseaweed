from dataclasses import dataclass
import pandas as pd
from typing import List
import time
import os
import warnings
from pathlib import Path

import ssl
from urllib import request, error

# data urls: https://docs.google.com/spreadsheets/d/1lLeKB43NvH5RlZwttCvSsepe5EiucqqTCpcbK5AbbG4/edit#gid=0
ssl._create_default_https_context = ssl._create_unverified_context
date_time_str = "%Y%m%d-%H%M%S"
timestr = time.strftime(date_time_str)
SCRAPE_FOLDER = Path("temp_scrape_data")


def _read_rijkswaterstaat_csv(file: str, skip_rows: int = 0) -> pd.DataFrame:
    return pd.read_csv(file, sep=";", parse_dates={"Datetime": [0, 1]}, dayfirst=True, index_col="Datetime", skiprows=skip_rows)


def _locate_waarde(old: pd.DataFrame, data_name: str, value_col: str) -> pd.DataFrame:
    if not value_col in old.columns:
        raise IOError(f"Column '{value_col}' is not found.")
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
    col_past: str = "Waarde"
    col_future: str = ""
    future_unavailable: bool = False  # if screaping future is not possible

    def url(self, time_horizon: str):
        return f"https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter={self.parameter}&locationSlug={self.locoation_slug}&timehorizon={time_horizon}"

    def _download_file(self, file_name: str, time_horizon: str):
        request.urlretrieve(self.url(time_horizon), file_name)

    def _download_raw(self, time_horizon: str) -> pd.DataFrame:
        file_name = SCRAPE_FOLDER / f"{self.locoation_slug}_{self.name}_{timestr}.csv"
        self._download_file(file_name, time_horizon)
        data_csv = _read_rijkswaterstaat_csv(file_name)
        os.remove(file_name)
        return data_csv

    def _combine_past_future(self, data_csv: pd.DataFrame, past: bool, future) -> pd.DataFrame:
        data_past = pd.DataFrame()
        data_future = pd.DataFrame()
        if past:
            data_past = _locate_waarde(data_csv, data_name=self.name, value_col=self.col_past)
        if future and self.col_future:
            data_future = _locate_waarde(data_csv, data_name=self.name, value_col=self.col_future)
        data_clean = pd.concat([data_past, data_future])

        return data_clean

    def _remove_future(self, time_horizon):
        times = time_horizon.split(",")
        if self.future_unavailable and float(times[1]) > 0:
            time_horizon = f"{times[0]},0"
            print(f"Updated to 'time_horizon={time_horizon}' because future times are unavailable")
        return time_horizon

    def download(self, time_horizon: str, past: bool, future: bool = False) -> pd.DataFrame:
        time_horizon_available = self._remove_future(time_horizon)
        data_csv = self._download_raw(time_horizon=time_horizon_available)
        data_clean = self._combine_past_future(data_csv, past=past, future=future)
        return data_clean


@dataclass
class Boei:
    data: List[BoeiData]
    locationSlug: str

    def download(self, time_horizon: str, past, future):
        results = pd.DataFrame()
        for boei_data in self.data:
            try:
                result = boei_data.download(time_horizon, past, future)
                results = pd.concat([results, result], axis=1)
            except error.HTTPError as e:
                warnings.warn(f"Could receive '{boei_data.name}' for '{boei_data.locoation_slug}': {e}'")
            except IOError as e:
                warnings.warn(f"Could receive '{boei_data.name}' for '{boei_data.locoation_slug}': {e}'")
        return results
