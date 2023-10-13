import pandas as pd
from pathlib import Path
import plotly.graph_objs as go
import matplotlib.dates as mdates
from plotly.subplots import make_subplots

mxFmt_major = mdates.DateFormatter('%d-%m')
mxFmt_minor = mdates.DateFormatter('%H')

website_folder = Path("D:\Goodle Drive\magicnorthseaweed")

plot_titles = {
    "rating": "Surf rating",
    "waveHeight": "Golven [m]",
    "wavePeriod": "Periode [s]",
    "windSpeed": "Wind [m/s]",
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

def add_direction_annotations(fig, data, value_key, direction_key, num_annotations=6):
    t_range = index_interval(data, num_annotations)
    directions = data[direction_key].loc[t_range]
    direction_labels = [angle_to_direction(x) for x in directions]

    for label, t in zip(direction_labels, t_range):
        fig.add_annotation(
            text=label,
            x=t,
            y=data[value_key].loc[t],
            showarrow=False,
            font=dict(color='grey')
        )

def create_subplot(data, key, title):
    subplot = go.Scatter(
        x=data.index,
        y=data[key],
        mode='lines',
        line=dict(width=2),
        marker=dict(size=4),
        name=key
    )
    return subplot

def plot_forecast(data: pd.DataFrame, spot):
    fig = make_subplots(rows=len(plot_titles), cols=1, shared_xaxes=True, subplot_titles=list(plot_titles.values()))

    for i, (key, title) in enumerate(plot_titles.items(), start=1):
        subplot = create_subplot(data, key, title)
        fig.add_trace(subplot, row=i, col=1)

        if key == "windSpeed":
            add_direction_annotations(fig, data, value_key=key, direction_key="windDirection")
        if key == "waveHeight":
            add_direction_annotations(fig, data, value_key=key, direction_key="waveDirection")

    fig.update_xaxes(
        title_text="Time",
        tickangle=45,
        tickvals=data.index,
        tickformat="%d-%m %H",
        showgrid=True,
        gridcolor='lightgray',
    )

    fig.update_yaxes(
        title_text="Value",
        showgrid=True,
        gridcolor='lightgray'
    )

    return fig


def save_to_web(fig, spot_name):
    fig.write_html(str(website_folder / f"{spot_name}.html"))  # Save as HTML instead of PNG for interactivity