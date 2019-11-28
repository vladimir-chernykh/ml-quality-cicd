import numpy as np


class MeanRegressor(object):

    def __init__(self):
        super().__init__()
        self._mean = 0

    def fit(self, X, y):
        self._mean = np.mean(y)
        return self

    def predict(self, X):
        return np.full(len(X), self._mean)
