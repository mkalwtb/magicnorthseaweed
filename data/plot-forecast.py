import pandas as pd
from matplotlib import pyplot as plt
from boeien import ijmuiden, K13, boeien

data_db = "data_db.pkl"

last_future_2_days = "-48,48"
last_2_days = "-48,0"
last_month = "-672,0"


if __name__ == '__main__':
    # for boei in boeien:
    #     boei.plot()

    df_new = ijmuiden.download(last_future_2_days, future=True, past=False)

    df_new.plot(subplots=True, grid=True)
    plt.suptitle(ijmuiden.location_slug + " voorspelling")
    plt.show()