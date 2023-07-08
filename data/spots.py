import pandas as pd
import numpy as np
from copy import deepcopy

from dataclasses import dataclass
import boeien, surffeedback
from rijkswaterstaat import Boei

@dataclass
class Spot:
    '''
    All spot info and data in one class

    :param boei: Dichtstbijzijnde boei
    :param richting: Richting van het strand
    '''
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
        input = self.boei.data
        output = self.feedback(only_spot_data=only_spot_data)
        data = deepcopy(input)
        data[columns] = np.nan

        for index, row in output.iterrows():
            datum = row["Datum"]
            start_tijd = f"{datum} {row['Start tijd']}"
            eind_tijd = f"{datum} {row['Eind tijd']}"
            query = (data.index >= start_tijd) & (data.index <= eind_tijd)
            if all(query == False):
                continue
            data.loc[query, columns] =  row[columns]
        if non_zero_only:
            return data[data["rating"].notnull()]
        else:
            return data


# Add all spots here
ijmuiden = Spot(boei=boeien.ijmuiden, richting=290, name="ZV Parnassia")


if __name__ == '__main__':
    data = ijmuiden.input_output_data(only_spot_data=False, non_zero_only=True)
    print(data)