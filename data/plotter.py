import pandas as pd
from matplotlib import pyplot as plt
from boeien import ijmuiden, K13

data_db = "data_db.pkl"

last_future_2_days = "-48,48"
last_2_days = "-48,0"
last_month = "-672,0"


def append_data(existing, new, overwrite_existing=True):
    if overwrite_existing:
        existing = existing.drop(existing.index.intersection(new.index))
    else:
        new = new.drop(new.index.intersection(existing.index))
    df = pd.concat([existing, new], axis=0)
    return df


if __name__ == '__main__':
    boeien = [ijmuiden, K13]
    for boei in boeien:
        df_new = boei.download(last_future_2_days, future=False, past=True)
        print(df_new)
        df_new.plot(subplots=True, grid=True)
        plt.suptitle(boei.locationSlug)

    df_new = ijmuiden.download(last_future_2_days, future=True, past=False)
    print(df_new)
    df_new.plot(subplots=True, grid=True)
    plt.suptitle(ijmuiden.locationSlug + " voorspelling")
    plt.show()
