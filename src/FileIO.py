import pandas as pd
from datetime import datetime
import json
import os


def write_to_csv(data: pd.DataFrame, path: str | None = None) -> None:
    if path is None:
        file_name = datetime.now().strftime("%Y%m%d_%H%M%S.csv")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(base_dir, "..", "results")
        path = os.path.join(results_dir, file_name)

    data.to_csv(path, index=False)


def load_config_file(path: str) -> dict:
    with open(path) as config_file:
        return json.load(config_file)
