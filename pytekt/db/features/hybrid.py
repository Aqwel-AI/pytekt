"""Hybrid text + vector + metadata search."""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Sequence

from ..base import Connection


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _text_score(text: str, query: str) -> float:
    if not query or not text:
        return 0.0
    q = query.lower()
    t = text.lower()
    if q in t:
        return 1.0
    words = [w for w in re.split(r"\W+", q) if w]
    if not words:
        return 0.0
    hits = sum(1 for w in words if w in t)
    return hits / len(words)


def hybrid_search(
    conn: Connection,
    collection: str,
    *,
    text: Optional[str] = None,
    vector: Optional[Sequence[float]] = None,
    filter: Optional[Dict[str, Any]] = None,
    text_field: str = "content",
    vector_field: str = "embedding",
    top_k: int = 10,
    text_weight: float = 0.4,
    vector_weight: float = 0.6,
) -> List[Dict[str, Any]]:
    """
    Score documents by combining text match, vector similarity, and metadata filters.

    Works on any backend; vector similarity uses cosine distance in Python.
    """
    coll = conn.collection(collection)
    candidates = coll.find(**(filter or {}))
    scored: List[tuple[float, Dict[str, Any]]] = []
    for doc in candidates:
        score = 0.0
        if text:
            body = str(doc.get(text_field, doc.get("text", "")))
            score += text_weight * _text_score(body, text)
        if vector is not None:
            emb = doc.get(vector_field)
            if isinstance(emb, (list, tuple)):
                score += vector_weight * _cosine(vector, emb)
        elif text is None:
            score = 1.0
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:top_k] if s > 0 or (text is None and vector is None)]
