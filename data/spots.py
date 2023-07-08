import pandas as pd
from dataclasses import dataclass
import boeien, surffeedback
from rijkswaterstaat import Boei

@dataclass
class Spot:
    boei_dichtbij: Boei
    richting: float
    name: str

    def feedback(self):
        all = pd.read_pickle(surffeedback.file)
        return all.query(f"spot == {self.name}")


ijmuiden = Spot(boeien.ijmuiden, 290, "ZV Parnassia")

if __name__ == '__main__':
    print(ijmuiden.feedback())