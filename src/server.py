import json
import pickle

import pandas as pd

from flask import Flask, request, jsonify


from models import MeanRegressor, RandomRegressor
with open("../models/LGBMRegressor.pkl", "rb") as f:
    model = pickle.load(f)
with open("../models/feature_sequence.txt", "r") as f:
    feature_sequence = json.load(f)

app = Flask(__name__)


@app.route("/ready")
def http_ready():
    return "OK"


@app.route("/predict", methods=["POST"])
def http_predict():
    request_data = request.get_json()
    X = pd.DataFrame(request_data["data"])[feature_sequence].values
    preds = model.predict(X)
    return jsonify({
        "predictions": preds.tolist()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
