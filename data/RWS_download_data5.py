from ddlpy import ddlpy
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter, DayLocator
import pandas as pd
from pandas import date_range
import os
import requests
from functools import reduce
from boeien import boeien
import numpy as np
import time
import xarray as xr
from io import BytesIO
from bs4 import BeautifulSoup
import logging
import sys
import json
from tabulate import tabulate
from io import StringIO
from scipy.stats import bootstrap
pd.set_option('display.expand_frame_repr', False)

#Hm0 = Significante golfhoogte in het spectrale domein Oppervlaktewater golffrequentie tussen 30 en 500 mHz in cm
#H1/3 = Gem. hoogte van hoogste 1/3 deel v.d. golven (tijdsdomein) Oppervlaktewater cm
#T1/3 = Gem. golfperiode langste 1/3 deel v.d. golven (tijdsdomein) Oppervlaktewater s
#T_H1/3 = Golfperiode die hoort bij H1/3 Oppervlaktewater s
#Th0 = Gemiddelde golfrichting in het spectrale domein Oppervlaktewater golffrequentie tussen 30 en 500 mHz in graad
#Th3 = Gem. richting deining tov ware noorden in spectrale domein Oppervlaktewater t.o.v. ware Noorden in graad
#WINDRTG = DD_10: wind direction average height sensor. (DD_10 is wind richting gem. hoogte sensor)
#WINDSHD = FF_10M_10: wind speed average sea converted. 10m land height sensor. (FX_10M_10 is wind snelh. werkelijk)

#SWAN voorspelling
#GM.1 = sign golfverwachting
#GM.9 = gem. golf periode [s]
#GM.5 = Gem. golfrichting

#HARMONIE voorspelling
#WN.1 = downscaling verwachting wind m/sec
#WN.2 = downscaling verwachting wind richt.

def check_df(df):
    #set the datetime index
    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d %H:%M')
    df.index = pd.to_datetime(df.index)

    # drop the indices that have 'None'
    df = df[df.index.notna()]

    # check for duplicate indices and for every duplicate remove the second one
    df = df.sort_index()
    if any(df.index.duplicated()):
        print("df had duplicate indices")
        duplicates = df.index.duplicated(keep='first')  # Mark duplicates, keeping the first occurrence
        df = df[~duplicates]

    # change , to . and replace values larger than 9999 or that are 0 to nan
    df = df.replace(',', '.', regex=True)
    df = df.apply(pd.to_numeric, errors='coerce')  # convert df to float, but leaving nan as nan
    df = df.mask(df >= 9999, np.nan)
    df = df.mask(df == 0, np.nan)

    return df

def waterbericht_download():

    #2021-02-28 23:00:00 first prediction waves
    #2023-02-24 12:00:00 first prediction wind
    #2021-04-01 08:30:00 first metingen

    start_date = datetime.strptime(start, '%Y-%m-%d').strftime('%Y-%m-%d') + "T00:00:00Z" #"2023-12-01T00:00:00Z"
    end_date = end.strftime('%Y-%m-%d') + "T00:00:00Z"

    #predictions
    #url_swan_wave_h =           "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=GM.1&sourceName=X-SWAN-KUST_6&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=" + str(boei.swan_code)
    #url_swan_wave_dir =         "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=GM.5&sourceName=X-SWAN-KUST_6&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=" + str(boei.swan_code)
    #url_swan_wave_period =      "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=GM.9&sourceName=X-SWAN-KUST_6&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=" + str(boei.swan_code)
    # # #measurements
    # url_wave_h =           "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=GH10.1&sourceName=S_1&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=MUNS"
    # url_wave_dir =             "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=GR.1-51&sourceName=S_1&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=MUNS"
    # url_wave_period =          ""
    # url_wind_dir =              "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=WN.2&sourceName=S_1&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=SPY1"
    # url_wind_sp =               "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=WN.1&sourceName=S_1&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=SPY1"

    url_harmonie_wind_sp =      "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=WN.1&sourceName=knmi_6&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=SPY1"
    url_harmonie_wind_dir =     "https://waterberichtgeving.rws.nl/wb/data/api/dd/2.0/timeseries?observationTypeId=WN.2&sourceName=knmi_6&=&startTime=" + str(start_date) + "&endTime=" + str(end_date) + "&locationCode=SPY1"

    url_prediction_list = [url_harmonie_wind_sp, url_harmonie_wind_dir]

    list_dates = []
    list_dfs = []

    for url in url_prediction_list:

        # Send an HTTP request to download the CSV file
        response = requests.get(url)
        data = json.loads(response.text)

       # print(json.dumps(data, indent=2))  # indent for pretty printing

        for result in data['results']:
            #get the data from the json
            data = result['events']

            #get the column names from the json
            observation_type = result.get("observationType", {})
            quantity = observation_type.get("quantity")

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Convert 'timeStamp' to datetime and set it as the index
        df['Datetime'] = pd.to_datetime(df['timeStamp'])
        df.set_index('Datetime', inplace=True)
        df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d %H:%M')
        df.drop(columns=['timeStamp'], inplace=True)

        #rename column
        if quantity == "downscaling verwachting wind m/sec":
            column_name = "harmonie_wind_speed"
        elif quantity == "downscaling verwachting wind richt.":
            column_name = "harmonie_wind_direction"
        df.rename(columns={'value': column_name}, inplace=True)

        #check the df
        df = check_df(df)

        #drop rows that have all nan
        df = df.dropna(axis=0, how='all')

        # get the first and last dateindex of the df
        list_dates.append(df.index[0])
        list_dates.append(df.index[-1])

        list_dfs.append(df)

    #create df_datetime from dates
    df_datetime = pd.DataFrame(index=date_range(start=min(list_dates), end=max(list_dates), freq='10min'))
    df_datetime.index = pd.to_datetime(df_datetime.index).strftime('%Y-%m-%d %H:%M')
    df_datetime.index = pd.to_datetime(df_datetime.index)
    df_datetime.index.name = 'Datetime'

    #merge the dfs to df_datetime
    for df in list_dfs:
        df_datetime = df_datetime.merge(df, how='left', left_index=True, right_index=True)
    df_waterbericht = df_datetime

    #add one hour to the index, because the time is in UTM (Universal Time, Coordinated), with a timezone offset of +0)
    df_waterbericht.index = df_waterbericht.index + timedelta(hours=1)

    return df_waterbericht

