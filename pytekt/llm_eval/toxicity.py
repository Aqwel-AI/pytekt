"""Basic toxicity and PII detection for LLM outputs."""

from __future__ import annotations

import re
from typing import Any, Dict, List

_TOXIC_PATTERNS = [
    r"\b(kill|murder|attack|destroy|hate|racist|sexist)\b",
    r"\b(stupid|idiot|moron|dumb)\b",
    r"\b(threat|bomb|weapon|explode)\b",
]

_PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}


def toxicity_check(text: str) -> Dict[str, Any]:
    """
    Run basic keyword-based toxicity detection.

    Returns a dict with ``is_flagged``, ``score`` (0-1), and ``matched_patterns``.
    This is a simple heuristic -- not a replacement for a trained classifier.
    """
    text_lower = text.lower()
    matches: List[str] = []
    for pattern in _TOXIC_PATTERNS:
        found = re.findall(pattern, text_lower)
        matches.extend(found)

    words = text_lower.split()
    word_count = max(len(words), 1)
    score = min(len(matches) / word_count * 5, 1.0)

    return {
        "is_flagged": len(matches) > 0,
        "score": round(score, 4),
        "matched_terms": list(set(matches)),
        "match_count": len(matches),
    }


def contains_pii(text: str) -> Dict[str, Any]:
    """
    Detect potential PII (emails, phones, SSNs, credit cards, IPs).

    Returns a dict with ``has_pii``, ``findings``, and ``count``.
    """
    findings: Dict[str, List[str]] = {}
    total = 0
    for pii_type, pattern in _PII_PATTERNS.items():
        found = re.findall(pattern, text)
        if found:
            findings[pii_type] = found
            total += len(found)

    return {
        "has_pii": total > 0,
        "findings": findings,
        "count": total,
    }
