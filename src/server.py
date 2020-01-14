import json
import pickle

import pandas as pd

from flask import Flask, request, jsonify


# load previously trained and saved MeanRegressor model
from models import MeanRegressor, RandomRegressor
with open("../models/MeanRegressor.pkl", "rb") as f:
    model = pickle.load(f)
# load correct order of features for the model
with open("../models/feature_sequence.txt", "r") as f:
    feature_sequence = json.load(f)

# initialize Flask web app
app = Flask(__name__)


# add `/ready` endpoint which allows to check that the app
# initialization and model loading went well
@app.route("/ready")
def http_ready():
    return "OK"


# main `predict` endpoint which accepts data and outputs predictions
@app.route("/predict", methods=["POST"])
def http_predict():
    # get data from JSON body
    request_data = request.get_json()
    # transform data into array with correct order of features
    X = pd.DataFrame(request_data["data"])[feature_sequence].values
    # make prediction
    preds = model.predict(X)
    # return answers
    return jsonify({
        "predictions": preds.tolist()
    })


# run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
