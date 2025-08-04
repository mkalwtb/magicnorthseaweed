import pickle
from pathlib import Path
from typing import List

import pandas as pd
import xgboost as xgb
from cleanlab.regression.learn import CleanLearning
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from data.plotting import plot_forecast
from data.spots import ZV
from data.spots import SPOTS


class Model:
    def __init__(self, perk: str, channels, model=None):
        self.perk = perk
        self.model: xgb.XGBModel = model if model is not None else self._load_model()
        self.channels = channels

    def train(self, spots, perk: str, channels: List[str], verbose=False, save=True, match_all_feedback_times=True):
        """Train a model, save it and returns the model"""
        dfs = pd.DataFrame()
        for spot in spots:
            df = spot.combined(only_spot_data=True, match_all_feedback_times=match_all_feedback_times,
                               fb_columns=perk)
            dfs = pd.concat([df, dfs])

        dfs = dfs[channels + [perk]]
        X = dfs.drop(perk, axis=1)
        y = dfs[perk]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        self.model = xgb.XGBRegressor(objective='reg:squarederror', max_depth=3)
        self.model.fit(X_train, y_train)

        y_pred_test = self.model.predict(X_test)
        y_pred_train = self.model.predict(X_train)

        mse_train = mean_squared_error(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)


        if verbose:
            print(f'RMS {perk}: train={mse_train:.2f}, test={mse_test:.2f} (from {len(dfs)} feedback entries)')
        if save:
            self.save_model()
        return mse_test


    @classmethod
    def train_new(cls, spots, perk: str, channels: List[str], verbose=False, save=True, match_all_feedback_times=True):
        # double with train. Temp.
        dfs = pd.DataFrame()
        for spot in spots:
            df = spot.combined(only_spot_data=True, match_all_feedback_times=match_all_feedback_times,
                               fb_columns=perk)
            dfs = pd.concat([df, dfs])

        dfs = dfs[channels + [perk]]
        X = dfs.drop(perk, axis=1)
        y = dfs[perk]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        model = xgb.XGBRegressor(objective='reg:squarederror', max_depth=3)
        model.fit(X_train, y_train)
        return cls(perk, channels, model=model)


    def train_best(self, spots, perk: str, channels: List[str], verbose=True, save=True, match_all_feedback_times=True, attempts=10):
        model_best = None
        rms_best = 9999
        for i in range(attempts):
            rms = self.train(spots, perk=perk, channels=channels, save=False, verbose=True, match_all_feedback_times=match_all_feedback_times)
            model = self.model
            if rms < rms_best:
                rms_best = rms
                model_best = model
                if save:
                    self.save_model()
                if verbose:
                    print(f"new best model: {perk}:\t{rms:.2f}")
        self.model = model_best

    def clean_model(self):
        self.model = CleanLearning(self.model)

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

    def plot_model(self):
        xgb.plot_tree(self.model)
        plt.show()

input_columns = ['wavePeriod', 'waveHeight', 'windSpeed', 'windWaveHeight',
       'currentSpeed', 'NAP', 'waveOnshore', 'waveSideshore', 'windOnshore',
       'windSideshore', 'seaRise', 'pier']

# forecast_columns = ["rating", "hoog", "clean", "krachtig", "stijl", "stroming", "windy"]
forecast_columns = {
    "rating": ['waveEnergy', 'wavePeriod', 'windWaveHeight2', 'NAP', 'windMagOnShore', 'shelterWind', 'seaRise'],
    "hoog": ['waveEnergy', 'wavePeriod', 'seaRise'],
    "hoogte-v2": ['waveEnergy', 'wavePeriod', 'seaRise'],
    "clean": ['windMagOnShore', 'waveEnergy', 'windWaveHeight2', 'shelterWind'],
    "krachtig": ['waveEnergy', 'NAP', 'seaRise'],
    "stijl": ['waveEnergy', 'wavePeriod', 'NAP', 'windMagOnShore', 'shelterWind'],
    "stroming": ['currentSpeed', 'seaRise', 'windMagOnShore'],
    "windy": ['windMagOnShore', 'windSpeed', 'shelterWind'],
}

hoog2_forecase_cols = ['waveEnergy', 'waveHeight', 'wavePeriod', 'seaRise']

MODELS = []
for perk, in_columns in forecast_columns.items():
    model = Model(perk, channels=in_columns)
    MODELS.append(model)

# if __name__ == "__main__":
#     model = MODELS[2]
#     xgb.plot_tree(model.model, num_trees=3)
#     fig = plt.gcf()
#     fig.set_size_inches(150, 100)
#     plt.show()


if __name__ == '__main__':
    # Train models
    attenpts = 20
    rating = MODELS[0]
    # rating.train_best(spots, perk=rating.perk, channels=rating.channels, save=True, verbose=True, attempts=attenpts)
    for model in MODELS:
        model.train_best(SPOTS, perk=model.perk, channels=model.channels, save=True, attempts=attenpts)


    spot = ZV
    df = spot.surf_rating(cache=True)
    plot_forecast(df, spot, perks_plot=True)

    # df = ZV.surf_rating(cache=True)
    # plot_forecast(df, ZV, perks_plot=True)
    #
    # df = ijmuiden.surf_rating(cache=True)
    # plot_forecast(df, ijmuiden, perks_plot=True)
    plt.show()

    rating.plot_model()



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