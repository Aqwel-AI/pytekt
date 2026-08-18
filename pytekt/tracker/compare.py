"""Utilities for comparing experiment runs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def compare_runs(
    runs: List[Dict[str, Any]],
    metric_name: Optional[str] = None,
    *,
    ascending: bool = False,
) -> List[Dict[str, Any]]:
    """
    Sort runs by a metric value for comparison.

    If *metric_name* is ``None``, returns runs sorted by start time.
    """
    if metric_name is None:
        return sorted(runs, key=lambda r: r.get("start_time", 0), reverse=True)

    def sort_key(run: Dict[str, Any]) -> float:
        metrics = run.get("metrics", {})
        val = metrics.get(metric_name)
        if val is None:
            return float("-inf") if not ascending else float("inf")
        return val

    return sorted(runs, key=sort_key, reverse=not ascending)


def best_run(
    runs: List[Dict[str, Any]],
    metric_name: str,
    *,
    minimize: bool = True,
) -> Optional[Dict[str, Any]]:
    """Return the run with the best value for *metric_name*."""
    ranked = compare_runs(runs, metric_name, ascending=minimize)
    return ranked[0] if ranked else None
