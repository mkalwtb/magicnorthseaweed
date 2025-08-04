from datetime import timezone, timedelta
from math import radians, cos, sin, floor
from typing import List

import pandas as pd
from suntime import suntime
from tabulate import tabulate

from surffeedback import hoogte_label
from plotting import angle_to_direction
from plotting import website_folder

hex_colors = [
    "rgba(255, 0, 0, 0.0)", "rgba(255, 0, 0, 0.0)", "rgba(255, 0, 0, 0.0)",
    "#e31a1c",  # Red for scale
    "#fc7d23",  # Orange for scale
    "#fdd036",  # Yellow for scale
    # "#d2d550", #
    "#a6d96a",  # Light green for scale 7
    "#86cb67", # 8 light green
    # "#76c465",  # 8 medium
    "#66bd63",  # 9 green
    "#800080"  # purple for scale 10
]

def get_color(rating: float) -> str:
    return hex_colors[floor(rating+0.5)-1] if rating > 0 else "rgba(255, 0, 0, 0.0)"

head = """
<head>
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<meta http-equiv="Pragma" content="no-cache" />
<meta http-equiv="Expires" content="0" />
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    table {
        border-collapse: collapse;
        margin-top: 20px;
    }

    th, td {
        text-align: center;
        white-space: nowrap;
        vertical-align: middle;
        /* border: 1px solid #ddd; Adding a border for better visibility */
    }

    h3 {
      display: inline-block; /* Make the h3 inline-block */
      margin: 5px; /* Add some margin between the div and h3 */
    }

    th {
        background-color: #f2f2f2;
    }
    .grey {
        color: rgb(152, 162, 175);
    }
    .unit {
        font-size: 14px;
        padding-right: 12px;
    }
    .rounded-span {
        height: 20px; /* Adjust the height as needed */
        width: 5px; /* Adjust the height as needed */
        border-radius: 2.5px; /* Adjust the border-radius for round corners */
        display: inline-block;
    }
    .large {
        min-width: 700px;
    }
    .widget {
        width: 100%;
        max-width: 300px; /* Or any maximum width you prefer */
        margin: auto; /* Centers the container */
    }
    .widget table {
        width: 300px; /* Set a minimum width for the table */
        font-size: 32px;
    }
    .large-font-table {
        font-size: 1.5em; /* Adjust the size as needed */
        /* Other styling as needed */
    }

    .widget table {
        width: 300px; /* Set a minimum width for the table */
        font-size: 32px; /* Increase font size */
    }
    body {
        font-size: 32px; /* Increase font size */
    }
    .large-font-table .unit, .grey {
        font-size: 10px; /* Adjust text sizes within the table */
    }
}

</style>
</head>
"""

def round_off_rating(number):
    return number
    # return round(number * 2) / 2


def replace_last_comma_by_and(string):
    delimiter = ", "
    replacement = " en "
    if delimiter in string:
        start, _, end = string.rpartition(delimiter)
        return start + replacement + end
    else:
        return string


def perk_identification(row):
    perks = []
    # if row["krachtig"] > 2:
    #     perks.append("krachtig")
    if row["rating"] < 6:
        return []

    if row["clean"] < 1:
        if row["hoog"] >= 2:
            perks.append("stormy")
        else:
            perks.append("klotsbak")
    elif row["clean"] >= 1.8:
        perks.append("clean")
    elif row["clean"] >= 2.6:
        perks.append("ultra clean")


    if row["stroming"] >= 2.6:
        perks.append("veel stroming")
    elif row["stroming"] >= 1.8:
        perks.append("stroming")

    if row["windy"] >= 1.8:
        perks.append("windy")
    elif row["windy"] >= 2.6:
        perks.append("heel windy")

    return perks

def html_arrow(angle):
    angle_name = angle_to_direction(angle)
    return f"<span class='grey' title='{angle:.0f} deg''>{angle_name}</span>"
    # return f"<b title='{angle_name} ({angle:.0f} deg)' style='height: 18px; transform: rotate({angle+180:.0f}deg);'>&uarr;</b>"
    # return f"<i  class='fa fa-arrow-left' style='transform: rotate({angle+180:.0f}deg);'></i>"

def table_html(df, spot):
    headers = ["Tijd", "rating", "hoogte", "swell", "wind", "getij", "beschrijving"]

    # header
    html = head
    html += f"<h3> {df.index[0].strftime('%A, %d-%m')} </h3>"
    html += "<table class='large'>\n"
    html += "<tr>\n"
    for header in headers:
        html += f"<th>{header}</th>\n"
    html += "</tr>\n"

    # rows
    df = df.between_time('06:00', '23:00')
    for index, row in df.iterrows():

        color = get_color(row['rating'])
        color_bar = f"<div class='rounded-span'  style='background-color: {color}'></div>"

        html += "<tr>\n"
        html += f"\t<td>{index.strftime('%H:%M')}</td>\n"
        html += f"\t<td> {color_bar} <h3>{round_off_rating(row['rating']):.1f}</h3></td>\n"

        hoogtev2 = hoogte_label(row["hoogte-v2"])
        html += f"\t<td>{hoogtev2}</td>\n"

        div = "<td>"
        div += f"<b>{row['waveHeight']:.1f} </b> <i class='unit'>m</i>"
        div += f"<b>{row['wavePeriod']:.0f} </b> <i class='unit'>s</i>"
        div += html_arrow(row["waveDirection"])
        div += "</td>"
        html += div

        html += f"\t<td>{row['windSpeed']*3.6:.0f}  <i class='unit'>km/h</i>"
        html += f"{html_arrow(row['windDirection'])}</td>"

        html += f"\t<td>{10*round(10*row['NAP']):.0f} <i class='unit'>cm</i></td>"

        html += "<td>"
        perks = perk_identification(row)
        html += replace_last_comma_by_and(", ".join(perks))
        html += "</td>"

        html += "</tr>\n"
    html += "</table>\n"
    return html

