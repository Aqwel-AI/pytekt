"""Compose preprocessing steps."""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple, Union

import numpy as np

from ._base import TransformerMixin, _as_2d


class ColumnTransformer:
    """Apply different transformers to subsets of columns.

    Parameters
    ----------
    transformers : list of (name, transformer, columns)
        ``columns`` may be a list of indices or ``'all'``.
    remainder : str
        ``'drop'`` or ``'passthrough'`` for remaining columns.
    """

    def __init__(
        self,
        transformers: Sequence[Tuple[str, Any, Union[str, Sequence[int]]]],
        *,
        remainder: str = "drop",
    ) -> None:
        self.transformers = list(transformers)
        self.remainder = remainder
        self.n_features_out_: int = 0

    def fit(self, X, y: Optional[Any] = None) -> "ColumnTransformer":
        X = _as_2d(X)
        n_features = X.shape[1]
        used: set = set()
        self.n_features_out_ = 0
        for _, trans, cols in self.transformers:
            if cols == "all":
                col_idx = list(range(n_features))
            else:
                col_idx = list(cols)
            used.update(col_idx)
            trans.fit(X[:, col_idx], y)
            out = trans.transform(X[:1, col_idx])
            self.n_features_out_ += out.shape[1]
        if self.remainder == "passthrough":
            rest = [i for i in range(n_features) if i not in used]
            self.n_features_out_ += len(rest)
        return self

    def transform(self, X) -> np.ndarray:
        X = _as_2d(X)
        n_features = X.shape[1]
        used: set = set()
        parts: List[np.ndarray] = []
        for _, trans, cols in self.transformers:
            if cols == "all":
                col_idx = list(range(n_features))
            else:
                col_idx = list(cols)
            used.update(col_idx)
            parts.append(trans.transform(X[:, col_idx]))
        if self.remainder == "passthrough":
            rest = [i for i in range(n_features) if i not in used]
            if rest:
                parts.append(X[:, rest])
        return np.hstack(parts) if parts else np.zeros((X.shape[0], 0))

    def fit_transform(self, X, y: Optional[Any] = None) -> np.ndarray:
        return self.fit(X, y).transform(X)


class PreprocessingPipeline(TransformerMixin):
    """Chain transformers sequentially."""

    def __init__(self, steps: Sequence[Tuple[str, TransformerMixin]]) -> None:
        self.steps = list(steps)

    def fit(self, X, y: Optional[Any] = None) -> "PreprocessingPipeline":
        Xt = X
        for _, step in self.steps:
            step.fit(Xt, y)
            Xt = step.transform(Xt)
        return self

    def transform(self, X) -> np.ndarray:
        Xt = X
        for _, step in self.steps:
            Xt = step.transform(Xt)
        return _as_2d(Xt)
