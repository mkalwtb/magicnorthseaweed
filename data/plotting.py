import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
mxFmt_major = mdates.DateFormatter('%A, %d-%m')
mxFmt_minor = mdates.DateFormatter('%H')

website_folder = Path("D:\Goodle Drive\magicnorthseaweed")
perks = ['hoog', 'clean', 'krachtig', 'stijl', 'stroming', 'windy']
perk_levels = ["niet", "beetje", "best", "heel"]

y_labels_main = {
    "rating": "Surf rating",
    "waveHeight": "Golven [m]",
    "wavePeriod": "Periode [s]",
    "windSpeed": "Wind [m/s]",
    "NAP": "getij [m]",
}

y_labels_perks = {
    # "rating": "Surf rating",
    "hoog": "Hoog",
    "clean": "Clean",
    # "krachtig": "Krachtig",
    "stroming": "Stroming",
    # "windy": "Windy",
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


def plot_forecast(data: pd.DataFrame, spot, fig=None, axs=None, perks_plot=False):
    y_labels = y_labels_main
    add = 1 if perks_plot else 0


    if not fig and not axs:
        fig, axs = plt.subplots(len(y_labels) + add, 1, figsize=(10.5, 10.5))
        fig.suptitle(f"{spot.name} surf forecast")

    for ax, (key, title) in zip(axs, y_labels.items()):
        ax.plot(data[key], label=key)
        # ax.title.set_text(title)
        ax.set_ylabel(title)
        ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
        ax.xaxis.set_minor_formatter(mxFmt_minor)
        ax.grid(which="both")

        if key == "windSpeed":
            add_direction_annotations(ax, data, value_key=key, direction_key="windDirection")
        if key == "waveHeight":
            add_direction_annotations(ax, data, value_key=key, direction_key="waveDirection")
        if key == "rating":
            ax.set_ylim([1, 10])
        if key in ["windSpeed", "waveHeight"]:
            y_min, y_max = ax.get_ylim()
            ax.set_ylim([0, y_max])
        if key in ["wavePeriod"]:
            y_min, y_max = ax.get_ylim()
            ax.set_ylim([min(y_min, 4), max(9, y_max)])
        if key in perks:
            ax.set_ylim([0, 3])
            ax.set_yticklabels(perk_levels)


        ax.xaxis.set_tick_params(which='major', pad=10)
        ax.xaxis.set_major_formatter(mxFmt_major)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))

    if perks_plot:
        for key, title in y_labels_perks.items():
            axs[-1].plot(data[key], label=key)
        axs[-1].set_ylim([0, 3])
        axs[-1].grid(which="both")
        axs[-1].set_yticklabels(perk_levels)
        axs[-1].legend(y_labels_perks.values())
        axs[-1].xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
        axs[-1].xaxis.set_minor_formatter(mxFmt_minor)
        axs[-1].xaxis.set_tick_params(which='major', pad=10)
        axs[-1].xaxis.set_major_formatter(mxFmt_major)
        axs[-1].xaxis.set_major_locator(mdates.DayLocator(interval=1))



    axs[-1].text(0.25, -0.25, 'forecast from magicnorthseaweed.nl',
            horizontalalignment='left',
            verticalalignment='top',
            transform=axs[-1].transAxes,
            color="grey")

    fig.tight_layout()
    return fig, axs


def plot_all(spots, datas, perks_plot):
    for data, spot, i in zip(datas, spots, range(len(spots))):
        if i == 0:
            fig, axs = plot_forecast(datas[0], spots[0])
            for ax in axs:
                ax.grid(which="both")
        else:
            plot_forecast(data, spot, fig, axs, perks_plot=perks_plot)
        fig.legend([spot.name for spot in spots])
        fig.suptitle(f"Alle spots surf forecast")


def save_to_web(spot_name):
    plt.savefig(website_folder / f"{spot_name}.png")

