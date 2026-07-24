"""Base classes for preprocessing transformers."""

from __future__ import annotations

from typing import Any, Optional, Tuple, Union

import numpy as np

ArrayLike = Union[np.ndarray, list]


def _as_2d(X: ArrayLike) -> np.ndarray:
    arr = np.asarray(X, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    return arr


class TransformerMixin:
    """Mixin providing ``fit_transform``."""

    def fit(self, X: ArrayLike, y: Optional[Any] = None) -> "TransformerMixin":
        raise NotImplementedError

    def transform(self, X: ArrayLike) -> np.ndarray:
        raise NotImplementedError

    def fit_transform(self, X: ArrayLike, y: Optional[Any] = None) -> np.ndarray:
        return self.fit(X, y).transform(X)

    def inverse_transform(self, X: ArrayLike) -> np.ndarray:
        raise NotImplementedError("inverse_transform not implemented for this transformer")
