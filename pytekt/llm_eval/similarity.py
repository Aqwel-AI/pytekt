"""Semantic similarity scoring for LLM outputs."""

from __future__ import annotations

from typing import List

import numpy as np


def _embed(text: str) -> np.ndarray:
    from ..embed import embed_text
    return embed_text(text)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a, b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(dot / (na * nb))


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Return cosine similarity between the embeddings of two texts.

    Result in ``[-1, 1]``; higher means more similar.
    """
    return _cosine(_embed(text_a), _embed(text_b))


def batch_similarity(reference: str, candidates: List[str]) -> List[float]:
    """Score each candidate against a reference text."""
    ref_vec = _embed(reference)
    return [_cosine(ref_vec, _embed(c)) for c in candidates]


def relevance_score(query: str, response: str, *, context: str = "") -> float:
    """
    Composite relevance score combining query-response and context-response
    similarity (if context is provided).
    """
    qr = semantic_similarity(query, response)
    if not context:
        return qr
    cr = semantic_similarity(context, response)
    return 0.6 * qr + 0.4 * cr
