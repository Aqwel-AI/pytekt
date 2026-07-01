"""Evaluation helpers for agent runs."""

from __future__ import annotations

from typing import Any, Dict, List


def evaluate_run(
    *,
    final_answer: str,
    tool_calls: List[Dict[str, Any]],
    failures: List[str],
    expected_keywords: List[str] | None = None,
) -> Dict[str, Any]:
    """Return a simple evaluation summary for one agent run."""
    normalized = final_answer.casefold()
    expected = expected_keywords or []
    covered = [keyword for keyword in expected if keyword.casefold() in normalized]
    return {
        "success": bool(final_answer.strip()) and not failures,
        "tool_call_count": len(tool_calls),
        "failure_count": len(failures),
        "keyword_coverage": len(covered) / len(expected) if expected else 1.0,
        "covered_keywords": covered,
    }
