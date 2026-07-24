"""Faithfulness and groundedness checks for RAG outputs."""

from __future__ import annotations

from typing import Any, Dict, List

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


def faithfulness_score(response: str, context: str) -> float:
    """
    Estimate how faithful *response* is to *context* using sentence-level
    embedding similarity.

    Splits the response into sentences and checks how well each aligns
    with the context. Returns a score in ``[0, 1]``.
    """
    sentences = [s.strip() for s in response.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    if not sentences:
        return 0.0

    ctx_vec = _embed(context)
    scores = [max(0.0, _cosine(_embed(s), ctx_vec)) for s in sentences]
    return float(np.mean(scores))


def check_groundedness(
    response: str,
    sources: List[str],
    *,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Check whether each sentence in *response* is grounded in at least one
    of the *sources*.

    Returns per-sentence verdicts and an overall groundedness ratio.
    """
    sentences = [s.strip() for s in response.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    if not sentences:
        return {"grounded_ratio": 0.0, "sentences": []}

    source_vecs = [_embed(s) for s in sources]
    results = []
    grounded_count = 0

    for sent in sentences:
        sent_vec = _embed(sent)
        best_score = max(_cosine(sent_vec, sv) for sv in source_vecs) if source_vecs else 0.0
        is_grounded = best_score >= threshold
        if is_grounded:
            grounded_count += 1
        results.append({
            "sentence": sent,
            "best_similarity": round(best_score, 4),
            "grounded": is_grounded,
        })

    return {
        "grounded_ratio": grounded_count / len(sentences),
        "sentences": results,
    }
