from datetime import datetime
from pathlib import Path

import pandas as pd
from tabulate import tabulate

from data.stormglass import load_data


if __name__ == '__main__':
    name = "ZV"
    file = Path(f'data/stormglass/data_{name}.pkl')
    data_db = pd.read_pickle(file)
    print(tabulate(data_db))

    # data_total = pd.concat([data_db, data_new_historical], axis=0)
    # if len(data_new) > 0:  # save data
    #     data_total.to_pickle(file)
    # return data_new