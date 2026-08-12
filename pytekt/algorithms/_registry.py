"""Register legacy algorithms from search, arrays, and graphs modules."""

from __future__ import annotations

from . import arrays, graphs, search
from .catalog import register_existing


def _register_module(module, category: str) -> None:
    for name in dir(module):
        if name.startswith("_"):
            continue
        obj = getattr(module, name)
        if callable(obj) and getattr(obj, "__module__", "").startswith("pytekt.algorithms"):
            register_existing(obj, category=category, module=module.__name__.rsplit(".", 1)[-1])


def bootstrap_legacy() -> None:
    _register_module(search, "search")
    _register_module(arrays, "arrays")
    _register_module(graphs, "graphs")


def load_all() -> None:
    """Import all algorithm modules and register legacy functions."""
    from importlib import import_module

    import_module("pytekt.algorithms.sliding_window")
    from . import (  # noqa: F401
        backtracking,
        bit_manipulation,
        compression,
        dynamic_programming,
        geometry,
        greedy,
        hashing,
        heaps,
        math_number_theory,
        numerical,
        queues_stacks,
        sorting,
        statistics,
        strings,
        trees,
        two_pointers,
        union_find,
    )

    bootstrap_legacy()
