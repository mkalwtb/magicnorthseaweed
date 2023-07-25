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
                             location_slug="IJgeul(IJGL)",
                             col_future="Verwachting"),
                    BoeiData(name="wave-period",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s&locationSlug=IJgeul-stroommeetpaal(SPY)&timehorizon=-672,0                          col_past="Waarde",
                             parameter="Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s",
                             location_slug="IJgeul-stroommeetpaal(SPY)"),
                    BoeiData(name="wind-speed",
                             parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                             location_slug="IJmuiden-Buitenhaven(IJMH)",
                             col_future="Verwachting"),
                    BoeiData(name="wind-dir",
                             parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                             location_slug="IJmuiden-Buitenhaven(IJMH)",
                             col_past="Windrichting"),
                    BoeiData(name="tide-height",
                             parameter="Waterhoogte___20Oppervlaktewater___20t.o.v.___20Normaal___20Amsterdams___20Peil___20in___20cm",
                             location_slug="IJmuiden-Buitenhaven(IJMH)",
                             col_future="Verwachting"),
                    BoeiData(name="wave-dir",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad&locationSlug=IJgeul-Munitiestort-1(MUN1)&timehorizon=-48,0
                             parameter="Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad",
                             location_slug="IJgeul-Munitiestort-1(MUN1)",
                             future_unavailable=True)
                ],
                location_slug="IJmuiden-Buitenhaven(IJMH)",
                N=52.474773,
                E=4.535204)

K13 = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                             parameter="Gem.___20hoogte___20van___20hoogste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20cm",
                             location_slug="K13-Alpha(K13)",
                             col_future="Verwachting"),
                    BoeiData(name="wave-period",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s&locationSlug=IJgeul-stroommeetpaal(SPY)&timehorizon=-672,0                          col_past="Waarde",
                             parameter="Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s",
                             location_slug="K13-Alpha(K13)"),
                    BoeiData(name="wind-speed",
                             parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                             location_slug="K13-Alpha(K13)",
                             col_future="Verwachting"),
                    BoeiData(name="wave-dir",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad&locationSlug=IJgeul-Munitiestort-1(MUN1)&timehorizon=-48,0
                             parameter="Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad",
                             location_slug="K13-Alpha(K13)",
                             future_unavailable=True)
                ],
                location_slug="K13-Alpha(K13)",
                N=53.586792,
                E=3.075473)

A12 = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                             parameter="Gem.___20hoogte___20van___20hoogste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20cm",
                             location_slug="A12-platform(A12)",
                             col_future="Verwachting"),
                    BoeiData(name="wave-period",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s&locationSlug=IJgeul-stroommeetpaal(SPY)&timehorizon=-672,0                          col_past="Waarde",
                             parameter="Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s",
                             location_slug="A12-platform(A12)"),
                    BoeiData(name="wind-speed",
                             parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                             location_slug="A12-platform(A12)",
                             col_future="Verwachting"),
                    BoeiData(name="wave-dir",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad&locationSlug=IJgeul-Munitiestort-1(MUN1)&timehorizon=-48,0
                             parameter="Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad",
                             location_slug="A12-platform(A12)",
                             future_unavailable=True)
                ],
                location_slug="A12-platform(A12)",
                N=55.108640,
                E=3.738921)


EPL = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                             parameter="Gem.___20hoogte___20van___20hoogste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20cm",
                             location_slug="Europlatform(EPL)",
                             col_future="Verwachting"),
                    BoeiData(name="wave-period",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Golfperiode___20bepaald___20uit___20de___20spectrale___20momenten___20m0___20en___20m2___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20s&locationSlug=IJgeul-stroommeetpaal(SPY)&timehorizon=-672,0                          col_past="Waarde",
                             parameter="Gem.___20golfperiode___20langste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20s",
                             location_slug="Europlatform(EPL)"),
                    BoeiData(name="wind-speed",
                             parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                             location_slug="Europlatform(EPL)",
                             col_future="Verwachting"),
                    BoeiData(name="wave-dir",  # https://waterinfo.rws.nl/api/CsvDownload/CSV?expertParameter=Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad&locationSlug=IJgeul-Munitiestort-1(MUN1)&timehorizon=-48,0
                             parameter="Gemiddelde___20golfrichting___20in___20het___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20500___20mHz___20in___20graad",
                             location_slug="Europlatform(EPL)",
                             future_unavailable=True)
                ],
                location_slug="Europlatform(EPL)",
                N=55.108640,
                E=3.738921)

