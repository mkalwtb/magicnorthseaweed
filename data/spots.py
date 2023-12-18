import pandas as pd
import numpy as np
from copy import deepcopy, copy
import datetime
import re
from dataclasses import dataclass
from matplotlib import pyplot as plt

from data.models import Model, MODELS
from plotting import plot_forecast

import surffeedback, stormglass


def _compute_onshore(data: pd.DataFrame, richting: float, side_shore) -> pd.DataFrame:
    if side_shore:
        data = (data - richting + 360) % 360
    else:
        data = (data - richting + 90 + 360) % 360
    data = np.sin(data.values / 360 * 2 * np.pi)
    return copy(data)

def _enrich_input_data(data: pd.DataFrame, richting: float) -> pd.DataFrame:
    data['waveOnshore'] = _compute_onshore(data['waveDirection'], richting, side_shore=False)
    data['waveSideshore'] = _compute_onshore(data['waveDirection'], richting, side_shore=True)
    data = data.drop('waveDirection', axis=1)

    data['windOnshore'] = _compute_onshore(data['windDirection'], richting, side_shore=False)
    data['windSideshore'] = _compute_onshore(data['windDirection'], richting, side_shore=True)
    data = data.drop('windDirection', axis=1)

    data['seaRise'] = data["NAP"].diff()

    return data




@dataclass
class Spot:
    """
        All spot info and data in one class

    :param boei: Dichtstbijzijnde boei
    :param richting: Richting van het strand
    :name name: Name in the surf feedback form
    """
    # boei: Boei
    richting: float
    name: str
    lat: float
    long: float

    def feedback(self, only_spot_data):
        """Surf feedback form"""

        all = surffeedback.load(surffeedback.file_raw)
        if only_spot_data:
            return all[all["spot"].str.contains(self.name)==True]
        else:
            return all

    def _hindcast_input(self):
        """Surf historical statistics"""
        data = stormglass.load_data(self.lat, self.long)
        data = _enrich_input_data(data, self.richting)
        return data

    def combined(self, only_spot_data, non_zero_only=True, match_all_feedback_times=True, fb_columns: str=None):
        """Combined surf statistics and feedback form"""
        input = self._hindcast_input()
        output = self.feedback(only_spot_data=only_spot_data)
        data = deepcopy(input)
        if not fb_columns:
            fb_columns = output.forecast_columns
        data[fb_columns] = np.nan

        for index, row in output.iterrows():
            pattern = r'^\d{2}:\d{2}:\d{2}$'
            datum = row["Datum"]
            date_wrong_format = not re.match(pattern, str(row['Start tijd'])) or not re.match(pattern,
                                                                                              str(row['Start tijd']))
            if date_wrong_format:
                continue
            start_tijd = datetime.datetime.strptime(f"{datum} {row['Start tijd']}", "%d-%m-%Y %H:%M:%S")
            eind_tijd = datetime.datetime.strptime(f"{datum} {row['Eind tijd']}", "%d-%m-%Y %H:%M:%S")
            if not match_all_feedback_times:
                mid_tijd = start_tijd + ((eind_tijd - start_tijd) / 2)
                start_tijd = mid_tijd - datetime.timedelta(minutes=5)
                eind_tijd = mid_tijd + datetime.timedelta(minutes=5)
            start_tijd = start_tijd.strftime("%Y-%m-%d %H:%M:%S")
            eind_tijd = eind_tijd.strftime("%Y-%m-%d %H:%M:%S")
            query = (data.index >= start_tijd) & (data.index <= eind_tijd)
            # if all(query == False):
            #     continue
            data.loc[query, fb_columns] = row[fb_columns]
        if non_zero_only:
            return data[data[fb_columns].notnull()]
        else:
            return data

    def forecast(self, cache, hours=72, ):
        data = stormglass.forecast(self.lat, self.long, hours=hours, cache=cache)  # check: is N == lat?
        return data

    def predict_surf_perk(self, data, model: Model) -> pd.DataFrame:
        """Rate the surf forecast based on the trained model (file)"""

        data = _enrich_input_data(data, self.richting)
        result = model.model.predict(data)
        return result

    def surf_rating(self, models=MODELS, cache=False):
        data_init = self.forecast(cache)
        data = deepcopy(data_init)
        for model in models:
            data[model.perk] = self.predict_surf_perk(data_init, model)
        return data


# Add all spots here
ijmuiden = Spot(richting=290, name="ZV", lat=52.474773, long=4.535204)
scheveningen = Spot(richting=315, name="schev", lat=52.108703, long=4.267715)
camperduin = Spot(richting=270, name="camperduin", lat=52.723113, long=4.639215)
texel_paal17 = Spot(richting=305, name="texel17", lat=53.081695, long=4.733450)

spots = [ijmuiden, scheveningen, camperduin, texel_paal17]

if __name__ == '__main__':


    # Train models
    for model in MODELS:
        model.train(ijmuiden, channel=model.perk, only_spot_data=True, save=False)


    # Perks
    df = ijmuiden.surf_rating(cache=True)
    plot_forecast(df, ijmuiden, perks_plot=True)
    plot_forecast(df, ijmuiden)
    plt.show()



    # print(tabulate(df, df.columns))
    # mse = ijmuiden.train(only_spot_data=False, save=True)
    # model = ijmuiden.load_model()
    # xgb.plot_tree(model)
    # Plot tree
    # xgb.plot_tree(model)


    # print(tabulate(ijmuiden.feedback(only_spot_data=True), headers='keys', tablefmt='psql'))
    # data = ijmuiden.surf_rating(cache=True)
    # plot_forecast(data, ijmuiden)
    # plt.show()