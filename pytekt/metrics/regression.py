"""Regression metrics."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

ArrayLike = Union[np.ndarray, Sequence[float]]


def _check(y_true, y_pred) -> tuple:
    yt = np.asarray(y_true, dtype=np.float64).ravel()
    yp = np.asarray(y_pred, dtype=np.float64).ravel()
    if len(yt) != len(yp):
        raise ValueError("y_true and y_pred must have the same length")
    return yt, yp


def mean_squared_error(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    yt, yp = _check(y_true, y_pred)
    return float(np.mean((yt - yp) ** 2))


def root_mean_squared_error(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def mean_absolute_error(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    yt, yp = _check(y_true, y_pred)
    return float(np.mean(np.abs(yt - yp)))


def mean_absolute_percentage_error(y_true: ArrayLike, y_pred: ArrayLike, *, eps: float = 1e-8) -> float:
    yt, yp = _check(y_true, y_pred)
    return float(np.mean(np.abs((yt - yp) / (yt + eps))) * 100)


def r2_score(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    yt, yp = _check(y_true, y_pred)
    ss_res = np.sum((yt - yp) ** 2)
    ss_tot = np.sum((yt - np.mean(yt)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def adjusted_r2_score(y_true: ArrayLike, y_pred: ArrayLike, *, n_features: int = 1) -> float:
    yt, yp = _check(y_true, y_pred)
    n = len(yt)
    r2 = r2_score(yt, yp)
    if n - n_features - 1 <= 0:
        return r2
    return float(1 - (1 - r2) * (n - 1) / (n - n_features - 1))


def explained_variance_score(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    yt, yp = _check(y_true, y_pred)
    var = np.var(yt)
    if var == 0:
        return 1.0 if np.allclose(yt, yp) else 0.0
    return float(1 - np.var(yt - yp) / var)
