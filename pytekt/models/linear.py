"""Linear models (regression and classification)."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ._base import BaseEstimator, _as_1d, _as_2d


class LinearRegression(BaseEstimator):
    """Ordinary least squares linear regression (normal equation)."""

    def __init__(self, *, fit_intercept: bool = True) -> None:
        self.fit_intercept = fit_intercept
        self.coef_: Optional[np.ndarray] = None
        self.intercept_: float = 0.0

    def fit(self, X, y) -> "LinearRegression":
        X = _as_2d(X)
        y = _as_1d(y)
        if self.fit_intercept:
            X_aug = np.hstack([np.ones((X.shape[0], 1)), X])
        else:
            X_aug = X
        w, _, _, _ = np.linalg.lstsq(X_aug, y, rcond=None)
        if self.fit_intercept:
            self.intercept_ = float(w[0])
            self.coef_ = w[1:]
        else:
            self.intercept_ = 0.0
            self.coef_ = w
        return self

    def predict(self, X) -> np.ndarray:
        X = _as_2d(X)
        return X @ self.coef_ + self.intercept_


class LogisticRegression(BaseEstimator):
    """Binary logistic regression via gradient descent."""

    def __init__(
        self,
        *,
        learning_rate: float = 0.1,
        max_iter: int = 1000,
        fit_intercept: bool = True,
        tol: float = 1e-5,
        l2: float = 0.0,
    ) -> None:
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.fit_intercept = fit_intercept
        self.tol = tol
        self.l2 = l2
        self.coef_: Optional[np.ndarray] = None
        self.intercept_: float = 0.0
        self.classes_: Optional[np.ndarray] = None

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        z = np.clip(z, -500, 500)
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, X, y) -> "LogisticRegression":
        X = _as_2d(X)
        y = _as_1d(y)
        self.classes_ = np.unique(y)
        if len(self.classes_) != 2:
            raise ValueError("LogisticRegression supports binary classification only")
        y_bin = (y == self.classes_[1]).astype(np.float64)
        n, d = X.shape
        w = np.zeros(d)
        b = 0.0
        for _ in range(self.max_iter):
            z = X @ w + b
            p = self._sigmoid(z)
            grad_w = (X.T @ (p - y_bin)) / n + self.l2 * w
            grad_b = np.mean(p - y_bin)
            w_new = w - self.learning_rate * grad_w
            b_new = b - self.learning_rate * grad_b
            if np.max(np.abs(w_new - w)) < self.tol:
                w, b = w_new, b_new
                break
            w, b = w_new, b_new
        self.coef_ = w
        self.intercept_ = float(b)
        return self

    def predict_proba(self, X) -> np.ndarray:
        X = _as_2d(X)
        p1 = self._sigmoid(X @ self.coef_ + self.intercept_)
        return np.column_stack([1 - p1, p1])

    def predict(self, X) -> np.ndarray:
        proba = self.predict_proba(X)[:, 1]
        labels = np.where(proba >= 0.5, self.classes_[1], self.classes_[0])
        return labels
