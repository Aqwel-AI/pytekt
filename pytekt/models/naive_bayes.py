"""Naive Bayes classifiers."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ._base import BaseEstimator, _as_1d, _as_2d


class GaussianNB(BaseEstimator):
    """Gaussian Naive Bayes for classification."""

    def __init__(self, *, var_smoothing: float = 1e-9) -> None:
        self.var_smoothing = var_smoothing
        self.classes_: Optional[np.ndarray] = None
        self.class_count_: Optional[np.ndarray] = None
        self.theta_: Optional[np.ndarray] = None
        self.var_: Optional[np.ndarray] = None

    def fit(self, X, y) -> "GaussianNB":
        X = _as_2d(X)
        y = _as_1d(y)
        self.classes_ = np.unique(y)
        n_classes = len(self.classes_)
        n_features = X.shape[1]
        self.theta_ = np.zeros((n_classes, n_features))
        self.var_ = np.zeros((n_classes, n_features))
        self.class_count_ = np.zeros(n_classes)
        for i, c in enumerate(self.classes_):
            X_c = X[y == c]
            self.class_count_[i] = X_c.shape[0]
            self.theta_[i] = X_c.mean(axis=0)
            self.var_[i] = X_c.var(axis=0) + self.var_smoothing
        return self

    def _log_pdf(self, X: np.ndarray, mean: np.ndarray, var: np.ndarray) -> np.ndarray:
        return -0.5 * (np.log(2 * np.pi * var) + ((X - mean) ** 2) / var).sum(axis=1)

    def predict(self, X) -> np.ndarray:
        X = _as_2d(X)
        log_probs = []
        for i in range(len(self.classes_)):
            prior = np.log(self.class_count_[i] / self.class_count_.sum())
            log_probs.append(prior + self._log_pdf(X, self.theta_[i], self.var_[i]))
        return self.classes_[np.argmax(np.column_stack(log_probs), axis=1)]
