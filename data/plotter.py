import pandas as pd
from matplotlib import pyplot as plt
from boeien import ijmuiden

data_db = "data_db.pkl"

time_48h48h = "-48,48"
time_48h0h = "-48,0"
time_28d = "-672,0"


def append_data(existing, new, overwrite_existing=True):
    if overwrite_existing:
        existing = existing.drop(existing.index.intersection(new.index))
    else:
        new = new.drop(new.index.intersection(existing.index))
    df = pd.concat([existing, new], axis=0)
    return df


if __name__ == '__main__':
    df_new = ijmuiden.download(time_48h48h, future=True, past=False)
    print(df_new)
    df_new.plot(subplots=True, grid=True)
    plt.show()
