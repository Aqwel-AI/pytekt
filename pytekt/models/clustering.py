"""Clustering algorithms."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ._base import BaseEstimator, _as_2d


class KMeans(BaseEstimator):
    """K-means clustering (Lloyd's algorithm)."""

    def __init__(
        self,
        n_clusters: int = 8,
        *,
        max_iter: int = 300,
        tol: float = 1e-4,
        random_state: Optional[int] = None,
    ) -> None:
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.cluster_centers_: Optional[np.ndarray] = None
        self.labels_: Optional[np.ndarray] = None
        self.inertia_: float = 0.0

    def fit(self, X, y=None) -> "KMeans":
        X = _as_2d(X)
        rng = np.random.RandomState(self.random_state)
        n = X.shape[0]
        idx = rng.choice(n, self.n_clusters, replace=n >= self.n_clusters)
        centers = X[idx].copy()
        for _ in range(self.max_iter):
            dist = np.linalg.norm(X[:, np.newaxis] - centers[np.newaxis], axis=2)
            labels = np.argmin(dist, axis=1)
            new_centers = np.array([X[labels == k].mean(axis=0) for k in range(self.n_clusters)])
            if np.max(np.abs(new_centers - centers)) < self.tol:
                centers = new_centers
                break
            centers = new_centers
        self.cluster_centers_ = centers
        self.labels_ = labels
        self.inertia_ = float(((X - centers[labels]) ** 2).sum())
        return self

    def predict(self, X) -> np.ndarray:
        X = _as_2d(X)
        dist = np.linalg.norm(X[:, np.newaxis] - self.cluster_centers_[np.newaxis], axis=2)
        return np.argmin(dist, axis=1)

    def fit_predict(self, X) -> np.ndarray:
        return self.fit(X).labels_
