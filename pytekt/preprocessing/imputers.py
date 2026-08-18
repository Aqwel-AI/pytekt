"""Missing value imputation."""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from ._base import TransformerMixin, _as_2d


class SimpleImputer(TransformerMixin):
    """Replace missing values with mean, median, mode, or a constant.

    Parameters
    ----------
    strategy : str
        ``'mean'``, ``'median'``, ``'most_frequent'``, or ``'constant'``.
    fill_value : float
        Used when strategy is ``'constant'``.
  missing_values : float
        Value treated as missing (default NaN).
    """

    def __init__(
        self,
        *,
        strategy: str = "mean",
        fill_value: float = 0.0,
        missing_values: float = np.nan,
    ) -> None:
        self.strategy = strategy
        self.fill_value = fill_value
        self.missing_values = missing_values
        self.statistics_: Optional[np.ndarray] = None

    def _mask(self, X: np.ndarray) -> np.ndarray:
        if np.isnan(self.missing_values):
            return np.isnan(X)
        return X == self.missing_values

    def fit(self, X, y: Optional[Any] = None) -> "SimpleImputer":
        X = _as_2d(X).copy()
        mask = self._mask(X)
        X[mask] = np.nan
        if self.strategy == "mean":
            self.statistics_ = np.nanmean(X, axis=0)
        elif self.strategy == "median":
            self.statistics_ = np.nanmedian(X, axis=0)
        elif self.strategy == "most_frequent":
            stats = []
            for j in range(X.shape[1]):
                col = X[:, j]
                col = col[~np.isnan(col)]
                if len(col) == 0:
                    stats.append(0.0)
                else:
                    vals, counts = np.unique(col, return_counts=True)
                    stats.append(vals[np.argmax(counts)])
            self.statistics_ = np.array(stats, dtype=np.float64)
        elif self.strategy == "constant":
            self.statistics_ = np.full(X.shape[1], self.fill_value)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        nan_cols = np.isnan(self.statistics_)
        self.statistics_[nan_cols] = self.fill_value
        return self

    def transform(self, X) -> np.ndarray:
        if self.statistics_ is None:
            raise RuntimeError("SimpleImputer is not fitted")
        X = _as_2d(X).copy()
        mask = self._mask(X)
        for j in range(X.shape[1]):
            X[mask[:, j], j] = self.statistics_[j]
        return X
