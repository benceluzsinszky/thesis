import pandas as pd
import json
import os


def write_to_csv(data: pd.DataFrame, endpoint: str) -> None:
    file_name = f"{endpoint}.csv"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, "..", "results")
    path = os.path.join(results_dir, file_name)
    file_exists = os.path.isfile(path)
    data.to_csv(path, mode="a", header=not file_exists, index=False)


def load_config_file(path: str) -> dict:
    with open(path) as config_file:
        return json.load(config_file)