def matroos_download():

    start_date =    datetime.strptime(start, '%Y-%m-%d').strftime('%Y%m%d') + "0000"    #"202312010000"
    end_date =      end.strftime('%Y%m%d') + "0000"

    #SWAN urls
    url_swan_wave_hm0 = "https://noos.matroos.rws.nl/direct/get_series.php?loc=ijgeul_stroompaal1&source=swan_kuststrook_harmonie&unit=wave_height_hm0&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"
    url_swan_wave_dir = "https://noos.matroos.rws.nl/direct/get_series.php?loc=ijgeul_stroompaal1&source=swan_kuststrook_harmonie&unit=wave_direction&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"
    url_swan_wave_period = "https://noos.matroos.rws.nl/direct/get_series.php?loc=ijgeul_stroompaal1&source=swan_kuststrook_harmonie&unit=wave_period&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"

    #DCSM urls
    url_dcsm_wave_hm0 = "https://noos.matroos.rws.nl/direct/get_series.php?loc=ijgeul_stroompaal1&source=swan_dcsm_harmonie&unit=wave_height_hm0&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"
    url_dcsm_wave_dir = "https://noos.matroos.rws.nl/direct/get_series.php?loc=ijgeul_stroompaal1&source=swan_dcsm_harmonie&unit=wave_direction&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"
    url_dcsm_wave_period = "https://noos.matroos.rws.nl/direct/get_series.php?loc=ijgeul_stroompaal1&source=swan_dcsm_harmonie&unit=wave_period&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"

    #observed urls
    url_observed_wave_hm0 = "https://noos.matroos.rws.nl/direct/get_series.php?loc=spy&source=observed&unit=wave_height_hm0&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"
    url_observed_wave_dir = "https://noos.matroos.rws.nl/direct/get_series.php?loc=ijm2&source=observed&unit=wave_direction&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"
    url_observed_wave_period = "https://noos.matroos.rws.nl/direct/get_series.php?loc=spy&source=observed&unit=wave_period&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"
    url_observed_wind_speed = "https://noos.matroos.rws.nl/direct/get_series.php?loc=spy&source=observed&unit=wind_speed&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"
    url_observed_wind_direction = "https://noos.matroos.rws.nl/direct/get_series.php?loc=spy&source=observed&unit=wind_direction&tstart=" + start_date + "&tstop=" + end_date + "&timezone=MET"

    url_list = [url_swan_wave_hm0, url_swan_wave_dir, url_swan_wave_period, url_dcsm_wave_hm0, url_dcsm_wave_dir, url_dcsm_wave_period, url_observed_wave_hm0, url_observed_wave_dir, url_observed_wave_period, url_observed_wind_speed, url_observed_wind_direction]

    list_dates = []
    list_dfs = []

    for url in url_list:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and print the text content
            text_content = soup.get_text()

            # Find the line containing "# Source      :"
            source_line = [line.strip() for line in text_content.split('\n') if "# Source      :" in line][0]
            source_value = source_line.split(":")[1].strip()

            # Find the line containing "# Unit        :"
            unit_line = [line.strip() for line in text_content.split('\n') if "# Unit        :" in line][0]
            unit_value = unit_line.split(":")[1].strip()

            if source_value == 'swan_kuststrook_harmonie':
                column_name = 'swan_' + unit_value
            elif source_value == 'observed':
                column_name = 'observed_' + unit_value
            elif source_value == 'swan_dcsm_harmonie':
                column_name = 'dcsm_' + unit_value

            # Remove metadata lines and create a Pandas DataFrame
            df = pd.read_csv(StringIO("\n".join(line for line in text_content.splitlines() if not line.startswith('#'))),delim_whitespace=True, header=None, names=['Timestamp', column_name])

            # Convert 'Timestamp' column to datetime
            df['Datetime'] = pd.to_datetime(df['Timestamp'], format='%Y%m%d%H%M')
            df.set_index('Datetime', inplace=True)
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d %H:%M')
            df.drop(columns=['Timestamp'], inplace=True)

            #check df
            df = check_df(df)

            # get the first and last dateindex of the df
            list_dates.append(df.index[0])
            list_dates.append(df.index[-1])

            list_dfs.append(df)

        else:
            print(f"Failed to retrieve content. Status code: {response.status_code}")

    # create df_datetime from dates
    df_datetime = pd.DataFrame(index=date_range(start=min(list_dates), end=max(list_dates), freq='10min'))
    df_datetime.index = pd.to_datetime(df_datetime.index).strftime('%Y-%m-%d %H:%M')
    df_datetime.index = pd.to_datetime(df_datetime.index)
    df_datetime.index.name = 'Datetime'

    # merge the dfs to df_datetime
    for df in list_dfs:
        df_datetime = df_datetime.merge(df, how='left', left_index=True, right_index=True)
    df_matroos = df_datetime

    #drop rows with all nan
    df_matroos = df_matroos.dropna(how='all')

    return df_matroos

