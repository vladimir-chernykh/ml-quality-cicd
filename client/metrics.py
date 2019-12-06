import os

import pandas as pd


def answers_enricher(folder):

    path = os.path.join(folder, "parsed_answers.csv")

    parsed_answers = pd.read_csv(path)
    parsed_answers = parsed_answers.sort_values(by=["path", "row_number"]).reset_index(drop=True)

    parsed_answers["gt"] = None

    # try to append correct answers to the parsed answers
    for file in parsed_answers["path"].drop_duplicates().values:
        file_data = pd.read_csv(file)
        if "MEDV" in file_data.columns:
            parsed_answers.loc[parsed_answers["path"] == file, "gt"] = file_data["MEDV"].values

    parsed_answers.to_csv(path, index=False)

    return parsed_answers


def compute_metrics(folder):

    path = os.path.join(folder, "parsed_answers.csv")

    parsed_answers = pd.read_csv(path)
    parsed_answers = parsed_answers.sort_values(by=["path", "row_number"]).reset_index(drop=True)

    parsed_answers["mae"] = abs(parsed_answers["gt"] - parsed_answers["prediction"])
    parsed_answers["mse"] = (parsed_answers["gt"] - parsed_answers["prediction"]) ** 2
    parsed_answers["mape"] = parsed_answers["mae"] / parsed_answers["gt"]

    parsed_answers.to_csv(path, index=False)

    metrics_by_file = parsed_answers.groupby("path")[["mae", "mse", "mape"]].mean()
    metrics_by_file.to_csv(os.path.join(folder, "metrics_by_file.csv"))

    return parsed_answers
