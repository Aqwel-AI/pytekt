from aion.algorithms import arrays, search, graphs


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
