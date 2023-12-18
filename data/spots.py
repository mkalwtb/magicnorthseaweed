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
from tabulate import tabulate
from plotting import plot_forecast

import boeien, surffeedback, stormglass
from rijkswaterstaat import Boei

forecast_columns = ["rating", "hoog", "clean", "krachtig", "stijl", "stroming", "windy"]

def _compute_onshore(data: pd.DataFrame, richting: float, side_shore) -> pd.DataFrame:
    if side_shore:
        data = (data - richting + 360) % 360
    else:
        data = (data - richting + 90 + 360) % 360
    data = np.sin(data.values / 360 * 2 * np.pi)
    return copy(data)

def _enrich_input_data(data: pd.DataFrame, richting: float) -> pd.DataFrame:
    data['waveOnshore'] = _compute_onshore(data['waveDirection'], richting, side_shore=False)
    data['waveSideshore'] = _compute_onshore(data['waveDirection'], richting, side_shore=True)
    data = data.drop('waveDirection', axis=1)

    data['windOnshore'] = _compute_onshore(data['windDirection'], richting, side_shore=False)
    data['windSideshore'] = _compute_onshore(data['windDirection'], richting, side_shore=True)
    data = data.drop('windDirection', axis=1)

    data['seaRise'] = data["NAP"].diff()

    return data

class Model:
    def __init__(self, perk: str, model=None):
        self.perk = perk
        self.model: xgb.XGBModel = model if model is not None else self._load_model()

    @classmethod
    def train(cls, spot, channel, verbose=False, save=True, only_spot_data=True, match_all_feedback_times=True):
        """Train a model, save it and returns the model"""
        df = spot.combined(only_spot_data=only_spot_data, match_all_feedback_times=match_all_feedback_times,
                           fb_columns=channel)
        # TODO add loop, this line for each spot

        X = df.drop(channel, axis=1)
        y = df[channel]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        model = xgb.XGBRegressor(objective='reg:squarederror')
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)

        print(f'Mean Squared Error: {mse:.2f} (from {len(df)} feedback entries)')
        if verbose:
            for i in range(len(y_test)):
                print('real:', y_test[i], 'pred:', y_pred[i])
        obj = cls(perk=channel, model=model)
        if save:
            obj.save_model()
        return obj

    def _load_model(self):
        if not self.model_file.is_file():
            raise NotImplementedError("Use .train() first to train a model")
        with open(self.model_file, 'rb') as f:
            model = pickle.load(f)
        return model

    def save_model(self):
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.model, f)

    @property
    def model_file(self):
        return Path(f"AI-models/model_XGBRegressor_ZV_{self.perk}.pkl")  # todo remove ZV


MODELS = [Model(perk) for perk in forecast_columns]


@dataclass
class Spot:
    """
        All spot info and data in one class

    :param boei: Dichtstbijzijnde boei
    :param richting: Richting van het strand
    :name name: Name in the surf feedback form
    """
    # boei: Boei
    richting: float
    name: str
    lat: float
    long: float

    def feedback(self, only_spot_data):
        """Surf feedback form"""

        all = surffeedback.load(surffeedback.file_raw)
        if only_spot_data:
            return all[all["spot"].str.contains(self.name)==True]
        else:
            return all

    def _hindcast_input(self):
        """Surf historical statistics"""
        data = stormglass.load_data(self.lat, self.long)
        data = _enrich_input_data(data, self.richting)
        return data

    def combined(self, only_spot_data, non_zero_only=True, match_all_feedback_times=True, fb_columns: str=None):
        """Combined surf statistics and feedback form"""
        input = self._hindcast_input()
        output = self.feedback(only_spot_data=only_spot_data)
        data = deepcopy(input)
        if not fb_columns:
            fb_columns = output.forecast_columns
        data[fb_columns] = np.nan

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
            data.loc[query, fb_columns] = row[fb_columns]
        if non_zero_only:
            return data[data[fb_columns].notnull()]
        else:
            return data

    def forecast(self, cache, hours=72, ):
        data = stormglass.forecast(self.lat, self.long, hours=hours, cache=cache)  # check: is N == lat?
        return data

    def predict_surf_perk(self, data, model: Model) -> pd.DataFrame:
        """Rate the surf forecast based on the trained model (file)"""

        data = _enrich_input_data(data, self.richting)
        result = model.model.predict(data)
        return result

    def surf_rating(self, models=MODELS, cache=False):
        data_init = self.forecast(cache)
        data = deepcopy(data_init)
        for model in models:
            data[model.perk] = self.predict_surf_perk(data_init, model)
        return data


# Add all spots here
ijmuiden = Spot(richting=290, name="ZV", lat=52.474773, long=4.535204)
scheveningen = Spot(richting=315, name="schev", lat=52.108703, long=4.267715)
camperduin = Spot(richting=270, name="camperduin", lat=52.723113, long=4.639215)
texel_paal17 = Spot(richting=305, name="texel17", lat=53.081695, long=4.733450)

spots = [ijmuiden, scheveningen, camperduin, texel_paal17]

if __name__ == '__main__':


    # Train models
    for model in MODELS:
        model.train(ijmuiden, channel=model.perk, only_spot_data=True, save=False)


    # Perks
    df = ijmuiden.surf_rating(cache=True)
    plot_forecast(df, ijmuiden, perks_plot=True)
    plot_forecast(df, ijmuiden)
    plt.show()



    # print(tabulate(df, df.columns))
    # mse = ijmuiden.train(only_spot_data=False, save=True)
    # model = ijmuiden.load_model()
    # xgb.plot_tree(model)
    # Plot tree
    # xgb.plot_tree(model)


    # print(tabulate(ijmuiden.feedback(only_spot_data=True), headers='keys', tablefmt='psql'))
    # data = ijmuiden.surf_rating(cache=True)
    # plot_forecast(data, ijmuiden)
    # plt.show()