"""Deterministic routing helpers for specialized agents."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple


DEFAULT_ROUTE_RULES: Tuple[Tuple[str, str], ...] = (
    ("bug", "debug"),
    ("error", "debug"),
    ("python", "code"),
    ("dataset", "data"),
    ("csv", "data"),
    ("physics", "physics"),
    ("thermo", "physics"),
    ("document", "docs"),
    ("readme", "docs"),
    ("research", "research"),
)


def route_task(task: str, route_map: Dict[str, str] | Iterable[Tuple[str, str]] | None = None) -> str:
    """Route a task to a specialist role using deterministic keyword matching."""
    normalized = task.casefold()
    rules = route_map.items() if isinstance(route_map, dict) else (route_map or DEFAULT_ROUTE_RULES)
    for keyword, role in rules:
        if keyword in normalized:
            return role
    return "general"
