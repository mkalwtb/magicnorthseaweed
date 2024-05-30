import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path
import numpy as np

class Boei:
    location_slug: str
    waterinfo_code: str
    donar_code: str
    knmi_code: str
    swan_code: str
    lon: float
    lat: float
    input_or_output: str
    def __init__(self, location_slug: str, waterinfo_code: str, donar_code: str, knmi_code: str, swan_code: str, lon: float, lat: float, input_or_output: str, seq_offset: str):
        self.location_slug: str = location_slug
        self.waterinfo_code: str = waterinfo_code
        self.donar_code: str = donar_code
        self.knmi_code: str = knmi_code
        self.swan_code: str = swan_code
        self.lon: float = lon
        self.lat: float = lat
        self.input_or_output: str = input_or_output
        self.seq_offset: str = seq_offset

ijmuiden = Boei(
                location_slug= "IJgeul-stroommeetpaal(SPY)",
                waterinfo_code = "SPY",
                donar_code = "IJMDSMPL",
                knmi_code = "IJmond",
                swan_code = "SPY",
                lon=4.517361,
                lat=52.463736,
                input_or_output = "output",
                seq_offset = False
                )

ijgeul = Boei(
                location_slug="IJgeul(IJGL)",
                waterinfo_code = "IJGL",
                donar_code = "IJMDN05",
                knmi_code = False,
                swan_code = "IJGL",
                lon=4.33293,
                lat=52.48144,
                input_or_output = "input",
                seq_offset = 3
                )

F3 = Boei(
                location_slug="F3-platform(F3)",
                waterinfo_code = "F3",
                donar_code = "F3PFM",
                knmi_code = 'platform F3 locatie FD2',
                swan_code = "F003",
                lon= 4.696111,
                lat= 54.853889,
                input_or_output = "input",
                seq_offset = 0
                )

D15 = Boei(
                location_slug="D15-platform(D15)",
                waterinfo_code = "D15",
                donar_code = False, #donar_code geeft geen informatie
                knmi_code = 'platform D15-FA-1 locatie DV', #'platform D15-FA-1 locatie DV1' 'platform D15-FA-1 locatie DV2',
                swan_code = "D151",
                lon= 2.935833,
                lat= 54.325556,
                input_or_output = "input",
                seq_offset = 0
                )

L9 = Boei(
                location_slug="L9-platform(L9)",
                waterinfo_code = "L9",
                donar_code = "L9PFM",
                knmi_code = 'platform L9-FF-1 locatie MG', #'platform L9-FF-1 locatie MG1' 'platform L9-FF-1 locatie MG2',
                swan_code = "L9",
                lon= 4.960278,
                lat= 53.614444,
                input_or_output = "input",
                seq_offset = 0
                )

eierlandse_gat = Boei(
                location_slug="Eierlandse-Gat-boei(ELD1)-1",
                waterinfo_code = "ELD1",
                donar_code = "EIELSGT",
                knmi_code = False,
                swan_code = "ELD",
                lon= 4.641966,
                lat= 53.285332,
                input_or_output = "input",
                seq_offset = 0
                )

munitiestort = Boei(
                location_slug="IJgeul-Munitiestort-1(MUN1)",
                waterinfo_code = "MUN1",
                donar_code = "IJMDMNTSPS",
                knmi_code = False,
                swan_code = "MUNS",
                lon=4.081380001,
                lat=52.55909,
                input_or_output = "input",
                seq_offset = 6 * 1
                )

maasvlakte = Boei(
                location_slug="Maasgeul-Maasvlakte-Noord(MMND)",
                waterinfo_code = "MMND",
                donar_code = "MAASMSMPL",
                knmi_code = False,
                swan_code = "MG04",
                lon=3.98961,
                lat=52.00401,
                input_or_output = "input",
                seq_offset = 0
                )

K13 = Boei(
                location_slug="K13-Alpha(K13)",
                waterinfo_code = "K13",
                donar_code = "K13APFM",
                knmi_code =  'platform K13 locatie 0', # 'platform K13 locatie 1' "platform K13 locatie 2"
                swan_code = "K13",
                lon=3.218932,
                lat=53.21701,
                input_or_output = "input",
                seq_offset = 6 * 4
                )

