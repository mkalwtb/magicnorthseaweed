import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from spots import ijmuiden, spots, camperduin
import matplotlib.dates as mdates
mxFmt_major = mdates.DateFormatter('%d-%m')
mxFmt_minor = mdates.DateFormatter('%H')

website_folder = Path("D:\Goodle Drive\magicnorthseaweed")

plot_titles = {
    "rating": "Surf rating",
    "waveHeight": "Golfhoogte [m]",
    "wavePeriod": "Periode[s]",
    "windSpeed": "Windsnelheid [m/s]",
    # "windDirection": "Wind richting [°]",
    "NAP": "getij [m]",
}


def angle_to_direction(angle):
    # Define the compass directions
    directions = ['N', 'NNO', 'NO', 'ONO', 'O', 'OZO', 'ZO', 'ZZO', 'Z', 'ZZW', 'ZW', 'WZW', 'W', 'WNW', 'NW', 'NNW']

    # Ensure the angle is within 0 to 360 degrees
    angle %= 360

    # Calculate the index of the direction based on the angle
    index = int((angle + 11.25) / 22.5) % 16

    # Return the corresponding direction
    return directions[index]


def index_interval(data: pd.DataFrame, amount: int):
    return data.iloc[::int(len(data) / amount)].index


def add_direction_annotations(ax, data, value_key, direction_key, num_annotations=6):
    t_range = index_interval(data, num_annotations)
    directions = data[direction_key].loc[t_range]
    direction_labels = [angle_to_direction(x) for x in directions]
    for label, t in zip(direction_labels, t_range):
        ax.annotate(label, xy=(t, data[value_key].loc[t]), xytext=(t, data[value_key].loc[t]),
                    ha='center', va='center', color='grey')


def plot_forecast(data, spot):
    fig, axs = plt.subplots(len(plot_titles), 1, figsize=(10.5, 10.5))
    fig.suptitle(f"{spot.name} surf forecast")

    for ax, (key, title) in zip(axs, plot_titles.items()):
        ax.plot(data[key], label=key)
        # ax.title.set_text(title)
        ax.set_ylabel(title)
        ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
        ax.xaxis.set_minor_formatter(mxFmt_minor)
        ax.grid(which="both")

        # wind dir labels
        if key == "windSpeed":
            add_direction_annotations(ax, data, value_key=key, direction_key="windDirection")

        if key == "waveHeight":
            add_direction_annotations(ax, data, value_key=key, direction_key="waveDirection")

        # Last x axis
        ax.xaxis.set_tick_params(which='major', pad=10)
        ax.xaxis.set_major_formatter(mxFmt_major)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))

    fig.tight_layout()


def save_to_web():
    plt.savefig(website_folder / f"{spot.name}.png")


if __name__ == '__main__':
    for spot in spots:  # [ijmuiden]:
        data = spot.surf_rating()
        plot_forecast(data, spot)
        save_to_web()
    plt.show()