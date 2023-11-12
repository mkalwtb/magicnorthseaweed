from matplotlib import pyplot as plt
from plotting import plot_forecast, save_to_web, plot_all
from spots import spots, texel_paal17, ijmuiden
from tabulate import tabulate

if __name__ == '__main__':
    datas = []
    for spot in spots:  # [ijmuiden]:
        data = spot.surf_rating(cache=False)
        datas.append(data)
        plot_forecast(data, spot)
        save_to_web(spot.name)


    plot_all(spots, datas)
    save_to_web("all")

    plt.show()