def table_html_simple(df, spot):
    headers = [spot.name, "", "hoogte", "wind"]

    # header
    html =  head + "\n<body>"
    with open("website-components/tableFilterNow.js", 'r') as fp:
        html += "\n<script>\n" + fp.read() + "\n</script>\n"
    html += "<table id='timeTable' class='widget'>\n"
    html += "<tr>\n"
    for header in headers:
        html += f"<th>{header}</th>\n"
    html += "</tr>\n"

    # rows
    time_zone_cet = timezone(timedelta(hours=1))  # Central European Time
    sun = suntime.Sun(spot.lat, spot.long)
    sun_set = sun.get_sunset_time(time_zone=time_zone_cet).hour + 2
    sun_rise = sun.get_sunrise_time(time_zone=time_zone_cet).hour +2
    df = df.between_time(f'{sun_rise}:00', f'{sun_set}:00')
    for index, row in df.iterrows():
        color = get_color(row['rating'])
        color_bar = f"<div class='rounded-span'  style='background-color: {color}'></div>"

        html += f"<tr data-time='{index}'>\n"
        html += f"\t<td>{index.strftime('%H:%M')}</td>\n"
        html += f"\t<td> {color_bar} <h3>{round_off_rating(row['rating']):.1f}</h3></td>\n"

        hoogtev2 = hoogte_label(row["hoogte-v2"])
        html += f"\t<td>{hoogtev2}</td>\n"

        html += f"\t<td>{row['windSpeed']*3.6:.0f}  <i class='unit'>km/h</i>"
        html += f"{html_arrow(row['windDirection'])}</td>"

        # html += f"\t<td>{10*round(10*row['NAP']):.0f} <i class='unit'>cm</i></td>"

        # html += "<td>"
        # perks = perk_identification(row)
        # html += replace_last_comma_by_and(", ".join(perks))
        # html += "</td>"

        html += "</tr>\n"
    html += "</table>\n"
    html += "</body>\n"
    return html


def weekoverzicht(datas):

    n_hours_av = 3
    datas_daily = [spot.rolling(n_hours_av).mean().resample('D').max() for spot in datas]
    for data_daily, data in zip(datas_daily, datas):
        data_daily["hoogte-v2"] = data["hoogte-v2"].rolling(n_hours_av).mean().resample('D').mean()

    names = [spot.name for spot in datas]
    rating = pd.concat([spot["rating"] for spot in datas_daily], axis=1, keys=names)
    hooogte = pd.concat([spot["hoogte-v2"] for spot in datas_daily], axis=1, keys=names)

    html = head
    html += "<table>\n"
    html += "<tr>\n"
    html += "<th></th>\n"
    for name in names:
        html += f"<th>{name}</th>\n"
    html += "</tr>\n"

    for (index, row_rating), (_, row_hoogte) in zip(rating.iterrows(), hooogte.iterrows()):
        html += "<tr>\n"
        html += f"\t<td>{index.strftime('%A, %d-%m')}</td>\n"
        for name in names:
            print(row_rating[name])
            color = get_color(row_rating['name'])
            hoogtev2 = hoogte_label(row_hoogte[name]) if row_hoogte[name] > 0 else "geen data"
            color_bar = f"<div class='rounded-span'  style='background-color: {color}'></div>"
            html += f"\t<td style='text-align: left;'>{color_bar} <h3>{round_off_rating(row_rating[name]):.1f}</h3> {hoogtev2}</td>\n"

        html += "</tr>\n"

    html += "</table>\n"
    with open(website_folder / "tables" / "weekoverzicht.html", "w") as fp:
        fp.write(html)


def table_html_search(dfs):
    headers = ["Tijd"] + [df.name for df in dfs]

    # header
    html = head
    html += f"<h2> {dfs[0].index[0].strftime('%A, %d-%m')} </h2>"
    html += "<table>\n"
    html += "<tr>\n"
    for header in headers:
        html += f"<th>{header}</th>\n"
    html += "</tr>\n"
    pass

def table_per_day(df, spot, function):
    df_days = [group[1] for group in df.groupby(df.index.date)]
    # table(df_days[1])

    html = ""
    for df_day in df_days:
        if len(df_day) == 0:
            continue
        html += function(df_day, spot)
    return html


def write_table_per_day(df, spot, function=table_html):
    html = table_per_day(df, spot, function)
    with open(website_folder / "tables" / f"table_{spot.name}.html", "w") as fp:
        fp.write(html)


def write_simple_table(df, spot):
    html = table_html_simple(df, spot)
    with open(website_folder / "tables_widget" / f"table_{spot.name}.html", "w") as fp:
        fp.write(html)


if __name__ == "__main__":
    df = pd.read_pickle("df.pkl")

    html = write_simple_table(df, "ZV")

    # table_per_day(df, "ZV")

