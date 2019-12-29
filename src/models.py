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


class RandomRegressor(object):
    
    def __init__(self):
        super().__init__()
        self._max = 100
        self._min = 0
    
    def fit(self, X, y):
        self._max, self._min = np.quantile(y, (0.01, 0.99))
        return self
    
    def predict(self, X):
        np.random.seed(10)
        return np.random.rand(len(X)) * (self._max - self._min) + self._min
