import pickle

import numpy as np

from flask import Flask, request, jsonify


from models import MeanRegressor
with open("../models/MeanRegressor.pkl", "rb") as f:
    model = pickle.load(f)

app = Flask(__name__)


@app.route("/ready")
def http_ready():
    return "OK"


@app.route("/predict", methods=["POST"])
def http_predict():
    request_data = request.get_json()
    X = np.array(request_data["data"])
    preds = model.predict(X)
    return jsonify({
        "predictions": preds.tolist()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
