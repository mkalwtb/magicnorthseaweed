import pandas as pd
from matplotlib import pyplot as plt
from boeien import ijmuiden

data_db = "data_db.pkl"


def append_data(existing, new, overwrite_existing=True):
    if overwrite_existing:
        existing = existing.drop(existing.index.intersection(new.index))
    else:
        new = new.drop(new.index.intersection(existing.index))
    df = pd.concat([existing, new], axis=0)
    return df


if __name__ == '__main__':
    df_new = ijmuiden.download()
    print(df_new)

    df_all = pd.read_pickle(data_db)
    print(df_all)

    df_all = append_data(df_all, df_new)
    df_all.to_pickle(df_all)

    df_all.plot(subplots=True, grid=True)
    plt.show()