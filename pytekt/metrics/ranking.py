"""Ranking metrics."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def ndcg_score(
    y_true: Sequence[float],
    y_score: Sequence[float],
    *,
    k: int | None = None,
) -> float:
    """Normalized discounted cumulative gain (single query)."""
    yt = np.asarray(y_true, dtype=np.float64)
    ys = np.asarray(y_score, dtype=np.float64)
    order = np.argsort(-ys)
    if k is not None:
        order = order[:k]
    gains = 2 ** yt[order] - 1
    discounts = np.log2(np.arange(2, len(gains) + 2))
    dcg = float((gains / discounts).sum())
    ideal_order = np.argsort(-yt)
    if k is not None:
        ideal_order = ideal_order[:k]
    ideal_gains = 2 ** yt[ideal_order] - 1
    idcg = float((ideal_gains / discounts[: len(ideal_gains)]).sum())
    return dcg / idcg if idcg > 0 else 0.0


def mrr_score(relevance: Sequence[Sequence[int]]) -> float:
    """Mean reciprocal rank for multiple queries (1 if relevant in list)."""
    scores = []
    for rel in relevance:
        for i, r in enumerate(rel):
            if r > 0:
                scores.append(1.0 / (i + 1))
                break
        else:
            scores.append(0.0)
    return float(np.mean(scores)) if scores else 0.0
