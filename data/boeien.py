from matplotlib import pyplot as plt
from pathlib import Path
from rijkswaterstaat import Boei, BoeiData

time_48h48h = "-48,48"
# Link: https://waterinfo.rws.nl/#!/kaart/wind/

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

if __name__ == '__main__':
    df = ijmuiden.download()
    print(df)
    # print(tabulate(df, headers=df.columns))
    df.plot(subplots=True)
    df.to_csv(r"example\test_data.csv")
    plt.show()