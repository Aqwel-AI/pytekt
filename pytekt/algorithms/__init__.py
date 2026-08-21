"""
Algorithms Package
==================

High-performance, domain-categorized algorithmic suite for data structures,
searching, sorting, graph theory, optimization paradigms, mathematics, and strings.

Subpackages
-----------
- ``pytekt.algorithms.data_structures`` : Arrays, heaps, trees, queues/stacks, union-find, hashing
- ``pytekt.algorithms.searching``       : Sequence search, binary search on answer, selection, pattern matching
- ``pytekt.algorithms.sorting``         : Comparison, distribution, and specialized sorting algorithms
- ``pytekt.algorithms.graphs``          : Traversal, shortest path, MST, network flow, centrality, connectivity
- ``pytekt.algorithms.paradigms``       : Dynamic programming, greedy, backtracking, sliding window, two pointers, bit manipulation
- ``pytekt.algorithms.mathematics``     : Number theory, numerical methods, geometry, statistics
- ``pytekt.algorithms.strings``         : String processing, edit distance, compression (Huffman, LZW, RLE)

Catalog & Discovery
-------------------
Use ``count_algorithms()``, ``categories()``, ``list_algorithms()``, and ``get_algorithm(name)``
to discover and run any registered algorithm in the catalog.
"""

from __future__ import annotations

import sys

# 1. Catalog & Registry Core
from .catalog import (
    AlgorithmEntry,
    categories,
    count_algorithms,
    get_algorithm,
    list_algorithms,
    register_algorithm,
    register_existing,
)
from . import data_structures, searching, sorting, graphs, paradigms, mathematics, strings

# 2. Category Subpackage Modules
from .data_structures import (
    arrays,
    hashing,
    heaps,
    queues_stacks,
    trees,
    union_find,
)
from .searching import search
from .sorting import sorting as sorting_module
from .graphs import graphs as graphs_module
from .paradigms import (
    backtracking,
    bit_manipulation,
    dynamic_programming,
    greedy,
    sliding_window as sliding_window_module,
    two_pointers,
)
from .mathematics import (
    geometry,
    math_number_theory,
    numerical,
    statistics,
)
from .strings import (
    compression,
    strings as strings_module,
)

# 3. Load all algorithms into the unified catalog
from ._registry import load_all
load_all()

# 4. Backward-compatible module aliases in sys.modules
_MODULE_ALIASES = {
    "pytekt.algorithms.arrays": arrays,
    "pytekt.algorithms.heaps": heaps,
    "pytekt.algorithms.queues_stacks": queues_stacks,
    "pytekt.algorithms.trees": trees,
    "pytekt.algorithms.union_find": union_find,
    "pytekt.algorithms.hashing": hashing,
    "pytekt.algorithms.search": search,
    "pytekt.algorithms.sorting": sorting_module,
    "pytekt.algorithms.graphs": graphs_module,
    "pytekt.algorithms.backtracking": backtracking,
    "pytekt.algorithms.bit_manipulation": bit_manipulation,
    "pytekt.algorithms.dynamic_programming": dynamic_programming,
    "pytekt.algorithms.greedy": greedy,
    "pytekt.algorithms.sliding_window": sliding_window_module,
    "pytekt.algorithms.two_pointers": two_pointers,
    "pytekt.algorithms.geometry": geometry,
    "pytekt.algorithms.math_number_theory": math_number_theory,
    "pytekt.algorithms.numerical": numerical,
    "pytekt.algorithms.statistics": statistics,
    "pytekt.algorithms.strings": strings_module,
    "pytekt.algorithms.compression": compression,
}
for _mod_name, _mod_obj in _MODULE_ALIASES.items():
    sys.modules.setdefault(_mod_name, _mod_obj)

# 5. Curated Top-Level Function Exports

