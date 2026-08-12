"""Base estimator for PyTekt models."""

from __future__ import annotations

from typing import Any, Optional, Union

import numpy as np

ArrayLike = Union[np.ndarray, list]


def _as_2d(X: ArrayLike) -> np.ndarray:
    arr = np.asarray(X, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    return arr


def _as_1d(y: ArrayLike) -> np.ndarray:
    return np.asarray(y).ravel()


class BaseEstimator:
    """Minimal sklearn-style estimator interface."""

    def fit(self, X: ArrayLike, y: ArrayLike) -> "BaseEstimator":
        raise NotImplementedError

    def predict(self, X: ArrayLike) -> np.ndarray:
        raise NotImplementedError

    def score(self, X: ArrayLike, y: ArrayLike) -> float:
        from ..metrics.regression import r2_score
        from ..metrics.classification import accuracy_score

        y_pred = self.predict(X)
        y_true = _as_1d(y)
        if hasattr(self, "classes_"):
            return float(accuracy_score(y_true, y_pred))
        return float(r2_score(y_true, y_pred))
