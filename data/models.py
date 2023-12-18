import pickle
from pathlib import Path

import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


class Model:
    def __init__(self, perk: str, model=None):
        self.perk = perk
        self.model: xgb.XGBModel = model if model is not None else self._load_model()

    @classmethod
    def train(cls, spots, channel, verbose=False, save=True, match_all_feedback_times=True):
        """Train a model, save it and returns the model"""
        dfs = pd.DataFrame()
        for spot in spots:
            df = spot.combined(only_spot_data=True, match_all_feedback_times=match_all_feedback_times,
                               fb_columns=channel)
            dfs = pd.concat([df, dfs])

        X = dfs.drop(channel, axis=1)
        y = dfs[channel]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        model = xgb.XGBRegressor(objective='reg:squarederror')
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)

        print(f'Mean Squared Error: {mse:.2f} (from {len(dfs)} feedback entries)')
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


forecast_columns = ["rating", "hoog", "clean", "krachtig", "stijl", "stroming", "windy"]
MODELS = [Model(perk) for perk in forecast_columns]
