"""Clustering metrics."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

ArrayLike = Union[np.ndarray, Sequence]


def silhouette_score(X: ArrayLike, labels: ArrayLike) -> float:
    """Mean silhouette coefficient (-1 to 1, higher is better)."""
    X = np.asarray(X, dtype=np.float64)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    labels = np.asarray(labels).ravel()
    unique = np.unique(labels)
    n = X.shape[0]
    if len(unique) < 2 or n <= len(unique):
        return 0.0
    scores = []
    for i in range(n):
        same = labels == labels[i]
        a = np.mean(np.linalg.norm(X[same] - X[i], axis=1))
        b = np.inf
        for c in unique:
            if c == labels[i]:
                continue
            other = X[labels == c]
            b = min(b, np.mean(np.linalg.norm(other - X[i], axis=1)))
        if b == np.inf:
            continue
        s = (b - a) / max(a, b) if max(a, b) > 0 else 0.0
        scores.append(s)
    return float(np.mean(scores)) if scores else 0.0


def adjusted_rand_score(labels_true: ArrayLike, labels_pred: ArrayLike) -> float:
    """Adjusted Rand index for cluster agreement."""
    lt = np.asarray(labels_true).ravel()
    lp = np.asarray(labels_pred).ravel()
    n = len(lt)
    contingency = {}
    for i in range(n):
        contingency[(lt[i], lp[i])] = contingency.get((lt[i], lp[i]), 0) + 1
    def comb2(x):
        return x * (x - 1) / 2
    sum_comb = sum(comb2(v) for v in contingency.values())
    sum_a = sum(comb2(np.sum(lt == a)) for a in np.unique(lt))
    sum_b = sum(comb2(np.sum(lp == b)) for b in np.unique(lp))
    total = comb2(n)
    if total == 0:
        return 1.0
    expected = sum_a * sum_b / total
    max_index = 0.5 * (sum_a + sum_b)
    return float((sum_comb - expected) / (max_index - expected)) if max_index != expected else 0.0
