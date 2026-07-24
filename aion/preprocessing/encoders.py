"""Categorical encoders."""

from __future__ import annotations

from typing import Any, List, Optional, Sequence

import numpy as np

from ._base import TransformerMixin, _as_2d


class LabelEncoder:
    """Encode class labels to integers 0..n_classes-1."""

    def __init__(self) -> None:
        self.classes_: Optional[np.ndarray] = None
        self._map: dict = {}

    def fit(self, y: Sequence[Any]) -> "LabelEncoder":
        self.classes_ = np.array(sorted(set(y)), dtype=object)
        self._map = {c: i for i, c in enumerate(self.classes_)}
        return self

    def transform(self, y: Sequence[Any]) -> np.ndarray:
        unknown = [v for v in y if v not in self._map]
        if unknown:
            raise ValueError(f"Unknown labels: {unknown[:5]}")
        return np.array([self._map[v] for v in y], dtype=np.int64)

    def fit_transform(self, y: Sequence[Any]) -> np.ndarray:
        return self.fit(y).transform(y)

    def inverse_transform(self, y: Sequence[int]) -> np.ndarray:
        if self.classes_ is None:
            raise RuntimeError("LabelEncoder is not fitted")
        return self.classes_[np.asarray(y, dtype=np.int64)]


class OneHotEncoder(TransformerMixin):
    """One-hot encode categorical features (dense output)."""

    def __init__(self, *, drop_first: bool = False, unknown_value: str = "error") -> None:
        self.drop_first = drop_first
        self.unknown_value = unknown_value
        self.categories_: List[np.ndarray] = []
        self.n_features_out_: int = 0

    def fit(self, X, y: Optional[Any] = None) -> "OneHotEncoder":
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self.categories_ = []
        n_out = 0
        for j in range(X.shape[1]):
            cats = np.array(sorted(set(X[:, j].tolist())), dtype=object)
            self.categories_.append(cats)
            n_cats = len(cats) - (1 if self.drop_first else 0)
            n_out += max(n_cats, 0)
        self.n_features_out_ = n_out
        return self

    def transform(self, X) -> np.ndarray:
        if not self.categories_:
            raise RuntimeError("OneHotEncoder is not fitted")
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        parts = []
        for j, cats in enumerate(self.categories_):
            col = X[:, j]
            n_cats = len(cats) - (1 if self.drop_first else 0)
            block = np.zeros((X.shape[0], max(n_cats, 1)))
            cat_to_idx = {c: i for i, c in enumerate(cats)}
            if self.drop_first:
                cat_to_idx = {c: i - 1 for i, c in enumerate(cats) if i > 0}
            for i, val in enumerate(col):
                if val in cat_to_idx:
                    idx = cat_to_idx[val]
                    if 0 <= idx < block.shape[1]:
                        block[i, idx] = 1.0
                elif self.unknown_value == "error":
                    raise ValueError(f"Unknown category {val!r} in column {j}")
            if self.drop_first and block.shape[1] > 1:
                block = block[:, : len(cats) - 1]
            parts.append(block)
        return np.hstack(parts) if parts else np.zeros((X.shape[0], 0))


class OrdinalEncoder(TransformerMixin):
    """Encode categories as integers per column."""

    def __init__(self) -> None:
        self.categories_: List[np.ndarray] = []
        self._maps: List[dict] = []

    def fit(self, X, y: Optional[Any] = None) -> "OrdinalEncoder":
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self.categories_ = []
        self._maps = []
        for j in range(X.shape[1]):
            cats = np.array(sorted(set(X[:, j].tolist())), dtype=object)
            self.categories_.append(cats)
            self._maps.append({c: i for i, c in enumerate(cats)})
        return self

    def transform(self, X) -> np.ndarray:
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        out = np.zeros(X.shape, dtype=np.float64)
        for j, mapping in enumerate(self._maps):
            for i, val in enumerate(X[:, j]):
                if val not in mapping:
                    raise ValueError(f"Unknown category {val!r} in column {j}")
                out[i, j] = mapping[val]
        return out
