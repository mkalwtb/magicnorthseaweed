import pandas as pd
from pathlib import Path

file = r"surf-feedback-raw/Surf-feedback-08-07-2023v3.csv"

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
    "spot": "Spot"
}

colums_delete = ["Hoe was de surf? Alleen invullen bij een nat pak (: [Mellow]", "E-mailadres"]

column_names_swapped = dict((v, k) for k,v in column_names.items())
hoeveelheden = ["Helemaal niet", "Een beetje", "Best wel", "Helemaal"]


def rename_columns(columns):
    columns = list(columns)
    for i, column in enumerate(columns):
        if column in column_names.values():
            columns[i] = column_names_swapped[column]
    return columns

def text_to_value(data: pd.DataFrame) -> pd.DataFrame:
    for waarde, text in enumerate(hoeveelheden):
        data = data.replace(to_replace=text, value=waarde)
    return data

def load(file_name):
    data = pd.read_csv(file)
    data.columns = rename_columns(data.columns)
    data = text_to_value(data)
    data = data.drop(colums_delete, axis=1)
    return data


if __name__ == '__main__':
    data = load(file)
    print(data)
    data.to_pickle(file.with_suffix(".pkl"))