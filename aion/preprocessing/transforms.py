"""Feature construction and binning."""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from ._base import TransformerMixin, _as_2d


class PolynomialFeatures(TransformerMixin):
    """Generate polynomial and interaction features up to a given degree."""

    def __init__(self, degree: int = 2, *, include_bias: bool = True) -> None:
        self.degree = degree
        self.include_bias = include_bias
        self.n_features_out_: int = 0

    def fit(self, X, y: Optional[Any] = None) -> "PolynomialFeatures":
        X = _as_2d(X)
        n_in = X.shape[1]
        # count monomials: C(n_in + degree, degree) roughly - compute for degree 2
        self.n_features_out_ = self._count_output_features(n_in)
        return self

    def _count_output_features(self, n_in: int) -> int:
        from math import comb
        total = 0
        for d in range(1 if not self.include_bias else 0, self.degree + 1):
            total += comb(n_in + d - 1, d)
        return total

    def transform(self, X) -> np.ndarray:
        X = _as_2d(X)
        n_samples, n_in = X.shape
        if self.degree == 1:
            out = X.copy()
            if self.include_bias:
                out = np.hstack([np.ones((n_samples, 1)), out])
            return out
        if self.degree == 2:
            cols = []
            if self.include_bias:
                cols.append(np.ones((n_samples, 1)))
            cols.append(X)
            for i in range(n_in):
                for j in range(i, n_in):
                    cols.append((X[:, i] * X[:, j]).reshape(-1, 1))
            return np.hstack(cols)
        raise ValueError("PolynomialFeatures supports degree 1 or 2 only")


class Binarizer(TransformerMixin):
    """Binarize features according to a threshold."""

    def __init__(self, *, threshold: float = 0.0) -> None:
        self.threshold = threshold

    def fit(self, X, y: Optional[Any] = None) -> "Binarizer":
        return self

    def transform(self, X) -> np.ndarray:
        X = _as_2d(X)
        return (X > self.threshold).astype(np.float64)


class KBinsDiscretizer(TransformerMixin):
    """Bin continuous features into k intervals."""

    def __init__(self, n_bins: int = 5, *, strategy: str = "uniform") -> None:
        self.n_bins = n_bins
        self.strategy = strategy
        self.bin_edges_: Optional[list] = None

    def fit(self, X, y: Optional[Any] = None) -> "KBinsDiscretizer":
        X = _as_2d(X)
        self.bin_edges_ = []
        for j in range(X.shape[1]):
            col = X[:, j]
            if self.strategy == "uniform":
                edges = np.linspace(col.min(), col.max(), self.n_bins + 1)
            elif self.strategy == "quantile":
                edges = np.percentile(col, np.linspace(0, 100, self.n_bins + 1))
            else:
                raise ValueError(f"Unknown strategy: {self.strategy}")
            edges[0] -= 1e-8
            edges[-1] += 1e-8
            self.bin_edges_.append(edges)
        return self

    def transform(self, X) -> np.ndarray:
        if self.bin_edges_ is None:
            raise RuntimeError("KBinsDiscretizer is not fitted")
        X = _as_2d(X)
        out = np.zeros_like(X)
        for j, edges in enumerate(self.bin_edges_):
            out[:, j] = np.digitize(X[:, j], edges[1:-1])
        return out
