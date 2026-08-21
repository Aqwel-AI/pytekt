# pytekt.algorithms — High-Performance Algorithmic Suite

## 1. Overview

The **pytekt.algorithms** package is a professional, domain-structured algorithmic library designed for high-performance sequence analysis, graph theory, mathematical reasoning, combinatorial optimization, and data structures. It provides over 570+ tested, zero-dependency algorithmic primitives.

---

## 2. Package Architecture

The package is organized into 7 clean domain categories with full subpackage modularity and unified catalog discovery:

```
pytekt/algorithms/
├── data_structures/     # Arrays, Heaps, Stacks/Queues, Trees, Union-Find, Hashing
├── searching/           # Sequence search, Selection, BS on Answer, String pattern matching
├── sorting/             # Comparison, Distribution, and Specialized sorting algorithms
├── graphs/              # Traversal, Shortest paths, MST, Network flow, Centrality, SCC
├── paradigms/           # Dynamic programming, Greedy, Backtracking, Two pointers, Sliding window, Bit
├── mathematics/         # Number theory, Numerical methods, Computational geometry, Statistics
├── strings/             # String transformations, Edit distance, Compression (Huffman, LZW, RLE)
├── catalog.py           # Algorithmic discovery and metadata registry
└── _registry.py         # Subpackage auto-loader and bootstrap
```

### Domain Taxonomy

| Domain Category | Subpackage | Key Modules / Primitives | Functions |
|---|---|---|---|
| **Data Structures** | `pytekt.algorithms.data_structures` | `arrays`, `heaps`, `queues_stacks`, `trees`, `union_find`, `hashing` | ~160 |
| **Searching** | `pytekt.algorithms.searching` | `search` (Binary, Jump, Ternary, KMP, Quickselect, Optimization) | ~45 |
| **Sorting** | `pytekt.algorithms.sorting` | `sorting` (Quick, Merge, Heap, TimSort, Radix, Counting, Shell) | ~35 |
| **Graphs** | `pytekt.algorithms.graphs` | `graphs` (Dijkstra, A*, Floyd-Warshall, Tarjan SCC, Kruskal, Flow) | ~30 |
| **Paradigms** | `pytekt.algorithms.paradigms` | `dynamic_programming`, `greedy`, `backtracking`, `sliding_window`, `two_pointers`, `bit_manipulation` | ~165 |
| **Mathematics** | `pytekt.algorithms.mathematics` | `math_number_theory`, `numerical`, `geometry`, `statistics` | ~115 |
| **Strings & Compression** | `pytekt.algorithms.strings` | `strings`, `compression` (Huffman, LZW, RLE, Levenshtein, Suffix) | ~45 |

---

## 3. Usage & Import Styles

### 3.1 Domain Subpackage Imports (Recommended)

```python
# Import from clean category subpackages
from pytekt.algorithms.data_structures import arrays, trees, heaps
from pytekt.algorithms.searching import binary_search, kmp_search
from pytekt.algorithms.sorting import quick_sort, merge_sort
from pytekt.algorithms.graphs import dijkstra, bfs, dfs
from pytekt.algorithms.paradigms import dynamic_programming, greedy, backtracking
from pytekt.algorithms.mathematics import math_number_theory, numerical, geometry
from pytekt.algorithms.strings import compression, strings
```

### 3.2 Curated Top-Level Access

```python
from pytekt.algorithms import (
    binary_search,
    dijkstra,
    flatten_array,
    kmp_search,
    moving_average,
)

# Binary Search
idx = binary_search([10, 20, 30, 40, 50], 30)  # 2

# Graph Shortest Path
graph = {
    'A': [('B', 1), ('C', 4)],
    'B': [('C', 2), ('D', 5)],
    'C': [('D', 1)],
    'D': [],
}
distances, paths = dijkstra(graph, 'A')
```

### 3.3 Dynamic Catalog Discovery

```python
from pytekt.algorithms import count_algorithms, categories, list_algorithms, get_algorithm

# Total number of registered algorithms
print(count_algorithms())  # 572+

# All registered categories
print(categories())

# Inspect a category
dp_algos = list_algorithms("dynamic_programming")
for entry in dp_algos[:3]:
    print(f"[{entry.category}] {entry.name}: {entry.summary}")

# Execute dynamically by name
fn = get_algorithm("lcs_length")
assert fn("abcde", "ace") == 3
```

---

## 4. Design Principles

- **Zero External Dependencies**: 100% Python standard library for core algorithms.
- **Strict Typing**: Full type annotations (`TypeVar`, `Optional`, `List`, `Dict`, `Tuple`).
- **Optimal Time & Space Complexities**: Standard mathematical efficiency across all routines.
- **Backward Compatibility**: Supports legacy module imports through `pytekt.algorithms.*` aliases.
