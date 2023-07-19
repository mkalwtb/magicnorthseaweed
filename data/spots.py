import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime
import re

from dataclasses import dataclass
import boeien, surffeedback
from rijkswaterstaat import Boei

@dataclass
class Spot:
    """
    All spot info and data in one class

    :param boei: Dichtstbijzijnde boei
    :param richting: Richting van het strand
    :name name: Name in the surf feedback form
    """
    boei: Boei
    richting: float
    name: str

    def feedback(self, only_spot_data):
        all = pd.read_pickle(surffeedback.file_pkl)
        if only_spot_data:
            return all.query(f"spot == '{self.name}'")
        else:
            return all

    def input_output_data(self, only_spot_data, non_zero_only=False):
        columns = "rating"
        input = self.data()
        output = self.feedback(only_spot_data=only_spot_data)
        data = deepcopy(input)
        data[columns] = np.nan

        for index, row in output.iterrows():
            pattern = r'^\d{2}:\d{2}:\d{2}$'
            datum = row["Datum"]
            date_wrong_format = not re.match(pattern, str(row['Start tijd'])) or not re.match(pattern, str(row['Start tijd']))
            if date_wrong_format:
                continue
            start_tijd = datetime.strptime(f"{datum} {row['Start tijd']}", "%d-%m-%Y %H:%M:%S")
            start_tijd = start_tijd.strftime("%Y-%m-%d %H:%M:%S")
            eind_tijd = datetime.strptime(f"{datum} {row['Eind tijd']}", "%d-%m-%Y %H:%M:%S")
            eind_tijd = eind_tijd.strftime("%Y-%m-%d %H:%M:%S")
            query = (data.index >= start_tijd) & (data.index <= eind_tijd)
            # print(f"start={start_tijd}, \teind={eind_tijd}, \taantal={sum(query)}")
            # if all(query == False):
            #     continue
            data.loc[query, columns] =  row[columns]
        if non_zero_only:
            return data[data["rating"].notnull()]
        else:
            return data

    def data(self):
        data = self.boei.data
        data['wave-dir'] = (data['wave-dir'] - self.richting + 360) % 360
        data['onshore-wave'] = np.sin(data['wave-dir'].values/360*2*np.pi)
        data = data.drop('wave-dir', axis=1)

        data['wind-dir'] = (data['wind-dir'] - self.richting + 360) % 360
        data['onshore-wind'] = np.sin(data['wind-dir'].values/360*2*np.pi)
        data = data.drop('wind-dir', axis=1)
        return data


# Add all spots here
ijmuiden = Spot(boei=boeien.ijmuiden, richting=290, name="ZV Parnassia")


if __name__ == '__main__':
    data = ijmuiden.input_output_data(only_spot_data=False, non_zero_only=True)
    print(data)