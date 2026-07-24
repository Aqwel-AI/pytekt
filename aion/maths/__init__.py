"""Sectioned mathematics and statistics utilities.

The category packages provide focused imports, while this module preserves
the original flat API for compatibility::

    from aion import maths
    maths.mean([1, 2, 3])

    from aion.maths.linear_algebra import matrix_multiply
"""

from . import maths as _core
from . import (
    arithmetic,
    linear_algebra,
    machine_learning,
    number_theory,
    probability,
    random,
    signal_processing,
    statistics,
    trigonometry,
    utilities,
)

MATH_SECTIONS = _core.MATH_SECTIONS
list_sections = _core.list_sections
section_functions = _core.section_functions

# Keep ``aion.maths.<function>`` compatible with the original single-file
# module while the implementation is organized into category packages.
for _section_names in MATH_SECTIONS.values():
    for _name in _section_names:
        globals()[_name] = getattr(_core, _name)

__all__ = [
    "MATH_SECTIONS",
    "list_sections",
    "section_functions",
    "arithmetic",
    "random",
    "linear_algebra",
    "statistics",
    "trigonometry",
    "machine_learning",
    "signal_processing",
    "probability",
    "number_theory",
    "utilities",
    *[name for names in MATH_SECTIONS.values() for name in names],
]

del _section_names, _name
