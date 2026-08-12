# Algorithms catalog

The `pytekt.algorithms` package now includes **570+** registered functions across 21 categories.

## Discover algorithms

```python
from pytekt.algorithms import count_algorithms, list_algorithms, get_algorithm, categories

print(count_algorithms())  # 570+
print(categories())        # sorting, dynamic_programming, graphs, ...

# Run any registered algorithm by name
fn = get_algorithm("merge_sort")
assert fn([3, 1, 2]) == [1, 2, 3]

# Browse a category
for entry in list_algorithms("dynamic_programming")[:5]:
    print(entry.name, entry.summary)
```

## Categories

| Category | Module | ~Count |
|----------|--------|--------|
| search | search.py | 44 |
| arrays | arrays.py | 42 |
| graphs | graphs.py | 27 |
| sorting | sorting.py | 35 |
| dynamic_programming | dynamic_programming.py | 45 |
| greedy | greedy.py | 25 |
| strings | strings.py | 35 |
| trees | trees.py | 35 |
| heaps | heaps.py | 20 |
| math | math_number_theory.py | 40 |
| geometry | geometry.py | 25 |
| bit | bit_manipulation.py | 25 |
| hashing | hashing.py | 15 |
| sliding_window | sliding_window.py | 20 |
| two_pointers | two_pointers.py | 20 |
| backtracking | backtracking.py | 30 |
| union_find | union_find.py | 12 |
| numerical | numerical.py | 25 |
| statistics | statistics.py | 25 |
| compression | compression.py | 12 |
| queues_stacks | queues_stacks.py | 15 |

See [README.md](README.md) for design principles and curated exports.
