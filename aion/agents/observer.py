"""Observation summarizers for logs, traces, and tool output."""

from __future__ import annotations

from typing import Dict, List


def summarize_observation(text: str, *, max_lines: int = 10) -> str:
    """Compress long observation text into a small preview."""
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    head = lines[:max_lines]
    return "\n".join(head + [f"... ({len(lines) - max_lines} more lines)"])


def observation_stats(text: str) -> Dict[str, int]:
    """Return compact stats for one observation payload."""
    lines = text.splitlines()
    return {
        "lines": len(lines),
        "non_empty_lines": sum(1 for line in lines if line.strip()),
        "characters": len(text),
    }