A12 = Boei(
                location_slug="A12-platform(A12)",
                waterinfo_code = "A12",
                donar_code = "A12",
                knmi_code = "platform A12-CPP locatie AK", #'platform A12-CPP locatie AK1' 'platform A12-CPP locatie AK2'
                swan_code = "A121",
                lon=3.816671,
                lat=55.416663,
                input_or_output = "input",
                seq_offset = 0
                )

EPL = Boei(
                location_slug="Europlatform(EPL)",
                waterinfo_code = "EPL",
                donar_code = "EURPFM",
                knmi_code = "Europlatform locatie 0", #'Europlatform locatie 1' 'Europlatform locatie 2'
                swan_code = "EUGL",
                lon=3.275075,
                lat=51.997801,
                input_or_output = "input",
                seq_offset = 6 * 3
                )

K14 = Boei(
                location_slug="K14-platform(K14)",
                waterinfo_code = "K14",
                donar_code = "K14PFM",
                knmi_code = "platform K14-FA-1C locatie KV", #'platform K14-FA-1C locatie KV1' 'platform K14-FA-1C locatie KV2'
                swan_code = False,
                lon=3.63333,
                lat=53.26667,
                input_or_output = "input",
                seq_offset = 0
                )

eurogeul_dwe = Boei(
                location_slug="Eurogeul-DWE(DWE1)",
                waterinfo_code = "DWE1",
                donar_code = "EURGDWE",
                knmi_code = False,
                swan_code = "DWE",
                lon=2.99896,
                lat=51.94752,
                input_or_output = "input",
                seq_offset = 0
                )

P11 = Boei(
                location_slug = "P11-platform(P11)",
                waterinfo_code = "P11",
                donar_code = False,
                knmi_code = "platform P11-B locatie PG", #'platform P11-B locatie PG1'
                swan_code = False,
                lon =3.341500001,
                lat =52.35867,
                input_or_output = "input",
                seq_offset = 0
                )

J6 = Boei(
                location_slug = "J6-platform(J6)",
                waterinfo_code = "J6",
                donar_code = "J6",
                knmi_code = "platform J6-A locatie JA", #'platform J6-A locatie JA1' 'platform J6-A locatie JA2'
                swan_code = "J61",
                lon =2.950010001,
                lat =53.816632,
                input_or_output = "input",
                seq_offset = 0
                )

brent_charlie_platform = Boei(
                location_slug="Brent-Charlie-Platform(BTC1)",
                waterinfo_code = "BTC1",
                donar_code = "BRENTCLE",
                knmi_code = False,
                swan_code = False,
                lon=1.721389999,
                lat=61.09611,
                input_or_output = "input",
                seq_offset = 0
                )

gannet_platform = Boei(
                location_slug="Gannet-platform-1(GAN1)",
                waterinfo_code = "GAN1",
                donar_code = False,
                knmi_code = False,
                swan_code = False,
                lon=1,
                lat=57.18503,
                input_or_output = "input",
                seq_offset = 0
                )

nelson_platform = Boei(
                location_slug="Nelson-platform1(NLS1)",
                waterinfo_code = "NLS1",
                donar_code = False,
                knmi_code = False,
                swan_code = False,
                lon=1.144999999,
                lat=57.66169,
                input_or_output = "input",
                seq_offset = 0
                )

north_cormorant = Boei(
                location_slug="North-Cormorant(NC1)",
                waterinfo_code = "NC1",
                donar_code = "NORTHCMRT",
                knmi_code = False,
                swan_code = False,
                lon=1.166098999,
                lat=61.338188,
                input_or_output = "input",
                seq_offset = 0
                )

boeien = [ijmuiden]
#boeien = [ijmuiden, ijgeul, munitiestort, P11, eierlandse_gat, EPL, K14, eurogeul_dwe, K13, L9, J6, F3, D15, A12, gannet_platform, nelson_platform, brent_charlie_platform, north_cormorant]