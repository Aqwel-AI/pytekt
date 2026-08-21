"""
Sorting Subpackage
==================

Provides comparison-based, distribution-based, and specialized sorting algorithms:
- Comparison sorts: quick_sort, merge_sort, heap_sort, tim_sort, insertion_sort, selection_sort, bubble_sort
- Non-comparison & distribution sorts: counting_sort, radix_sort, bucket_sort
- Specialized sorts: shell_sort, comb_sort, cycle_sort, pancake_sort, cocktail_shaker_sort, etc.
"""

from __future__ import annotations

from . import sorting
from .sorting import *  # noqa: F401, F403

__all__ = [
    "sorting",
    "bubble_sort",
    "selection_sort",
    "insertion_sort",
    "merge_sort",
    "quick_sort",
    "heap_sort",
    "counting_sort",
    "radix_sort",
    "bucket_sort",
    "shell_sort",
    "comb_sort",
    "cycle_sort",
    "tim_sort",
]
