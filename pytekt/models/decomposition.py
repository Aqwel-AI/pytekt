"""Dimensionality reduction."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ._base import BaseEstimator, _as_2d


class PCA(BaseEstimator):
    """Principal component analysis via SVD."""

    def __init__(self, n_components: Optional[int] = None) -> None:
        self.n_components = n_components
        self.components_: Optional[np.ndarray] = None
        self.mean_: Optional[np.ndarray] = None
        self.explained_variance_ratio_: Optional[np.ndarray] = None

    def fit(self, X, y=None) -> "PCA":
        X = _as_2d(X)
        self.mean_ = X.mean(axis=0)
        Xc = X - self.mean_
        _, s, vt = np.linalg.svd(Xc, full_matrices=False)
        n_comp = self.n_components or min(X.shape)
        self.components_ = vt[:n_comp]
        var = (s ** 2) / max(X.shape[0] - 1, 1)
        total = var.sum()
        self.explained_variance_ratio_ = var[:n_comp] / total if total > 0 else var[:n_comp]
        return self

    def transform(self, X) -> np.ndarray:
        X = _as_2d(X) - self.mean_
        return X @ self.components_.T

    def fit_transform(self, X) -> np.ndarray:
        return self.fit(X).transform(X)

    def predict(self, X) -> np.ndarray:
        return self.transform(X)
