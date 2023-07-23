import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime
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


def _dir_to_onshore(data: pd.DataFrame, richting: float) -> pd.DataFrame:
    data['wave-dir'] = (data['wave-dir'] - richting + 360) % 360
    data['onshore-wave'] = np.sin(data['wave-dir'].values / 360 * 2 * np.pi)
    data = data.drop('wave-dir', axis=1)

    data['wind-dir'] = (data['wind-dir'] - richting + 360) % 360
    data['onshore-wind'] = np.sin(data['wind-dir'].values / 360 * 2 * np.pi)
    data = data.drop('wind-dir', axis=1)
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
        all = pd.read_pickle(surffeedback.file_pkl)
        if only_spot_data:
            return all.query(f"spot == '{self.name}'")
        else:
            return all

    def hindcast(self):
        """Surf historical statistics"""
        data = self.boei.data
        data = _dir_to_onshore(data, self.richting)
        return data

    def forecast(self):
        """Surf future statistics"""
        last_future_2_days = "-48,48"
        data = self.boei.download(last_future_2_days, future=True, past=False)
        return data

    def _stormglass(self):
        json_data = stormglass.download_json(self.boei.N, self.boei.E, cache=True)  # todo reset cache
        df_raw = stormglass.json_to_df(json_data)
        df = pd.DataFrame(index=df_raw.index)
        df[['wind-dir', 'wave-dir']] = df_raw[['windDirection_icon', 'waveDirection_icon']]
        df = _dir_to_onshore(df, self.richting)
        df.index = df.index.tz_localize(None)
        return df

    def combine_hindcast_and_feedback(self, only_spot_data, non_zero_only=True  ):
        """Combined surf statistics and feedback form"""
        columns = "rating"
        input = self.hindcast()
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
            start_tijd = datetime.strptime(f"{datum} {row['Start tijd']}", "%d-%m-%Y %H:%M:%S")
            start_tijd = start_tijd.strftime("%Y-%m-%d %H:%M:%S")
            eind_tijd = datetime.strptime(f"{datum} {row['Eind tijd']}", "%d-%m-%Y %H:%M:%S")
            eind_tijd = eind_tijd.strftime("%Y-%m-%d %H:%M:%S")
            query = (data.index >= start_tijd) & (data.index <= eind_tijd)
            # if all(query == False):
            #     continue
            data.loc[query, columns] = row[columns]
        if non_zero_only:
            return data[data["rating"].notnull()]
        else:
            return data

    def combine_forecasts(self):
        forecast = self.forecast()
        stormglass_data = self._stormglass()
        combined = pd.concat([forecast, stormglass_data], axis=1)
        combined.interpolate(inplace=True)
        return combined

    def train(self, verbose=True, save=True) -> pd.DataFrame:
        """Train a model, save it and returns the model"""
        df = self.combine_hindcast_and_feedback(only_spot_data=False)

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

    def rate(self) -> pd.DataFrame:
        """Rate the surf forecast based on the trained model (file)"""

        # Load model
        model_file = Path(f"model_XGBRegressor_{self.name}.pkl")
        print(model_file.is_file())
        with open(model_file, 'rb') as f:
            model = pickle.load(f)

        # Load data
        data = self.combine_forecasts()
        y_pred = model.predict(data)

        return y_pred

    def plot_forecast(self):
        data = self.combine_forecasts()
        data.plot(subplots=True, grid=True)
        plt.suptitle(self.name)



# Add all spots here
ijmuiden = Spot(boei=boeien.ijmuiden, richting=290, name="ZV Parnassia")


if __name__ == '__main__':
    # data = ijmuiden.combine_forecast_and_feedback(only_spot_data=False, non_zero_only=True)
    # print(data)

    ijmuiden.combine_forecasts()
    # ijmuiden.train()
    # ijmuiden.rate()
    # plt.show()