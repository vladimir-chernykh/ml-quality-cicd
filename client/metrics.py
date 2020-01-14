import os

import numpy as np
import pandas as pd


def answers_enricher(folder) -> pd.DataFrame:
    """ Adds ground truth values to the answers of the endpoint.

    Args:
        folder (str): path to the folder which contains 'parsed_answers.csv' file
                      with parsed endpoint predictions.

    Return:
        Parsed answers with ground truth values appended. The file is also saved to disc.
    """

    # read data
    path = os.path.join(folder, "parsed_answers.csv")

    parsed_answers = pd.read_csv(path)
    parsed_answers = parsed_answers.sort_values(by=["path", "row_number"]).reset_index(drop=True)

    parsed_answers["gt"] = None

    # try to append correct answers to the parsed answers
    for file in parsed_answers["path"].drop_duplicates().values:
        file_data = pd.read_csv(file)
        if "MEDV" in file_data.columns:
            parsed_answers.loc[parsed_answers["path"] == file, "gt"] = file_data["MEDV"].values

    # save data
    parsed_answers.to_csv(path, index=False)

    return parsed_answers


def compute_metrics(folder) -> pd.DataFrame:
    """ Compute instance-wise and global metrics for the predictions.

    Args:
        folder (str): path to the folder which contains 'parsed_answers.csv' file
                      with parsed endpoint predictions and ground truth values.

    Return:
        Parsed answers with ground truth values and instance-wise metrics computed.
        Both instance-wise and global metrics are also saved to disc.
    """

    # read data
    path = os.path.join(folder, "parsed_answers.csv")

    parsed_answers = pd.read_csv(path)
    parsed_answers = parsed_answers.sort_values(by=["path", "row_number"]).reset_index(drop=True)

    # compute instance-wise metrics
    parsed_answers["mae"] = abs(parsed_answers["gt"] - parsed_answers["prediction"])
    parsed_answers["mse"] = (parsed_answers["gt"] - parsed_answers["prediction"]) ** 2
    parsed_answers["mape"] = parsed_answers["mae"] / parsed_answers["gt"]

    # save data
    parsed_answers.to_csv(path, index=False)

    # compute and save global metrics
    metrics_by_file = parsed_answers.groupby("path")[["mae", "mse", "mape"]].mean()
    metrics_by_file["rmse"] = np.sqrt(metrics_by_file["mse"])
    metrics_by_file[["rmse", "mae", "mape"]].to_csv(os.path.join(folder, "metrics_by_file.csv"))

    return parsed_answers
