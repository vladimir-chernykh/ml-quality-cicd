import json

import pandas as pd


def answers_enricher(path):

    parsed_answers = pd.read_csv(path)
    parsed_answers = parsed_answers.sort_values(by=["path", "row_number"]).reset_index(drop=True)

    parsed_answers["gt"] = None

    # try to append correct answers to the parsed answers
    for file in parsed_answers["path"].drop_duplicates().values:
        file_data = pd.read_csv(file)
        if "MEDV" in file_data.columns:
            parsed_answers["gt"][parsed_answers["path"] == file] = file_data["MEDV"].values

    parsed_answers.to_csv(path, index=False)

    return parsed_answers
