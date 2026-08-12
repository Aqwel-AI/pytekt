"""Algorithm registry for discovery and introspection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

ALGORITHM_REGISTRY: List["AlgorithmEntry"] = []
_ALGORITHM_BY_NAME: Dict[str, Callable[..., Any]] = {}


@dataclass(frozen=True)
class AlgorithmEntry:
    name: str
    module: str
    category: str
    summary: str


def register_algorithm(
    *,
    category: str,
    summary: str = "",
    module: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a public algorithm function."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        mod = module or fn.__module__.rsplit(".", 1)[-1]
        entry = AlgorithmEntry(
            name=fn.__name__,
            module=mod,
            category=category,
            summary=summary or (fn.__doc__ or "").strip().split("\n")[0],
        )
        ALGORITHM_REGISTRY.append(entry)
        _ALGORITHM_BY_NAME[fn.__name__] = fn
        return fn

    return decorator


def register_existing(
    fn: Callable[..., Any],
    *,
    category: str,
    summary: str = "",
    module: Optional[str] = None,
) -> None:
    """Register a function without decorating (for legacy modules)."""
    mod = module or getattr(fn, "__module__", "unknown").rsplit(".", 1)[-1]
    entry = AlgorithmEntry(
        name=fn.__name__,
        module=mod,
        category=category,
        summary=summary or (fn.__doc__ or "").strip().split("\n")[0],
    )
    if fn.__name__ not in _ALGORITHM_BY_NAME:
        ALGORITHM_REGISTRY.append(entry)
        _ALGORITHM_BY_NAME[fn.__name__] = fn


def list_algorithms(category: Optional[str] = None) -> List[AlgorithmEntry]:
    if category is None:
        return list(ALGORITHM_REGISTRY)
    return [e for e in ALGORITHM_REGISTRY if e.category == category]


def count_algorithms() -> int:
    return len(ALGORITHM_REGISTRY)


def get_algorithm(name: str) -> Callable[..., Any]:
    if name not in _ALGORITHM_BY_NAME:
        raise KeyError(f"Unknown algorithm: {name!r}")
    return _ALGORITHM_BY_NAME[name]


def categories() -> List[str]:
    return sorted({e.category for e in ALGORITHM_REGISTRY})
