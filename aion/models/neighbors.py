"""K-nearest neighbors models."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ._base import BaseEstimator, _as_1d, _as_2d


class KNNClassifier(BaseEstimator):
    """K-nearest neighbors classifier."""

    def __init__(self, n_neighbors: int = 5, *, weights: str = "uniform") -> None:
        self.n_neighbors = n_neighbors
        self.weights = weights
        self._X: Optional[np.ndarray] = None
        self._y: Optional[np.ndarray] = None
        self.classes_: Optional[np.ndarray] = None

    def fit(self, X, y) -> "KNNClassifier":
        self._X = _as_2d(X)
        self._y = _as_1d(y)
        self.classes_ = np.unique(self._y)
        return self

    def _distances(self, X: np.ndarray) -> np.ndarray:
        # (n_test, n_train)
        diff = X[:, np.newaxis, :] - self._X[np.newaxis, :, :]
        return np.sqrt((diff ** 2).sum(axis=2))

    def predict(self, X) -> np.ndarray:
        X = _as_2d(X)
        dist = self._distances(X)
        k = min(self.n_neighbors, self._X.shape[0])
        idx = np.argpartition(dist, k - 1, axis=1)[:, :k]
        preds = []
        for i in range(X.shape[0]):
            labels = self._y[idx[i]]
            if self.weights == "distance":
                d = dist[i, idx[i]] + 1e-8
                w = 1.0 / d
                votes: dict = {}
                for lab, wt in zip(labels, w):
                    votes[lab] = votes.get(lab, 0) + wt
                preds.append(max(votes, key=votes.get))
            else:
                vals, counts = np.unique(labels, return_counts=True)
                preds.append(vals[np.argmax(counts)])
        return np.array(preds)


class KNNRegressor(BaseEstimator):
    """K-nearest neighbors regressor."""

    def __init__(self, n_neighbors: int = 5, *, weights: str = "uniform") -> None:
        self.n_neighbors = n_neighbors
        self.weights = weights
        self._X: Optional[np.ndarray] = None
        self._y: Optional[np.ndarray] = None

    def fit(self, X, y) -> "KNNRegressor":
        self._X = _as_2d(X)
        self._y = _as_1d(y)
        return self

    def predict(self, X) -> np.ndarray:
        X = _as_2d(X)
        diff = X[:, np.newaxis, :] - self._X[np.newaxis, :, :]
        dist = np.sqrt((diff ** 2).sum(axis=2))
        k = min(self.n_neighbors, self._X.shape[0])
        idx = np.argpartition(dist, k - 1, axis=1)[:, :k]
        preds = []
        for i in range(X.shape[0]):
            y_neigh = self._y[idx[i]]
            if self.weights == "distance":
                d = dist[i, idx[i]] + 1e-8
                preds.append(np.average(y_neigh, weights=1.0 / d))
            else:
                preds.append(np.mean(y_neigh))
        return np.array(preds)
