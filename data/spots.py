import pandas as pd
import numpy as np
from copy import deepcopy, copy
import datetime
import re
import pickle
from dataclasses import dataclass
from matplotlib import pyplot as plt
from pathlib import Path

import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

import boeien, surffeedback, stormglass
from rijkswaterstaat import Boei

def _compute_onshore(data: pd.DataFrame, richting: float) -> pd.DataFrame:
    data = (data - richting + 90 + 360) % 360
    data = np.sin(data.values / 360 * 2 * np.pi)
    return copy(data)

def _dir_to_onshore(data: pd.DataFrame, richting: float) -> pd.DataFrame:
    data['waveOnshore'] = _compute_onshore(data['waveDirection'], richting)
    data = data.drop('waveDirection', axis=1)

    data['windOnshore'] =  _compute_onshore(data['windDirection'], richting)
    data = data.drop('windDirection', axis=1)
    return data

@dataclass
class Spot:
    """
        All spot info and data in one class

    :param boei: Dichtstbijzijnde boei
    :param richting: Richting van het strand
    :name name: Name in the surf feedback form
    """
    boei: Boei
    richting: float
    name: str

    def feedback(self, only_spot_data):
        """Surf feedback form"""
        if not surffeedback.file_pkl.is_file():
            surffeedback.convert_csv_to_pickle()

        all = pd.read_pickle(surffeedback.file_pkl)
        if only_spot_data:
            return all.query(f"'{self.name}' in spot")
        else:
            return all

    def _hindcast_input(self):
        """Surf historical statistics"""
        data = stormglass.load_data(self.boei.N, self.boei.E)
        data = _dir_to_onshore(data, self.richting)
        return data


    def hindcast(self, only_spot_data, non_zero_only=True, match_all_feedback_times=True):
        """Combined surf statistics and feedback form"""
        columns = "rating"
        input = self._hindcast_input()
        output = self.feedback(only_spot_data=only_spot_data)
        data = deepcopy(input)
        data[columns] = np.nan

        for index, row in output.iterrows():
            pattern = r'^\d{2}:\d{2}:\d{2}$'
            datum = row["Datum"]
            date_wrong_format = not re.match(pattern, str(row['Start tijd'])) or not re.match(pattern,
                                                                                              str(row['Start tijd']))
            if date_wrong_format:
                continue
            start_tijd = datetime.datetime.strptime(f"{datum} {row['Start tijd']}", "%d-%m-%Y %H:%M:%S")
            eind_tijd = datetime.datetime.strptime(f"{datum} {row['Eind tijd']}", "%d-%m-%Y %H:%M:%S")
            if not match_all_feedback_times:
                mid_tijd = start_tijd + ((eind_tijd - start_tijd) / 2)
                start_tijd = mid_tijd - datetime.timedelta(minutes=5)
                eind_tijd = mid_tijd + datetime.timedelta(minutes=5)
            start_tijd = start_tijd.strftime("%Y-%m-%d %H:%M:%S")
            eind_tijd = eind_tijd.strftime("%Y-%m-%d %H:%M:%S")
            query = (data.index >= start_tijd) & (data.index <= eind_tijd)
            # if all(query == False):
            #     continue
            data.loc[query, columns] = row[columns]
        if non_zero_only:
            return data[data["rating"].notnull()]
        else:
            return data

    def forecast(self, hours=48):
        data = stormglass.forecast(self.boei.N, self.boei.E, hours=hours, cache=False)  # check: is N == lat?
        data = _dir_to_onshore(data, self.richting)
        return data

    def train(self, verbose=True, save=True, only_spot_data=True, match_all_feedback_times=True) -> pd.DataFrame:
        """Train a model, save it and returns the model"""
        df = self.hindcast(only_spot_data=only_spot_data, match_all_feedback_times=match_all_feedback_times)

        X = df.drop('rating', axis=1)
        y = df['rating']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        model = xgb.XGBRegressor(objective='reg:squarederror')
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        if save:
            model_file = f"model_XGBRegressor_{self.name}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)

        if verbose:
            print('Mean Squared Error:', mse)
            for i in range(len(y_test)):
                print('real:', y_test[i], 'pred:', y_pred[i])
        return model

    def predict_surf_rating(self) -> pd.DataFrame:
        """Rate the surf forecast based on the trained model (file)"""

        # Load model
        model_file = Path(f"model_XGBRegressor_{self.name}.pkl")
        if not model_file.is_file():
            raise NotImplementedError("Use .train() first to train a model")
        with open(model_file, 'rb') as f:
            model = pickle.load(f)

        # Load data
        data = self.forecast()
        data["rating"] = model.predict(data)

        return data

    def plot_surf_rating(self):
        channels_simple = ['waveHeight', 'wavePeriod', 'windSpeed', 'windOnshore', 'rating']
        data = self.predict_surf_rating()
        data.plot(subplots=True, grid=True)
        plt.suptitle(self.name)


# Add all spots here
ijmuiden = Spot(boei=boeien.ijmuiden, richting=290, name="ZV")


if __name__ == '__main__':
    # ijmuiden.train(only_spot_data=False, match_all_feedback_times=True)
    ijmuiden.plot_surf_rating()
    plt.show()