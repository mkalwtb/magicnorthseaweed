import pickle
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from data.models import Model, forecast_columns, hoog2_forecase_cols
from data.spots import SPOTS
import xgboost as xgb

perk = 'hoogte-v2'
channels = hoog2_forecase_cols

dfs = pd.DataFrame()
for spot in SPOTS:
    df = spot.combined(only_spot_data=True, match_all_feedback_times=True,
                       fb_columns=perk)
    dfs = pd.concat([df, dfs])

dfs = dfs[channels + [perk]]
X = dfs.drop(perk, axis=1)
y = dfs[perk]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

model = xgb.XGBRegressor(objective='reg:squarederror', max_depth=3)
model.fit(X_train, y_train)

file_name = Path(f"AI-models/model_XGBRegressor_ZV_{perk}.pkl")
pickle.dump(model, open(file_name, "wb"))