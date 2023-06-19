from dataclasses import dataclass
from typing import List

time_48h48h = "-48,48"
# Link: https://waterinfo.rws.nl/#!/kaart/wind/

@dataclass
class BoeiData:
    name: str
    col_past: str
    col_future: str
    parameter: str
    locoation_slug: str
    time_horizon: str
    # url: str

    @property
    def url(self):
        return f"https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter={self.parameter}&locationSlug={self.locoation_slug}&timehorizon={self.time_horizon}"

@dataclass
class Boei:
    data: List[BoeiData]
    locationSlug: str


ijmuiden = Boei(data=
                [BoeiData(name="Hs",
                          col_past="Waarde",
                          col_future="Verwachting",
                          parameter="Significante___20golfhoogte___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20cm",
                          locoation_slug="IJgeul(IJGL)",
                          time_horizon=time_48h48h),
                 BoeiData(name="v0",
                          col_past="Waarde",
                          col_future="Verwachting",
                          parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                          locoation_slug="IJmuiden-Buitenhaven(IJMH)",
                          time_horizon=time_48h48h),
                BoeiData(name="v_dir",
                         col_past="Windrichting",
                         col_future="None",
                         parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                         locoation_slug="IJmuiden-Buitenhaven(IJMH)",
                         time_horizon=time_48h48h),
                # BoeiData(name="water_hoogte",
                #          col_past="Waarde",
                #          col_future="None",
                #          parameter="Waterhoogte___20berekend___20Oppervlaktewater___20t.o.v.___20Normaal___20Amsterdams___20Peil___20in___20cm",
                #          locoation_slug="IJmuiden-stroommeetpaal(IJMDSMPL)",
                #          time_horizon=time_48h48h),
                ],
                locationSlug="IJmuiden-Buitenhaven(IJMH)")