from matplotlib import pyplot as plt
from plotting import plot_forecast, save_to_web
from spots import spots

if __name__ == '__main__':
    for spot in spots:  # [ijmuiden]:
        data = spot.surf_rating(cache=True)
        plot_forecast(data, spot)
        save_to_web(spot.name)
    plt.show()