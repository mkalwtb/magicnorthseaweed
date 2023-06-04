import pandas as pd
from pathlib import Path


def read_data(file: Path):
    return pd.read_csv(file, sep=";", parse_dates={"Datetime": [0, 1]}, dayfirst=True)

if __name__ == '__main__':
    file = Path(r"example\NVT_Hm0_IJGL.csv")
    Hs = read_data(file)
    print(Hs.iloc[0])