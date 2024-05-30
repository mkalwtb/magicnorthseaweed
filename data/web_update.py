from matplotlib import pyplot as plt
from plotting import plot_forecast, save_to_web, plot_all
import plotting2
from spots import spots, texel_paal17, ijmuiden
from tabulate import tabulate

if __name__ == '__main__':
    datas = []
    for spot in [ijmuiden]:  # [ijmuiden]:
        data = spot.surf_rating(cache=True)
        data.name = spot.name
        # csv = data.to_csv()
        # print(csv)
        datas.append(data)
        plotting2.write_table_per_day(data, spot)
        plotting2.write_simple_table(data, spot)
        plot_forecast(data, spot, perks_plot=True)
        save_to_web(spot.name)

    fig = plot_all(spots, datas, perks_plot=False)
    save_to_web("all")

    fig.show()
    plt.show()