"""Feature scaling transformers."""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from ._base import TransformerMixin, _as_2d


class StandardScaler(TransformerMixin):
    """Zero mean, unit variance scaling (per feature)."""

    def __init__(self, *, with_mean: bool = True, with_std: bool = True, eps: float = 1e-8) -> None:
        self.with_mean = with_mean
        self.with_std = with_std
        self.eps = eps
        self.mean_: Optional[np.ndarray] = None
        self.scale_: Optional[np.ndarray] = None

    def fit(self, X, y: Optional[Any] = None) -> "StandardScaler":
        X = _as_2d(X)
        self.mean_ = X.mean(axis=0) if self.with_mean else np.zeros(X.shape[1])
        if self.with_std:
            self.scale_ = X.std(axis=0, ddof=0)
            self.scale_[self.scale_ < self.eps] = 1.0
        else:
            self.scale_ = np.ones(X.shape[1])
        return self

    def transform(self, X) -> np.ndarray:
        if self.mean_ is None or self.scale_ is None:
            raise RuntimeError("StandardScaler is not fitted")
        return (_as_2d(X) - self.mean_) / self.scale_

    def inverse_transform(self, X) -> np.ndarray:
        return _as_2d(X) * self.scale_ + self.mean_


class MinMaxScaler(TransformerMixin):
    """Scale features to [feature_range_min, feature_range_max]."""

    def __init__(self, feature_range: tuple = (0, 1)) -> None:
        self.feature_range = feature_range
        self.min_: Optional[np.ndarray] = None
        self.scale_: Optional[np.ndarray] = None
        self.data_min_: Optional[np.ndarray] = None
        self.data_max_: Optional[np.ndarray] = None

    def fit(self, X, y: Optional[Any] = None) -> "MinMaxScaler":
        X = _as_2d(X)
        self.data_min_ = X.min(axis=0)
        self.data_max_ = X.max(axis=0)
        data_range = self.data_max_ - self.data_min_
        data_range[data_range == 0] = 1.0
        fr_min, fr_max = self.feature_range
        self.scale_ = (fr_max - fr_min) / data_range
        self.min_ = fr_min - self.data_min_ * self.scale_
        return self

    def transform(self, X) -> np.ndarray:
        if self.min_ is None or self.scale_ is None:
            raise RuntimeError("MinMaxScaler is not fitted")
        return _as_2d(X) * self.scale_ + self.min_

    def inverse_transform(self, X) -> np.ndarray:
        if self.scale_ is None or self.min_ is None:
            raise RuntimeError("MinMaxScaler is not fitted")
        return (_as_2d(X) - self.min_) / self.scale_


class RobustScaler(TransformerMixin):
    """Scale using median and IQR (robust to outliers)."""

    def __init__(self, *, quantile_range: tuple = (25.0, 75.0)) -> None:
        self.quantile_range = quantile_range
        self.center_: Optional[np.ndarray] = None
        self.scale_: Optional[np.ndarray] = None

    def fit(self, X, y: Optional[Any] = None) -> "RobustScaler":
        X = _as_2d(X)
        self.center_ = np.median(X, axis=0)
        q_low, q_high = np.percentile(X, self.quantile_range, axis=0)
        self.scale_ = q_high - q_low
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, X) -> np.ndarray:
        if self.center_ is None or self.scale_ is None:
            raise RuntimeError("RobustScaler is not fitted")
        return (_as_2d(X) - self.center_) / self.scale_


class Normalizer(TransformerMixin):
    """Scale each sample to unit norm (l1, l2, or max)."""

    def __init__(self, norm: str = "l2", eps: float = 1e-8) -> None:
        self.norm = norm
        self.eps = eps

    def fit(self, X, y: Optional[Any] = None) -> "Normalizer":
        return self

    def transform(self, X) -> np.ndarray:
        X = _as_2d(X)
        if self.norm == "l1":
            norms = np.abs(X).sum(axis=1, keepdims=True)
        elif self.norm == "l2":
            norms = np.sqrt((X ** 2).sum(axis=1, keepdims=True))
        elif self.norm == "max":
            norms = np.abs(X).max(axis=1, keepdims=True)
        else:
            raise ValueError(f"Unknown norm: {self.norm}")
        norms = np.maximum(norms, self.eps)
        return X / norms
