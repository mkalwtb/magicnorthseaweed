import pickle
from pathlib import Path
from typing import List

import pandas as pd
import xgboost as xgb
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


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

        self.model = xgb.XGBRegressor(objective='reg:squarederror')
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)

        print(f'Mean Squared Error {perk}: {mse:.2f} (from {len(dfs)} feedback entries)')
        if verbose:
            for i in range(len(y_test)):
                print('real:', y_test[i], 'pred:', y_pred[i])
        if save:
            self.save_model()

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

input_columns = ['wavePeriod', 'waveHeight', 'windSpeed', 'windWaveHeight',
       'currentSpeed', 'NAP', 'waveOnshore', 'waveSideshore', 'windOnshore',
       'windSideshore', 'seaRise', 'pier']

# forecast_columns = ["rating", "hoog", "clean", "krachtig", "stijl", "stroming", "windy"]
forecast_columns = {
    "rating": ['waveEnergy', 'wavePeriod', 'windWaveHeight2', 'NAP', 'windMagOnShore', 'shelterWind', 'seaRise'],
    "hoog": ['waveEnergy', 'wavePeriod', 'seaRise'],
    "clean": ['windMagOnShore', 'waveEnergy', 'windWaveHeight2', 'shelterWind'],
    "krachtig": ['waveEnergy', 'NAP', 'seaRise'],
    "stijl": ['waveEnergy', 'wavePeriod', 'NAP', 'windMagOnShore', 'shelterWind'],
    "stroming": ['currentSpeed', 'seaRise', 'windMagOnShore'],
    "windy": ['windMagOnShore', 'windSpeed', 'shelterWind'],
}

MODELS = []
for perk, in_columns in forecast_columns.items():
    model = Model(perk, channels=in_columns)
    MODELS.append(model)

if __name__ == "__main__":
    model = MODELS[0]
    xgb.plot_tree(model.model, num_trees=3)
    fig = plt.gcf()
    fig.set_size_inches(150, 100)
    plt.show()