def plot(df_total):

    # create df's based on past or future predictions
    df_past = df_total[df_total.index < datetime.now()]
    df_future = df_total[df_total.index >= datetime.now()]

    #create numpy arrays for the polynomial fit
    swan_hm0 = df_past['swan_wave_height_hm0'].to_numpy()
    hm0 = df_past['observed_wave_height_hm0'].to_numpy()

    #delete nan from x and y and create polynomial
    non_nan = np.isfinite(swan_hm0) & np.isfinite(hm0)
    poly_hm0 = np.poly1d(np.polyfit(swan_hm0[non_nan], hm0[non_nan], 2))

    #plot swan vs hm0 polynomial
    plt.scatter(swan_hm0[non_nan], hm0[non_nan], color='blue')
    plt.plot(swan_hm0[non_nan], poly_hm0(swan_hm0[non_nan]), color='orange')

    #add labels
    plt.xlabel("SWAN")
    plt.ylabel("hm0")
    plt.title(str(boei.swan_code))

    plt.show()

    figure, axis = plt.subplots(5, 1)

    #for the plotting, only show dates from x days ago untill x days into the future
    df_past = df_past[df_past.index > (datetime.now() - timedelta(days=5))]
    df_past = df_past[df_past.index < (datetime.now() + timedelta(days=2))]

    #plot past wave height
    axis[0].plot(df_past['swan_wave_height_hm0'].dropna(), label='swan_wave_height_hm0', color='blue')
    axis[0].plot(df_past['dcsm_wave_height_hm0'].dropna(), label='dcsm_wave_height_hm0', color='blue', linestyle='dotted')
    axis[0].plot(df_past['observed_wave_height_hm0'].dropna(), label='observed_wave_height_hm0', color='orange')
    axis[0].plot(df_past['swan_wave_height_hm0'].dropna().index, poly_hm0(df_past['swan_wave_height_hm0'].dropna().to_numpy()), label='Corrected golfhoogte SWAN', color='black')

    #plot future wave height
    axis[0].plot(df_future['swan_wave_height_hm0'].dropna(), color='blue')
    axis[0].plot(df_future['dcsm_wave_height_hm0'].dropna(), color='blue', linestyle='dotted')
    axis[0].plot(df_future['swan_wave_height_hm0'].dropna().index, poly_hm0(df_future['swan_wave_height_hm0'].dropna().to_numpy()), color='black')

    #plot past wave direction
    df_past['swan_wave_direction'] = np.cos(np.radians(df_past['swan_wave_direction'].values))
    df_past['dcsm_wave_direction'] = np.cos(np.radians(df_past['dcsm_wave_direction'].values))
    df_past['observed_wave_direction'] = np.cos(np.radians(df_past['observed_wave_direction'].values))
    axis[1].plot(df_past['swan_wave_direction'].dropna(), label='swan_wave_direction',color='blue')
    axis[1].plot(df_past['dcsm_wave_direction'].dropna(), label='dcsm_wave_direction', color='blue', linestyle='dotted')
    axis[1].plot(df_past['observed_wave_direction'].dropna(), label='observed_wave_direction', color='orange')

    #plot future wave direction
    df_future['swan_wave_direction'] = np.cos(np.radians(df_future['swan_wave_direction'].values))
    df_future['dcsm_wave_direction'] = np.cos(np.radians(df_future['dcsm_wave_direction'].values))
    axis[1].plot(df_future['swan_wave_direction'].dropna(), color='blue')
    axis[1].plot(df_future['dcsm_wave_direction'].dropna(), color='blue', linestyle='dotted')

    #plot past wave period
    axis[2].plot(df_past['swan_wave_period'].dropna(), label='swan_wave_period',color='blue')
    axis[2].plot(df_past['dcsm_wave_period'].dropna(), label='dcsm_wave_period', color='blue', linestyle='dotted')
    axis[2].plot(df_past['observed_wave_period'].dropna(), label='observed_wave_period', color='orange')

    #plot future wave period
    axis[2].plot(df_future['swan_wave_period'].dropna(), color='blue')
    axis[2].plot(df_future['dcsm_wave_period'].dropna(), color='blue', linestyle='dotted')

    #plot past wind direction
    df_past['harmonie_wind_direction'] = np.cos(np.radians(df_past['harmonie_wind_direction'].values))
    df_past['observed_wind_direction'] = np.cos(np.radians(df_past['observed_wind_direction'].values))
    axis[3].plot(df_past['harmonie_wind_direction'].dropna(), label='harmonie_wind_direction',color='blue')
    axis[3].plot(df_past['observed_wind_direction'].dropna(), label='observed_wind_direction', color='orange')

    #plot future wind direction
    df_future['harmonie_wind_direction'] = np.cos(np.radians(df_future['harmonie_wind_direction'].values))
    axis[3].plot(df_future['harmonie_wind_direction'].dropna(), color='blue')

    #plot past wind direction
    axis[4].plot(df_past['harmonie_wind_speed'].dropna(), label='harmonie_wind_speed',color='blue')
    axis[4].plot(df_past['observed_wind_speed'].dropna(), label='observed_wind_speed', color='orange')

    #plot future wind direction
    axis[4].plot(df_future['harmonie_wind_speed'].dropna(), color='blue')

    #format the y axis and colors of lines at ticks
    for ax_id, ax in enumerate(axis):
        if ax_id == 1 or ax_id == 3:
            ax.set_ylim(-1, None)
        else:
            ax.set_ylim(0, None)

        ax.tick_params(axis='x', which='minor', length=40, width=2, labelcolor='black', labelsize=8)
        ax.tick_params(axis='x', which='major', length=2, width=1, labelcolor='black', labelsize=8)
        ax.grid(which='major', linestyle='-', linewidth='0.5', color='gray')
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

        # Add legends to each subplot
        ax.legend()

    # Set hourly and daily ticks on the x-axis for the last subplot
    axis[-1].xaxis.set_major_locator(HourLocator(byhour=[6, 12, 18]))
    axis[-1].xaxis.set_major_formatter(DateFormatter('%H:%M'))
    axis[-1].xaxis.set_minor_locator(DayLocator(interval=1))
    axis[-1].xaxis.set_minor_formatter(DateFormatter('%Y-%m-%d'))

    for label in axis[-1].get_xticklabels():
        label.set_rotation(90)
        label.set_ha('center')

    plt.show()


for boei in boeien: #loop through the buoys

    start = '2023-12-12'
    end = datetime.now() + timedelta(days=4)

    df_waterbericht = waterbericht_download()
    df_matroos = matroos_download()

    print(df_waterbericht)

    df_total = df_waterbericht.merge(df_matroos, how='outer', left_index=True, right_index=True)

    print(df_total)

    plot(df_total)

