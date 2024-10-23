import pandas as pd
from datetime import datetime
import json


def write_to_csv(data: pd.DataFrame):
    file_name = datetime.now().strftime("%Y%m%d_%H%M%S.csv")
    data.to_csv(f"../results/{file_name}", index=False)


def load_config_file(path: str) -> dict:
    with open(path) as config_file:
        return json.load(config_file)
