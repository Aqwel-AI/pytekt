# Algorithms Catalog

The `pytekt.algorithms` package includes **570+** registered functions across **7 core domain packages** and **21 fine-grained categories**.

## Discover Algorithms

```python
from pytekt.algorithms import count_algorithms, list_algorithms, get_algorithm, categories

print(count_algorithms())  # 572+
print(categories())        # sorting, dynamic_programming, graphs, math, ...

# Run any registered algorithm by name
fn = get_algorithm("merge_sort")
assert fn([3, 1, 2]) == [1, 2, 3]

# Browse a category
for entry in list_algorithms("dynamic_programming")[:5]:
    print(entry.name, entry.summary)
```

## Domains and Categories

| Domain Package | Category Tag | Module File | ~Count |
|---|---|---|---|
| `pytekt.algorithms.searching` | `search` | `searching/search.py` | 44 |
| `pytekt.algorithms.data_structures` | `arrays` | `data_structures/arrays.py` | 42 |
| `pytekt.algorithms.data_structures` | `heaps` | `data_structures/heaps.py` | 20 |
| `pytekt.algorithms.data_structures` | `queues_stacks` | `data_structures/queues_stacks.py` | 15 |
| `pytekt.algorithms.data_structures` | `trees` | `data_structures/trees.py` | 35 |
| `pytekt.algorithms.data_structures` | `union_find` | `data_structures/union_find.py` | 12 |
| `pytekt.algorithms.data_structures` | `hashing` | `data_structures/hashing.py` | 15 |
| `pytekt.algorithms.sorting` | `sorting` | `sorting/sorting.py` | 35 |
| `pytekt.algorithms.graphs` | `graphs` | `graphs/graphs.py` | 27 |
| `pytekt.algorithms.paradigms` | `dynamic_programming` | `paradigms/dynamic_programming.py` | 45 |
| `pytekt.algorithms.paradigms` | `greedy` | `paradigms/greedy.py` | 25 |
| `pytekt.algorithms.paradigms` | `backtracking` | `paradigms/backtracking.py` | 30 |
| `pytekt.algorithms.paradigms` | `sliding_window` | `paradigms/sliding_window.py` | 20 |
| `pytekt.algorithms.paradigms` | `two_pointers` | `paradigms/two_pointers.py` | 20 |
| `pytekt.algorithms.paradigms` | `bit` | `paradigms/bit_manipulation.py` | 25 |
| `pytekt.algorithms.mathematics` | `math` | `mathematics/math_number_theory.py` | 40 |
| `pytekt.algorithms.mathematics` | `geometry` | `mathematics/geometry.py` | 25 |
| `pytekt.algorithms.mathematics` | `numerical` | `mathematics/numerical.py` | 25 |
| `pytekt.algorithms.mathematics` | `statistics` | `mathematics/statistics.py` | 25 |
| `pytekt.algorithms.strings` | `strings` | `strings/strings.py` | 35 |
| `pytekt.algorithms.strings` | `compression` | `strings/compression.py` | 12 |

See [README.md](README.md) for architectural design and curated exports.
