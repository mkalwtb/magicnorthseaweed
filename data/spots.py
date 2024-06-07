import pandas as pd
import numpy as np
from copy import deepcopy, copy
import datetime
import re
from dataclasses import dataclass, fields
from matplotlib import pyplot as plt
import xgboost as xgb
from suntime import Sun

from models import Model, MODELS
from plotting import plot_forecast

import surffeedback, stormglass


def shelter_from_series(signal_richting, spot):
    # Add shelter
    angle_wind = compute_angle(signal_richting, spot.richting+90)
    if spot.spot_info.pier == -1:
        return angle_wind.apply(compute_shelter)
    elif spot.spot_info.pier == 0:
        return 0
    elif spot.spot_info.pier == 1:
        return (-angle_wind).apply(compute_shelter)
    else:
        raise NotImplementedError("Pier not implemented")

def compute_shelter(shelter_angle):
    if 0 <= shelter_angle <= 20 or 160 <= shelter_angle <= 180:
        # Linear increase from 0 to 0.4 and then decrease back
        return 0.4 / 20 * min(shelter_angle, 180 - shelter_angle)
    elif 20 < shelter_angle < 160:
        # Linear increase from 0.4 to 0.7 up to 90°, then decrease back to 0.4
        if shelter_angle <= 90:
            return 0.4 + (0.7 - 0.4) / (90 - 20) * (shelter_angle - 20)
        else:
            return 0.4 + (0.7 - 0.4) / (90 - 20) * (160 - shelter_angle)
    else:
        # Zero reduction factor beyond 180°
        return 0


def compute_angle(data: pd.DataFrame, richting: float):
    return (data - richting + 360) % 360


def _compute_onshore(data: pd.DataFrame, richting: float, side_shore) -> pd.DataFrame:
    if side_shore:
        angle = compute_angle(data, richting)
    else:
        angle = compute_angle(data, richting + 90)
    data = np.sin(angle.values / 360 * 2 * np.pi)
    return copy(data)

def enrich_input_data(data: pd.DataFrame, spot) -> pd.DataFrame:
    spot.add_spot_info(data)
    data['waveOnshore'] = _compute_onshore(data['waveDirection'], spot.richting, side_shore=False)
    data['waveSideshore'] = _compute_onshore(data['waveDirection'], spot.richting, side_shore=True)
    # data = data.drop('waveDirection', axis=1)

    data['windOnshore'] = _compute_onshore(data['windDirection'], spot.richting, side_shore=False)
    data['windSideshore'] = _compute_onshore(data['windDirection'], spot.richting, side_shore=True)
    data["windMagOnShore"] = data['windOnshore'] * data["windSpeed"]
    data["windMagSideShore"] = data['windSideshore'] * data["windSpeed"]
    # data = data.drop('windDirection', axis=1)

    data["shelterWind"] = shelter_from_series(data["windDirection"], spot)

    # data["windMagOnShoreShelter"] = data["windMagOnShore"] * data["shelter"]
    # data["windMagSideShoreShelter"] = data["windMagSideShore"] * data["shelter"]

    data["waveEnergy"] = data["waveHeight"]**2 * data["wavePeriod"]**2 * data["waveOnshore"]
    data.loc[data['waveEnergy'] < 0, 'waveEnergy'] = 0

    # data['waveOnshore2nd'] = _compute_onshore(data['secondarySwellDirection'], richting, side_shore=False)
    # data["waveEnergy2nd"] = data["secondarySwellHeight"]**2 * data["secondarySwellPeriod"]**2 * data["waveOnshore2nd"]
    # data.loc[data['waveEnergy2nd'] < 0, 'waveEnergy2nd'] = 0
    data["windWaveHeight2"] = data["windWaveHeight"]**2  # todo use the code above: Tis is wrong and temp

    data['seaRise'] = data["NAP"].diff()

    return data


