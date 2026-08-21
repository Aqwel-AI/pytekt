"""Register all algorithms from category subpackages into the unified catalog."""

from __future__ import annotations

from .catalog import register_existing
from .data_structures import (  # noqa: F401
    arrays,
    hashing,
    heaps,
    queues_stacks,
    trees,
    union_find,
)
from .graphs import graphs
from .mathematics import (  # noqa: F401
    geometry,
    math_number_theory,
    numerical,
    statistics,
)
from .paradigms import (  # noqa: F401
    backtracking,
    bit_manipulation,
    dynamic_programming,
    greedy,
    sliding_window,
    two_pointers,
)
from .searching import search
from .sorting import sorting  # noqa: F401
from .strings import (  # noqa: F401
    compression,
    strings,
)


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
    """Ensure all subpackages and modules are imported and cataloged."""
    bootstrap_legacy()
