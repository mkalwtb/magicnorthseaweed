import sys
import os

import alert

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from matplotlib import pyplot as plt

from data.models import MODELS
from plotting import plot_forecast, save_to_web, plot_all
import webtables
from spots import SPOTS, texel_paal17, ijmuiden, ZV, schev, NW
from tabulate import tabulate

if __name__ == '__main__':
    datas = []
    for spot in [NW]:  # [ijmuiden]:
        data = spot.surf_rating(cache=False, models=MODELS)
        data.name = spot.name
        datas.append(data)
        # alert.check(data, spot, alert_filters=alert.FILTERS)
        webtables.write_table_per_day(data, spot)
        webtables.write_simple_table(data, spot)
        # plot_forecast(data, spot, perks_plot=True)
        save_to_web(spot.name)

    if len(datas) == len(SPOTS):
        webtables.weekoverzicht(datas)

    ZV = [data for data in datas if data.name == "ZV"][0]
    ZV_simple = ZV.resample('D').max()
    # print(tabulate(ZV_simple[["rating", "hoogte-v2"]], headers='keys', floatfmt=".1"))

    # plt.show()