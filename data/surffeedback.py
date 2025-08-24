import pandas as pd
from pathlib import Path

from tabulate import tabulate

file_raw = Path(r"surf-feedback-raw/Surf-feedback.csv")
file_pkl = file_raw.with_suffix(".pkl")

column_names = {
    "clean": "Hoe was de surf? Alleen invullen bij een nat pak (: [Clean]",
    "krachtig": "Hoe was de surf? Alleen invullen bij een nat pak (: [Krachtig]",
    "lange-ritjes": "Hoe was de surf? Alleen invullen bij een nat pak (: [Lange ritjes]",
    "stijl": "Hoe was de surf? Alleen invullen bij een nat pak (: [Stijle golven]",
    "stroming": "Hoe was de surf? Alleen invullen bij een nat pak (: [Stroming]",
    "crowd": "Hoe was de surf? Alleen invullen bij een nat pak (: [Crowd]",
    "hoog": "Hoe was de surf? Alleen invullen bij een nat pak (: [Hoog]",
    "windy": "Hoe was de surf? Alleen invullen bij een nat pak (: [Windy]",
    "rating": "Hoe goed was de surf?",
    "spot": "Spot",
    "hoogte-v2": "Hoe hoog was het?",

}

colums_delete = ["Hoe was de surf? Alleen invullen bij een nat pak (: [Mellow]", "E-mailadres"]

column_names_swapped = dict((v, k) for k,v in column_names.items())
hoeveelheden = ["Helemaal niet", "Een beetje", "Best wel", "Heel erg"]

hoeveelheden_hoogtev2 = ["Flat", "Knie-hoog", "Heup-hoog", "Navel-hoog", "Borst-hoog", "Schouder-hoog", "Head-hoog", "Overhead"]
hoeveelheden_hoogtev2_view = ["flat", "knie", "heup", "navel", "borst", "schouder", "head", "overhead"]

def rename_columns(columns):
    columns = list(columns)
    for i, column in enumerate(columns):
        if column in column_names.values():
            columns[i] = column_names_swapped[column]
    return columns

def text_to_value(data: pd.DataFrame) -> pd.DataFrame:
    for waarde, text in enumerate(hoeveelheden):
        data = data.replace(to_replace=text, value=waarde)
    for waarde, text in enumerate(hoeveelheden_hoogtev2):
        data = data.replace(to_replace=text, value=waarde)
    return data

def load(file_name):
    data = pd.read_csv(file_name)
    data.columns = rename_columns(data.columns)
    data = text_to_value(data)
    data = data.drop(colums_delete, axis=1)
    return data


# def convert_csv_to_pickle():
#     data = load(file_raw)
#     data.to_pickle(file_pkl)

if __name__ == '__main__':
    data = load(file_raw)
    print(tabulate(data))
    data.to_pickle(file_pkl)