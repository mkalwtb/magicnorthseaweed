import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from boeien import ijmuiden, K13, boeien

DATA_FOLDER = Path("boei-data")

time_48h48h = "-48,48"
time_48h0h = "-48,0"
time_28d = "-672,0"


def append_data(existing, new, overwrite_existing=True):
    if overwrite_existing:
        existing = existing.drop(existing.index.intersection(new.index))
    else:
        new = new.drop(new.index.intersection(existing.index))
    n_new_lines = len(existing.index.intersection(new.index))
    print(f"Added {n_new_lines} lines of data.")
    df = pd.concat([existing, new], axis=0)
    return df


def download_to_database(boei):
    df_new = boei.download(time_28d, future=False, past=True)

    # Append to existing data
    db_name = DATA_FOLDER / (boei.locationSlug + ".pkl")
    if db_name.is_file():
        df_all = pd.read_pickle(db_name)
        df_all = append_data(df_all, df_new)
    else:
        df_all = df_new
    df_all.to_pickle(db_name)
    return df_all


if __name__ == '__main__':
    for boei in boeien:
        data = download_to_database(boei)
        print(data)