@dataclass
class SpotInfo:
    pier: int


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
    db_name: str
    spot_info: SpotInfo

    def feedback(self, only_spot_data):
        """Surf feedback form"""

        all = surffeedback.load(surffeedback.file_raw)
        if only_spot_data:
            return all[all["spot"].str.contains(self.name) == True]
        else:
            return all

    def _hindcast_input(self):
        """Surf historical statistics"""
        data = stormglass.load_data(self.db_name)
        data = enrich_input_data(data, self)
        return data

    @staticmethod
    def _pims_hindcast_input():
        return pd.read_pickle(r"RWS/test.pkl")

    def combined(self, only_spot_data, non_zero_only=True, match_all_feedback_times=True, fb_columns: str=None, pim=False):
        """Combined surf statistics and feedback form"""
        if pim:
            input = self._pims_hindcast_input()
        else:
            input = self._hindcast_input()
        output = self.feedback(only_spot_data=only_spot_data)
        data = deepcopy(input)
        self.add_spot_info(data)

        if not fb_columns:
            fb_columns = output.columns
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

    def forecast(self, cache, hours=24*7, ):
        data = stormglass.forecast(self.lat, self.long, hours=hours, cache=cache)  # check: is N == lat?
        return data

    def predict_surf_perk(self, data, model: Model) -> pd.DataFrame:
        """Rate the surf forecast based on the trained model (file)"""

        data = enrich_input_data(data, self)
        data = data[model.channels]
        result = model.model.predict(data)
        return result

    def surf_rating(self, models=MODELS, cache=False):
        data_init = self.forecast(cache)

        data = deepcopy(data_init)
        for model in models:
            data[model.perk] = self.predict_surf_perk(data_init, model)
        return data

    def add_spot_info(self, data):
        # Add pier data
        for field in fields(self.spot_info):
            value = getattr(self.spot_info, field.name)
            data[field.name] = value


strand = SpotInfo(pier=0)
pier_links = SpotInfo(pier=-1)
pier_rechts = SpotInfo(pier=1)

# Add all spots here
ZV = Spot(richting=290, name="ZV", lat=52.474773, long=4.535204, db_name="ZV", spot_info=strand)
scheveningen = Spot(richting=315, name="Schev", lat=52.108703, long=4.267715, db_name="ZV", spot_info=strand)
camperduin = Spot(richting=270, name="Camperduin", lat=52.723113, long=4.639215, db_name="ZV", spot_info=strand)
texel_paal17 = Spot(richting=305, name="Texel17", lat=53.081695, long=4.733450, db_name="ZV", spot_info=strand)

wijk = Spot(richting=295, name="Wijk", lat=53.081695, long=4.733450, db_name="ZV", spot_info=pier_links)  # todo set lat, long, en richting
ijmuiden = Spot(richting=260, name="Ijmuiden", lat=53.081695, long=4.733450, db_name="ZV", spot_info=pier_rechts)  # todo set lat, long, en richting
Wadduwa = Spot(richting=240, name="Wadduwa", lat=6.625524189426171, long=79.93779864874834, db_name="ZV", spot_info=strand)
Lavinia = Spot(richting=265, name="Lavinia", lat=6.848208867737467, long=79.85826985402555, db_name="ZV", spot_info=strand)

# spots = [ijmuiden, scheveningen, camperduin, texel_paal17]
spots = [wijk, ZV, ijmuiden, camperduin, scheveningen, texel_paal17, Wadduwa, Lavinia]

if __name__ == '__main__':
    # Train models
    attenpts = 50
    rating = MODELS[0]
    # rating.train_best(spots, perk=rating.perk, channels=rating.channels, save=True, verbose=True, attempts=attenpts)
    for model in MODELS:
        model.train_best(spots, perk=model.perk, channels=model.channels, save=True, attempts=attenpts)


    spot = ZV
    df = spot.surf_rating(cache=True)
    plot_forecast(df, spot, perks_plot=True)

    # df = ZV.surf_rating(cache=True)
    # plot_forecast(df, ZV, perks_plot=True)
    #
    # df = ijmuiden.surf_rating(cache=True)
    # plot_forecast(df, ijmuiden, perks_plot=True)
    plt.show()

    rating.plot_model()



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