K14 = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                        parameter="Gem.___20hoogte___20van___20hoogste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20cm",
                        location_slug="K14-platform(K14)",
                        col_future="Verwachting"),
                    BoeiData(name="wave-period",
                          parameter="Gem.___20golfperiode___20langste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20s",
                          location_slug="K14-platform(K14)"),
                    BoeiData(name="wind-speed",
                          parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                          location_slug="K14-platform(K14)",
                          col_future="Verwachting"),
                    BoeiData(name="wind-dir",
                             parameter="Windrichting___20Lucht___20t.o.v.___20ware___20Noorden___20in___20graad",
                             location_slug="K14-platform(K14)",
                             col_past="Windrichting")
                    #wave direction niet beschikbaar
                ],
                location_slug="K14-platform(K14)",
                # EPSG=25831,
                N=542240.426,
                E=5902123.137)

ijgeul_munitiestort = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                        parameter="Gem.___20hoogte___20van___20hoogste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20cm",
                        location_slug="IJgeul-Munitiestort-2(MUN2)",
                        col_future="Verwachting"),
                    BoeiData(name="wave-period",
                          parameter="Gem.___20golfperiode___20langste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20s",
                          location_slug="IJgeul-Munitiestort-2(MUN2)"),
                    BoeiData(name="wave-dir",
                          parameter="Gem.___20richting___20deining___20tov___20ware___20noorden___20in___20spectrale___20domein___20Oppervlaktewater___20golffrequentie___20tussen___2030___20en___20100___20mHz___20in___20graad",
                          location_slug="IJgeul-Munitiestort-1(MUN1)",
                          future_unavailable=True)
                    #winddir & windpeed niet beschikbaar
                ],
                location_slug="IJgeul-Munitiestort-2(MUN2)",
                # EPSG=25831,
                N=573307.8064,
                E=5823774.056)

eurogeul_dwe = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                        parameter="Gem.___20hoogte___20van___20hoogste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20cm",
                        location_slug="Eurogeul-DWE(DWE1)",
                        col_future="Verwachting"),
                    BoeiData(name="wave-period",
                        parameter="Gem.___20golfperiode___20langste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20s",
                        location_slug="Eurogeul-DWE(DWE1)")
                    #wavedir, winddir & windspeed niet beschikbaar
                ],
                location_slug="Eurogeul-DWE(DWE1)",
                # EPSG=25831,
                N=499928.52,
                E=5755201.264)

P11 = Boei(parameters=
                [
                    BoeiData(name="wind-speed",
                        parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                        location_slug="P11-platform(P11)",
                        col_future="Verwachting"),
                    BoeiData(name="wind-dir",
                        parameter="Windrichting___20Lucht___20t.o.v.___20ware___20Noorden___20in___20graad",
                        location_slug="P11-platform(P11)",
                        col_past="Windrichting"),
                    #waveheight, period & wavedir niet beschikbaar
                ],
                location_slug = "P11-platform(P11)",
                # EPSG=25831,
                N =523256.2982,
                E =5800986.612)

J6 = Boei(parameters=
                [
                    BoeiData(name="wave-height",
                        parameter="Gem.___20hoogte___20van___20hoogste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20cm",
                        location_slug="J6-platform(J6)",
                        col_future="Verwachting"),
                    BoeiData(name="wave-period",
                          parameter="Gem.___20golfperiode___20langste___201___2F3___20deel___20v.d.___20golven___20___28tijdsdomein___29___20Oppervlaktewater___20s",
                          location_slug="J6-platform(J6)"),
                    BoeiData(name="wind-speed",
                        parameter="Windsnelheid___20Lucht___20t.o.v.___20Mean___20Sea___20Level___20in___20m___2Fs",
                        location_slug="J6-platform(J6)",
                        col_future="Verwachting"),
                    BoeiData(name="wind-dir",
                        parameter="Windrichting___20Lucht___20t.o.v.___20ware___20Noorden___20in___20graad",
                        location_slug="J6-platform(J6)",
                        col_past="Windrichting"),
                    #wavedir niet beschikbaar
                ],
                location_slug = "J6-platform(J6)",
                # EPSG=25831,
                N =496708.7948,
                E =5963121.522)

boeien = [ijmuiden, K13, A12, EPL, K14, eurogeul_dwe, P11, J6]