# Search & Selection
from .searching.search import (
    binary_search,
    lower_bound,
    upper_bound,
    is_sorted,
    jump_search,
    find_all_peaks,
    exponential_search,
    linear_search,
    first_occurrence,
    last_occurrence,
    first_last_occurrence,
    rotated_search,
    ternary_search,
    interpolation_search,
    integer_sqrt,
    nth_root,
    kmp_search,
    aho_corasick_simple,
    quickselect,
    find_median_unordered,
)

# Search Aliases
First_Occurrence = getattr(search, "First_Occurrence", first_occurrence)
Last_Occurrence = getattr(search, "Last_Occurrence", last_occurrence)
First_Last_Occurrence = getattr(search, "First_Last_Occurrence", first_last_occurrence)
roatated_search = getattr(search, "roatated_search", rotated_search)
find_peak_element = getattr(search, "find_peak_element", find_all_peaks)

# Arrays & Vectors
from .data_structures.arrays import (
    flatten_array,
    chunk_array,
    remove_duplicates,
    moving_average,
    flatten_deep,
    sliding_window,
    pad_array,
    rolling_sum,
    pairwise,
    matrix_transpose,
    matrix_multiply,
    z_score_normalization,
    min_max_scaling,
)

# Array Aliases
moving_avarage = getattr(arrays, "moving_avarage", moving_average)

# Graph Primitives
from .graphs.graphs import (
    bfs,
    dfs,
    toposort,
    dijkstra,
    a_star_search,
    bellman_ford,
    floyd_warshall,
    tarjan_scc,
    kosaraju_scc,
    prim_mst,
    kruskal_mst,
    ford_fulkerson,
    page_rank_simple,
    connected_components,
    shortest_path_unweighted,
)

# Graph Aliases
a_star = getattr(graphs_module, "a_star", a_star_search)
pagerank = getattr(graphs_module, "pagerank", page_rank_simple)

__all__ = [
    # Subpackages
    "data_structures",
    "searching",
    "sorting",
    "graphs",
    "paradigms",
    "mathematics",
    "strings",
    # Modules
    "arrays",
    "hashing",
    "heaps",
    "queues_stacks",
    "trees",
    "union_find",
    "search",
    "sorting_module",
    "graphs_module",
    "backtracking",
    "bit_manipulation",
    "dynamic_programming",
    "greedy",
    "sliding_window_module",
    "two_pointers",
    "geometry",
    "math_number_theory",
    "numerical",
    "statistics",
    "strings_module",
    "compression",
    # Catalog Discovery API
    "AlgorithmEntry",
    "categories",
    "count_algorithms",
    "get_algorithm",
    "list_algorithms",
    "register_algorithm",
    "register_existing",
    # Searching & Selection
    "binary_search",
    "lower_bound",
    "upper_bound",
    "is_sorted",
    "jump_search",
    "find_all_peaks",
    "find_peak_element",
    "exponential_search",
    "linear_search",
    "first_occurrence",
    "last_occurrence",
    "first_last_occurrence",
    "First_Occurrence",
    "Last_Occurrence",
    "First_Last_Occurrence",
    "rotated_search",
    "roatated_search",
    "ternary_search",
    "interpolation_search",
    "integer_sqrt",
    "nth_root",
    "kmp_search",
    "aho_corasick_simple",
    "quickselect",
    "find_median_unordered",
    # Array & Matrix
    "flatten_array",
    "chunk_array",
    "remove_duplicates",
    "moving_average",
    "moving_avarage",
    "flatten_deep",
    "sliding_window",
    "pad_array",
    "rolling_sum",
    "pairwise",
    "matrix_transpose",
    "matrix_multiply",
    "z_score_normalization",
    "min_max_scaling",
    # Graphs
    "bfs",
    "dfs",
    "toposort",
    "dijkstra",
    "a_star",
    "a_star_search",
    "bellman_ford",
    "floyd_warshall",
    "tarjan_scc",
    "kosaraju_scc",
    "prim_mst",
    "kruskal_mst",
    "ford_fulkerson",
    "pagerank",
    "connected_components",
    "shortest_path_unweighted",
]
