"""Dataset splitting: train/test, train/val/test, k-fold."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")


def train_test_split(
    *arrays: Any,
    test_ratio: Optional[float] = None,
    test_size: Optional[float] = None,
    shuffle: bool = True,
    seed: Optional[int] = None,
    random_state: Optional[int] = None,
    stratify_key: Optional[Callable[[Any], Any]] = None,
) -> Any:
    """
    Split one or more datasets into train and test sets.

    Supports both single datasets (returning ``(train, test)``) and multiple
    arrays such as ``X, y`` (returning ``(X_train, X_test, y_train, y_test)``).
    Preserves NumPy array types when provided.

    Parameters
    ----------
    *arrays : sequence or ndarray
        One or more datasets of the same length to split.
    test_ratio, test_size : float, default=0.2
        Fraction of data for the test set (0..1).
    shuffle : bool, default=True
        Whether to shuffle data before splitting.
    seed, random_state : int, optional
        Random seed for reproducibility.
    stratify_key : callable, optional
        Function mapping each item to a class label for stratified splitting
        (only applicable when splitting a single dataset).
    """
    if not arrays:
        raise ValueError("At least one array or dataset must be passed to train_test_split")

    ratio = test_size if test_size is not None else (test_ratio if test_ratio is not None else 0.2)
    resolved_seed = random_state if random_state is not None else seed

    if len(arrays) == 1:
        data = arrays[0]
        if stratify_key is not None:
            return _stratified_split(data, [1 - ratio, ratio], stratify_key, shuffle, resolved_seed)[:2]

        n = len(data)
        split = int(n * (1 - ratio))
        indices = list(range(n))
        if shuffle:
            rng = random.Random(resolved_seed)
            rng.shuffle(indices)

        train_idx = indices[:split]
        test_idx = indices[split:]

        try:
            import numpy as np
            if isinstance(data, np.ndarray):
                return data[train_idx], data[test_idx]
        except ImportError:
            pass

        items = list(data)
        return [items[i] for i in train_idx], [items[i] for i in test_idx]

    # Multiple arrays (e.g. X, y)
    lengths = [len(a) for a in arrays]
    if len(set(lengths)) > 1:
        raise ValueError(f"All arrays must have the same length. Got lengths: {lengths}")

    n = lengths[0]
    split = int(n * (1 - ratio))
    indices = list(range(n))
    if shuffle:
        rng = random.Random(resolved_seed)
        rng.shuffle(indices)

    train_idx = indices[:split]
    test_idx = indices[split:]

    res = []
    try:
        import numpy as np
    except ImportError:
        np = None

    for a in arrays:
        if np is not None and isinstance(a, np.ndarray):
            res.extend([a[train_idx], a[test_idx]])
        else:
            items = list(a)
            res.extend([[items[i] for i in train_idx], [items[i] for i in test_idx]])

    return tuple(res)


def train_val_test_split(
    data: Sequence[T],
    *,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    shuffle: bool = True,
    seed: Optional[int] = None,
    stratify_key: Optional[Callable[[T], Any]] = None,
) -> Tuple[List[T], List[T], List[T]]:
    """Split *data* into train, validation, and test sets."""
    total = train_ratio + val_ratio + test_ratio
    tr = train_ratio / total
    va = val_ratio / total

    if stratify_key is not None:
        return _stratified_split(data, [tr, va, 1 - tr - va], stratify_key, shuffle, seed)  # type: ignore[return-value]

    items = list(data)
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(items)
    n = len(items)
    s1 = int(n * tr)
    s2 = int(n * (tr + va))
    return items[:s1], items[s1:s2], items[s2:]


def kfold_split(
    data: Sequence[T],
    k: int = 5,
    *,
    shuffle: bool = True,
    seed: Optional[int] = None,
) -> List[Tuple[List[T], List[T]]]:
    """
    Generate *k* train/test folds for cross-validation.

    Returns a list of ``(train, test)`` tuples.
    """
    items = list(data)
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(items)
    fold_size = len(items) // k
    folds: List[Tuple[List[T], List[T]]] = []
    for i in range(k):
        start = i * fold_size
        end = start + fold_size if i < k - 1 else len(items)
        test_fold = items[start:end]
        train_fold = items[:start] + items[end:]
        folds.append((train_fold, test_fold))
    return folds


def _stratified_split(
    data: Sequence[T],
    ratios: List[float],
    key_fn: Callable[[T], Any],
    shuffle: bool,
    seed: Optional[int],
) -> Tuple[List[T], ...]:
    groups: Dict[Any, List[T]] = defaultdict(list)
    for item in data:
        groups[key_fn(item)].append(item)

    rng = random.Random(seed) if shuffle else None
    buckets: List[List[T]] = [[] for _ in ratios]

    for label, items in groups.items():
        if rng:
            rng.shuffle(items)
        n = len(items)
        boundaries = []
        cumulative = 0.0
        for r in ratios[:-1]:
            cumulative += r
            boundaries.append(int(n * cumulative))
        boundaries.append(n)
        prev = 0
        for i, b in enumerate(boundaries):
            buckets[i].extend(items[prev:b])
            prev = b

    if rng:
        for bucket in buckets:
            rng.shuffle(bucket)

    return tuple(buckets)
