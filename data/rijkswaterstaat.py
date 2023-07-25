from dataclasses import dataclass
from matplotlib import pyplot as plt
import pandas as pd
from typing import List
import time
import os
import warnings
from pathlib import Path
import math

import ssl
from urllib import request, error

# data urls: https://docs.google.com/spreadsheets/d/1lLeKB43NvH5RlZwttCvSsepe5EiucqqTCpcbK5AbbG4/edit#gid=0
ssl._create_default_https_context = ssl._create_unverified_context
date_time_str = "%Y%m%d-%H%M%S"
timestr = time.strftime(date_time_str)
SCRAPE_FOLDER = Path("temp_scrape_data")
DATA_FOLDER = Path("boei-data")


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
    location_slug: str
    col_past: str = "Waarde"
    col_future: str = ""
    future_unavailable: bool = False  # if scraping future is not possible

    def url(self, time_horizon: str):
        return f"https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter={self.parameter}&locationSlug={self.location_slug}&timehorizon={time_horizon}"

    def _download_file(self, file_name: str, time_horizon: str):
        request.urlretrieve(self.url(time_horizon), file_name)

    def _download_raw(self, time_horizon: str) -> pd.DataFrame:
        file_name = SCRAPE_FOLDER / f"{self.location_slug}_{self.name}_{timestr}.csv"
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


class Boei:
    def __init__(self, parameters: List[BoeiData], location_slug: str, N: float, E: float):
        self.parameters: List[BoeiData] = parameters
        self.location_slug: str = location_slug
        self._db_file_ = DATA_FOLDER / (self.location_slug + ".pkl")
        self.data: pd.DataFrame = self._load_data()
        self.N: float = N
        self.E: float = E

    def download(self, time_horizon: str, past, future) -> pd.DataFrame:
        """Download new buoy data"""
        results = pd.DataFrame()
        for parameter in self.parameters:
            try:
                result = parameter.download(time_horizon, past, future)
                results = pd.concat([results, result], axis=1)
            except error.HTTPError as e:
                warnings.warn(f"Could receive '{parameter.name}' for '{parameter.location_slug}': {e}'")
            except IOError as e:
                warnings.warn(f"Could receive '{parameter.name}' for '{parameter.location_slug}': {e}'")
        return results

    def _load_data(self):
        """Load buoy data file"""
        if self._db_file_.is_file():
            return pd.read_pickle(self._db_file_)
        return pd.DataFrame()

    def save_data(self):
        """Save the data to the buoys dataframe"""
        self.data.to_pickle(self._db_file_)

    def append_data(self, new: pd.DataFrame, overwrite_existing=True):
        """Append a new buoy dataframe to the existing buoy data"""
        if overwrite_existing:
            existing = self.data.drop(self.data.index.intersection(new.index))
        else:
            existing = self.data
            new = new.drop(new.index.intersection(self.data.index))
        n_lines_scraped = len(new)
        n_lines_overwritten = len(self.data.index.intersection(new.index))
        n_lines_new = n_lines_scraped - n_lines_overwritten
        self.data = pd.concat([existing, new], axis=0)
        return n_lines_new

    def scrape(self, time_str: str = "-48,48") -> pd.DataFrame:
        """Download new data and save in the db"""
        df_new = self.download(time_str, future=False, past=True)
        new_lines = self.append_data(df_new)
        self.save_data()
        print(f"Added {new_lines} new lines to {self.location_slug}).")
        return df_new

    def plot(self):
        self.data.plot(subplots=True, grid=True)
        plt.suptitle(self.location_slug)

    def angle_to(self, other_buoy):
        # Convert latitude and longitude to radians
        lat1_rad = math.radians(self.E)
        lon1_rad = math.radians(self.N)
        lat2_rad = math.radians(other_buoy.E)
        lon2_rad = math.radians(other_buoy.N)

        # Calculate the differences between the longitudes and latitudes
        delta_lon = lon2_rad - lon1_rad
        delta_lat = lat2_rad - lat1_rad

        # Calculate the angle using the Haversine formula
        y = math.sin(delta_lon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
        angle_rad = math.atan2(y, x)

        # Convert the angle to degrees
        angle_deg = math.degrees(angle_rad)

        # Normalize the angle between 0 and 360 degrees
        angle_normalized = (angle_deg + 360) % 360

        return angle_normalized


