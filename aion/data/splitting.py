"""Dataset splitting: train/test, train/val/test, k-fold."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")


def train_test_split(
    data: Sequence[T],
    *,
    test_ratio: float = 0.2,
    shuffle: bool = True,
    seed: Optional[int] = None,
    stratify_key: Optional[Callable[[T], Any]] = None,
) -> Tuple[List[T], List[T]]:
    """
    Split *data* into train and test sets.

    Parameters
    ----------
    test_ratio : float
        Fraction of data for the test set (0..1).
    stratify_key : callable, optional
        Function mapping each item to a class label for stratified splitting.
    """
    if stratify_key is not None:
        return _stratified_split(data, [1 - test_ratio, test_ratio], stratify_key, shuffle, seed)[:2]  # type: ignore[return-value]

    items = list(data)
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(items)
    split = int(len(items) * (1 - test_ratio))
    return items[:split], items[split:]


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
