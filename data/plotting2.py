from math import radians, cos, sin
from typing import List

import pandas as pd
from tabulate import tabulate
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

style = """
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<style>
    table {
        min-width: 600px;
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

</style>
"""

def round_off_rating(number):
    # return number
    return round(number * 2) / 2


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
    if row["clean"] <= 1:
        if row["hoog"] >= 2.5 and row["krachtig"] >= 2:
            perks.append("stormachtig")
        elif row["hoog"] >= 1.5:
            perks.append("klotsbak")
        else:
            perks.append("rommel")
    elif row["clean"] >= 2:
        perks.append("clean")

    if row["hoog"] <= 0.3:
        perks.append("flat")
    elif row["hoog"] <= 1.2:
        perks.append("klein")
    elif row["hoog"] >= 2:
        perks.append("hoog")

    if row["stroming"] > 2:
        perks.append("stroming")
    return perks

def html_arrow(angle):
    angle_name = angle_to_direction(angle)
    return f"<span class='grey' title='{angle:.0f} deg''>{angle_name}</span>"
    # return f"<b title='{angle_name} ({angle:.0f} deg)' style='height: 18px; transform: rotate({angle+180:.0f}deg);'>&uarr;</b>"
    # return f"<i  class='fa fa-arrow-left' style='transform: rotate({angle+180:.0f}deg);'></i>"

def table_html(df):
    columns_df = ["rating", "waveHeight", "wavePeriod", "windSpeed"]
    # columns = ["rating", "waveHeight", "waveDirection", "wavePeriod", "windSpeed", "windDirection"]
    headers = ["Tijd", "rating", "golven", "wind", "getij", "beschrijving"]

    # header
    html = style
    html += f"<h2> {df.index[0].strftime('%A, %d-%m')} </h2>"
    html += "<table>\n"
    html += "<tr>\n"
    for header in headers:
        html += f"<th>{header}</th>\n"
    html += "</tr>\n"

    # rows
    df = df.between_time('08:00', '17:00')
    for index, row in df.iterrows():
        color = hex_colors[round(row['rating'])-1]
        color_bar = f"<div class='rounded-span'  style='background-color: {color}'></div>"

        html += "<tr>\n"
        html += f"\t<td>{index.strftime('%H:%M')}</td>\n"
        html += f"\t<td> {color_bar} <h3>{round_off_rating(row['rating']):.1f}</h3></td>\n"

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


def table_html_search(dfs):
    headers = ["Tijd"] + [df.name for df in dfs]

    # header
    html = style
    html += f"<h2> {df[0].index[0].strftime('%A, %d-%m')} </h2>"
    html += "<table>\n"
    html += "<tr>\n"
    for header in headers:
        html += f"<th>{header}</th>\n"
    html += "</tr>\n"
    pass

def table_per_day(df, function):
    df_days = [group[1] for group in df.groupby(df.index.date)]
    # table(df_days[1])

    html = ""
    for df_day in df_days:
        html += function(df_day)
    return html


def write_table_per_day(df, spot_name, function=table_html):
    html = table_per_day(df, function)
    with open(website_folder / "tables" / f"table_{spot_name}.html", "w") as fp:
        fp.write(html)


if __name__ == "__main__":
    df = pd.read_pickle("df.pkl")

    html = table_per_day(df, table_html)
    with open("table_ZV.html", "w") as fp:
        fp.write(html)

    # table_per_day(df, "ZV")

