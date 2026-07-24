"""Simple k-fold cross-validation helpers."""

from __future__ import annotations

from typing import Any, Callable, Generator, List, Optional, Tuple

import numpy as np


def kfold_indices(
    n_samples: int,
    *,
    n_splits: int = 5,
    shuffle: bool = True,
    random_state: Optional[int] = None,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    indices = np.arange(n_samples)
    if shuffle:
        rng = np.random.default_rng(random_state)
        indices = rng.permutation(indices)
    fold_sizes = np.full(n_splits, n_samples // n_splits, dtype=int)
    fold_sizes[: n_samples % n_splits] += 1
    splits: List[Tuple[np.ndarray, np.ndarray]] = []
    current = 0
    for fold_size in fold_sizes:
        start, stop = current, current + fold_size
        test_idx = indices[start:stop]
        train_idx = np.concatenate([indices[:start], indices[stop:]])
        splits.append((train_idx, test_idx))
        current = stop
    return splits


def cross_val_score(
    estimator: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    scoring: Callable[[Any, Any, Any], float],
    n_splits: int = 5,
    shuffle: bool = True,
    random_state: Optional[int] = None,
) -> float:
    """Mean CV score (higher is better for the supplied scoring function)."""
    X = np.asarray(X)
    y = np.asarray(y).ravel()
    scores: List[float] = []
    for train_idx, test_idx in kfold_indices(
        len(y), n_splits=n_splits, shuffle=shuffle, random_state=random_state
    ):
        est = _clone_estimator(estimator)
        est.fit(X[train_idx], y[train_idx])
        scores.append(scoring(est, X[test_idx], y[test_idx]))
    return float(np.mean(scores))


def _clone_estimator(estimator: Any) -> Any:
    """Fresh unfitted estimator with the same constructor arguments."""
    cls = estimator.__class__
    params = {
        k: v
        for k, v in vars(estimator).items()
        if not k.startswith("_") and not k.endswith("_") and not callable(v)
    }
    return cls(**params)
