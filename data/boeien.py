import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path
from rijkswaterstaat import Boei, BoeiData

"""
Om de boei data op te zoeken:
1. Ga naar https://waterinfo.rws.nl/#!/details/publiek/waterhoogte/
2. Selecteer de boei & data die je wil
3. click Export/Delen
4. Right click op CSV
5. copy link adress
6. Extract de parameter=... en location_slug=... en time_horizon=...
7. Indien nodig, open de csv file en kijk hoe de colom heet. Normaal is dit Waarde
"""

time_48h48h = "-48,48"
time_48h0h = "-48,0"
time_28d = "-672,0"
timing = time_28d

ijmuiden = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                        parameter="Significante___20golfhoogte___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20cm",
                        locoation_slug="IJgeul(IJGL)",
                        col_future="Verwachting"),
                    BoeiData(name="wave-period",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s&locationSlug=IJgeul-stroommeetpaal(SPY)&timehorizon=-672,0                          col_past="Waarde",
                          parameter="Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s",
                          locoation_slug="IJgeul-stroommeetpaal(SPY)"),
                    BoeiData(name="wind-speed",
                          parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                          locoation_slug="IJmuiden-Buitenhaven(IJMH)",
                          col_future="Verwachting"),
                    BoeiData(name="wind-dir",
                          parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                          locoation_slug="IJmuiden-Buitenhaven(IJMH)",
                          col_past="Windrichting"),
                    BoeiData(name="tide-height",
                          parameter="Waterhoogte___20Oppervlaktewater___20t.o.v.___20Normaal___20Amsterdams___20Peil___20in___20cm",
                          locoation_slug="IJmuiden-Buitenhaven(IJMH)",
                          col_future="Verwachting"),
                    BoeiData(name="wave-dir", # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad&locationSlug=IJgeul-Munitiestort-1(MUN1)&timehorizon=-48,0
                          parameter="Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad",
                          locoation_slug="IJgeul-Munitiestort-1(MUN1)",
                          future_unavailable=True)
                ],
                location_slug="IJmuiden-Buitenhaven(IJMH)",
                N=52.474773,
                E=4.535204)

K13 = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                        parameter="Significante___20golfhoogte___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20cm",
                        locoation_slug="K13-Alpha(K13)",
                        col_future="Verwachting"),
                    BoeiData(name="wave-period",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s&locationSlug=IJgeul-stroommeetpaal(SPY)&timehorizon=-672,0                          col_past="Waarde",
                          parameter="Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s",
                          locoation_slug="K13-Alpha(K13)"),
                    BoeiData(name="wind-speed",
                          parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                          locoation_slug="K13-Alpha(K13)",
                          col_future="Verwachting"),
                    BoeiData(name="wave-dir",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad&locationSlug=IJgeul-Munitiestort-1(MUN1)&timehorizon=-48,0
                             parameter="Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad",
                             locoation_slug="K13-Alpha(K13)",
                             future_unavailable=True)
                ],
                location_slug="K13-Alpha(K13)",
                N=53.586792,
                E=3.075473)

boeien = [ijmuiden, K13]

