from pytekt.algorithms import arrays, search, graphs
from pytekt.algorithms import (
    data_structures,
    searching,
    sorting,
    graphs as graphs_subpkg,
    paradigms,
    mathematics,
    strings,
)


def test_arrays_basic():
    assert arrays.flatten_array([[1, 2], [3]]) == [1, 2, 3]
    assert arrays.chunk_array([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert arrays.remove_duplicates([1, 2, 1, 3]) == [1, 2, 3]


def test_search_basic():
    arr = [1, 3, 3, 5]
    idx = search.binary_search(arr, 3)
    assert idx in (1, 2)
    assert search.lower_bound(arr, 3) == 1
    assert search.upper_bound(arr, 3) == 3


def test_graphs_algorithms():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    assert graphs.bfs(graph, "a") == ["a", "b", "c", "d"]
    assert graphs.dfs(graph, "a")[0] == "a"
    order = graphs.toposort(graph)
    pos = {node: i for i, node in enumerate(order)}
    assert pos["a"] < pos["b"]
    assert pos["a"] < pos["c"]
    assert pos["b"] < pos["d"]
    assert pos["c"] < pos["d"]

    weighted = {
        "a": [("b", 1.0), ("c", 4.0)],
        "b": [("c", 2.0), ("d", 5.0)],
        "c": [("d", 1.0)],
        "d": [],
    }
    dist = graphs.dijkstra(weighted, "a")
    assert dist["d"] == 4.0


def test_subpackages_structure():
    # data_structures
    assert data_structures.arrays.flatten_array([[10], [20]]) == [10, 20]
    assert hasattr(data_structures, "heaps")
    assert hasattr(data_structures, "trees")
    assert hasattr(data_structures, "queues_stacks")
    assert hasattr(data_structures, "union_find")
    assert hasattr(data_structures, "hashing")

    # searching
    assert searching.binary_search([1, 2, 3, 4], 3) == 2
    assert searching.kmp_search("ABC ABCDAB", "ABCD") == [4]

    # sorting
    assert sorting.quick_sort([5, 2, 8, 1]) == [1, 2, 5, 8]
    assert sorting.merge_sort([5, 2, 8, 1]) == [1, 2, 5, 8]

    # graphs
    g = {"1": ["2"], "2": ["3"], "3": []}
    assert graphs_subpkg.bfs(g, "1") == ["1", "2", "3"]

    # paradigms
    assert paradigms.dynamic_programming.lcs_length("abcde", "ace") == 3
    assert paradigms.greedy.fractional_knapsack([10, 20, 30], [60, 100, 120], 50) == 240.0

    # mathematics
    assert mathematics.math_number_theory.gcd(48, 18) == 6
    assert mathematics.math_number_theory.is_prime(17) is True

    # strings
    assert strings.strings.is_anagram("anagram", "nagaram") is True
    assert hasattr(strings, "compression")
    assert strings.compression.run_length_encode("AAABBBCC") == [("A", 3), ("B", 3), ("C", 2)]
