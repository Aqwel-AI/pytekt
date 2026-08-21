"""Union-Find (Disjoint Set Union) algorithms (stdlib only)."""

from __future__ import annotations

from typing import Dict, List, Tuple

from pytekt.algorithms.catalog import register_algorithm


def _make_parent(n: int) -> List[int]:
    return list(range(n))


def _find(parent: List[int], x: int) -> int:
    while parent[x] != x:
        parent[parent[x]] = parent[x]
        x = parent[x]
    return x


def _union(parent: List[int], rank: List[int], a: int, b: int) -> bool:
    ra, rb = _find(parent, a), _find(parent, b)
    if ra == rb:
        return False
    if rank[ra] < rank[rb]:
        ra, rb = rb, ra
    parent[rb] = ra
    if rank[ra] == rank[rb]:
        rank[ra] += 1
    return True


@register_algorithm(category="union_find", summary="Initialize disjoint-set parent array for n elements.")
def make_disjoint_set(n: int) -> List[int]:
    return _make_parent(n)


@register_algorithm(category="union_find", summary="Find representative with path compression.")
def find_set(parent: List[int], x: int) -> int:
    return _find(parent, x)


@register_algorithm(category="union_find", summary="Union two sets by rank; returns whether merged.")
def union_sets(parent: List[int], rank: List[int], a: int, b: int) -> bool:
    return _union(parent, rank, a, b)


@register_algorithm(category="union_find", summary="Whether two elements are in the same connected component.")
def connected(parent: List[int], a: int, b: int) -> bool:
    return _find(parent, a) == _find(parent, b)


@register_algorithm(category="union_find", summary="Count connected components after union operations.")
def count_components(n: int, edges: List[Tuple[int, int]]) -> int:
    parent = _make_parent(n)
    rank = [0] * n
    for a, b in edges:
        _union(parent, rank, a, b)
    return len({_find(parent, i) for i in range(n)})


@register_algorithm(category="union_find", summary="Detect undirected cycle from edge list.")
def detect_cycle_undirected(n: int, edges: List[Tuple[int, int]]) -> bool:
    parent = _make_parent(n)
    rank = [0] * n
    for a, b in edges:
        if not _union(parent, rank, a, b):
            return True
    return False


@register_algorithm(category="union_find", summary="Kruskal MST total weight using union-find.")
def kruskal_mst_weight(n: int, edges: List[Tuple[int, int, int]]) -> int:
    parent = _make_parent(n)
    rank = [0] * n
    total = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if _union(parent, rank, u, v):
            total += w
    return total


@register_algorithm(category="union_find", summary="First redundant edge that creates a cycle.")
def redundant_connection(edges: List[Tuple[int, int]]) -> Tuple[int, int]:
    max_node = max(max(u, v) for u, v in edges)
    parent = _make_parent(max_node + 1)
    rank = [0] * (max_node + 1)
    for u, v in edges:
        if not _union(parent, rank, u - 1, v - 1):
            return u, v
    raise ValueError("no redundant edge")


@register_algorithm(category="union_find", summary="Number of friend circles in adjacency matrix.")
def friend_circles_count(is_connected: List[List[int]]) -> int:
    n = len(is_connected)
    parent = _make_parent(n)
    rank = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j]:
                _union(parent, rank, i, j)
    return len({_find(parent, i) for i in range(n)})


@register_algorithm(category="union_find", summary="Whether equality equations a==b are satisfiable with != constraints.")
def equations_satisfiable(equalities: List[Tuple[str, str]], inequalities: List[Tuple[str, str]]) -> bool:
    parent: Dict[str, str] = {}
    rank: Dict[str, int] = {}

    def ensure(x: str) -> None:
        if x not in parent:
            parent[x] = x
            rank[x] = 0

    def find(x: str) -> str:
        ensure(x)
        while parent[x] != x:
            parent[parent[x]] = parent[x]
            x = parent[x]
        return x

    def unite(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    for a, b in equalities:
        unite(a, b)
    for a, b in inequalities:
        if find(a) == find(b):
            return False
    return True


@register_algorithm(category="union_find", summary="Count regions where adjacent cells differ by at most threshold.")
def regions_by_threshold(grid: List[List[int]], threshold: int) -> int:
    rows, cols = len(grid), len(grid[0])
    parent = [i for i in range(rows * cols)]
    rank = [0] * rows * cols

    def idx(r: int, c: int) -> int:
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0)):
                nr, nc = r + dr, c + dc
                if nr < rows and nc < cols and abs(grid[r][c] - grid[nr][nc]) <= threshold:
                    _union(parent, rank, idx(r, c), idx(nr, nc))
    return len({_find(parent, i) for i in range(rows * cols)})


@register_algorithm(category="union_find", summary="Kruskal MST edge list (u, v, weight).")
def kruskal_mst_edges(n: int, edges: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
    parent = _make_parent(n)
    rank = [0] * n
    mst: List[Tuple[int, int, int]] = []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if _union(parent, rank, u, v):
            mst.append((u, v, w))
    return mst


