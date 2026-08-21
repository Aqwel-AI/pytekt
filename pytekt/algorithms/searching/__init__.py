"""
Searching Subpackage
====================

Provides sequence searching, selection, and optimization algorithms:
- Binary search, lower_bound, upper_bound, exponential search, jump search, ternary search
- String pattern search: KMP, Rabin-Karp, Aho-Corasick, Boyer-Moore, Bitap, Z-algorithm
- Selection algorithms: quickselect, find_median_unordered, find_k_closest_elements
- Binary search on answer / optimization: integer_sqrt, nth_root, ship_capacity, etc.
"""

from __future__ import annotations

from . import search
from .search import *  # noqa: F401, F403

__all__ = [
    "search",
    "binary_search",
    "lower_bound",
    "upper_bound",
    "is_sorted",
    "jump_search",
    "find_all_peaks",
    "exponential_search",
    "linear_search",
    "first_occurrence",
    "last_occurrence",
    "first_last_occurrence",
    "rotated_search",
    "ternary_search",
    "interpolation_search",
    "integer_sqrt",
    "nth_root",
    "kmp_search",
    "aho_corasick_simple",
    "quickselect",
    "find_median_unordered",
]
