"""
Graph Algorithms
================

This module provides graph traversal and ordering algorithms for directed and
undirected graphs represented as adjacency lists. Implementations use only the
standard library and follow the same conventions as the rest of aion.algorithms:
correctness, clarity, and predictable behavior.

Scope
-----
- Breadth-first search (BFS): traverse or explore from a start node in level order.
- Depth-first search (DFS): traverse from a start node using a stack (iterative).
- Topological sort: linear ordering of vertices in a directed acyclic graph (DAG).

Graph representation
--------------------
Graphs are represented as adjacency lists: a mapping from node to list of neighbors.
- For BFS/DFS: graph[node] = list of adjacent nodes (any hashable type).
- For toposort: graph is directed; graph[node] = list of successors.
- Nodes must be hashable (e.g. int, str).

See also: aion/algorithms/README.md for full package documentation.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from collections import deque
import heapq


def bfs(graph: Dict[Any, List[Any]], start: Any) -> List[Any]:
    """
    Breadth-first search from a start node.

    Explores the graph level by level: start, then all nodes at distance 1,
    then distance 2, and so on. Uses a queue. Nodes are returned in BFS order.
    Nodes that are not reachable from start are not included.

    Parameters
    ----------
    graph : dict
        Adjacency list: graph[node] = list of neighbors. Undirected edges can be
        represented by listing each endpoint in the other's list.
    start : hashable
        The starting node (must be a key in graph or have no outgoing edges).

    Returns
    -------
    list
        List of nodes in BFS order (order of first visit).

    Raises
    ------
    KeyError
        If start is not in graph.

    Notes
    -----
    - Time complexity O(V + E); space O(V).
    - If start is not in graph, add it with an empty list: graph.setdefault(start, []).
    """
    if start not in graph:
        raise KeyError(f"Start node {start!r} not in graph")
    visited: Set[Any] = set()
    order: List[Any] = []
    queue: deque = deque([start])
    visited.add(start)
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def dfs(graph: Dict[Any, List[Any]], start: Any) -> List[Any]:
    """
    Depth-first search from a start node (iterative, stack-based).

    Explores as far as possible along each branch before backtracking.
    Returns nodes in the order they are first discovered (pre-order).
    Nodes not reachable from start are not included.

    Parameters
    ----------
    graph : dict
        Adjacency list: graph[node] = list of neighbors.
    start : hashable
        The starting node.

    Returns
    -------
    list
        List of nodes in DFS order (pre-order).

    Raises
    ------
    KeyError
        If start is not in graph.

    Notes
    -----
    - Time complexity O(V + E); space O(V).
    - Iterative implementation avoids recursion depth limits on large graphs.
    """
    if start not in graph:
        raise KeyError(f"Start node {start!r} not in graph")
    visited: Set[Any] = set()
    order: List[Any] = []
    stack: List[Any] = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in reversed(graph.get(node, [])):
            if neighbor not in visited:
                stack.append(neighbor)
    return order


def toposort(graph: Dict[Any, List[Any]]) -> List[Any]:
    """
    Topological sort of a directed acyclic graph (DAG).

    Returns a linear ordering of vertices such that for every directed edge
    (u, v), u comes before v. Uses Kahn's algorithm (in-degree based).
    If the graph has a cycle, ValueError is raised.

    Parameters
    ----------
    graph : dict
        Directed adjacency list: graph[node] = list of successors. All nodes
        that appear as keys or in any value list are considered vertices.

    Returns
    -------
    list
        One possible topological order of the vertices.

    Raises
    ------
    ValueError
        If the graph contains a cycle (not a DAG).

    Notes
    -----
    - Time complexity O(V + E).
    - Nodes with no outgoing edges may be omitted from graph; they are still
      included in the ordering if they appear as successors of others.
    """
    # Collect all vertices and compute in-degrees
    vertices: Set[Any] = set()
    in_degree: Dict[Any, int] = {}
    for node, neighbors in graph.items():
        vertices.add(node)
        in_degree.setdefault(node, 0)
        for v in neighbors:
            vertices.add(v)
            in_degree[v] = in_degree.get(v, 0) + 1
    # Queue of nodes with in-degree 0
    queue: deque = deque(u for u in vertices if in_degree.get(u, 0) == 0)
    order: List[Any] = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    if len(order) != len(vertices):
        raise ValueError("Graph contains a cycle; topological sort is undefined")
    return order


def dijkstra(
    graph: Dict[Any, List[Tuple[Any, float]]],
    start: Any,
) -> Dict[Any, float]:
    """
    Shortest-path distances from ``start`` on a graph with non-negative edges.

    ``graph[u]`` is a list of ``(v, weight)`` pairs. Unreachable nodes are omitted
    from the returned dict.
    """
    dist: Dict[Any, float] = {start: 0.0}
    pq: List[Tuple[float, Any]] = [(0.0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")):
            continue
        for v, w in graph.get(u, []):
            if w < 0:
                raise ValueError("dijkstra requires non-negative edge weights")
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def connected_components(graph: Dict[Any, List[Any]]) -> List[List[Any]]:
    """
    Undirected view: each directed edge ``u -> v`` is treated as mutual.
    Isolated vertices (keys with empty lists or nodes only appearing as neighbors)
    are included.
    """
    verts: Set[Any] = set(graph.keys())
    for u, nbrs in graph.items():
        verts.update(nbrs)
    und: Dict[Any, Set[Any]] = {v: set() for v in verts}
    for u, nbrs in graph.items():
        for v in nbrs:
            und[u].add(v)
            und[v].add(u)
    seen: Set[Any] = set()
    comps: List[List[Any]] = []
    for s in verts:
        if s in seen:
            continue
        comp: List[Any] = []
        stack = [s]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            comp.append(u)
            for v in und.get(u, ()):
                if v not in seen:
                    stack.append(v)
        comps.append(comp)
    return comps


def shortest_path_unweighted(
    graph: Dict[Any, List[Any]],
    start: Any,
    end: Any,
) -> Optional[List[Any]]:
    """
    BFS shortest path (fewest edges) in an unweighted directed graph.
    Returns vertex list including start and end, or None if unreachable.
    """
    if start == end:
        return [start]
    prev: Dict[Any, Any] = {}
    q: deque = deque([start])
    seen = {start}
    while q:
        u = q.popleft()
        for v in graph.get(u, []):
            if v in seen:
                continue
            seen.add(v)
            prev[v] = u
            if v == end:
                path = [end]
                cur = end
                while cur != start:
                    cur = prev[cur]
                    path.append(cur)
                path.reverse()
                return path
            q.append(v)
    return None
# --- Shortest Paths (Advanced) ---

def bellman_ford(graph: Dict[Any, List[Tuple[Any, float]]], start: Any) -> Tuple[Dict[Any, float], bool]:
    """Shortest path distances in a graph with negative edges. Returns (distances, has_negative_cycle)."""
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    nodes = list(graph.keys())
    
    for _ in range(len(nodes) - 1):
        for u in nodes:
            for v, weight in graph[u]:
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    
    for u in nodes:
        for v, weight in graph[u]:
            if distances[u] + weight < distances[v]:
                return distances, True
    return distances, False


def floyd_warshall(graph: Dict[Any, List[Tuple[Any, float]]]) -> Dict[Any, Dict[Any, float]]:
    """All-pairs shortest paths using Floyd-Warshall in O(V^3)."""
    nodes = list(graph.keys())
    dist = {u: {v: float('inf') for v in nodes} for u in nodes}
    for u in nodes:
        dist[u][u] = 0
        for v, weight in graph[u]:
            dist[u][v] = min(dist[u][v], weight)
            
    for k in nodes:
        for i in nodes:
            for j in nodes:
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist


def a_star_search(
    graph: Dict[Any, List[Tuple[Any, float]]], 
    start: Any, 
    end: Any, 
    heuristic: Dict[Any, float]
) -> Optional[List[Any]]:
    """Informed search algorithm (A*) to find the shortest path between start and end."""
    pq = [(0 + heuristic.get(start, 0), 0, start, [start])]
    visited = set()
    
    while pq:
        f, g, current, path = heapq.heappop(pq)
        if current == end:
            return path
        if current in visited:
            continue
        visited.add(current)
        for neighbor, weight in graph.get(current, []):
            if neighbor not in visited:
                new_g = g + weight
                new_f = new_g + heuristic.get(neighbor, 0)
                heapq.heappush(pq, (new_f, new_g, neighbor, path + [neighbor]))
    return None


def bidirectional_bfs(graph: Dict[Any, List[Any]], start: Any, end: Any) -> Optional[List[Any]]:
    """Meeting-in-the-middle BFS search between two nodes."""
    if start == end:
        return [start]
    q1, q2 = deque([start]), deque([end])
    v1, v2 = {start: None}, {end: None}
    
    while q1 and q2:
        # Expand from start side
        u1 = q1.popleft()
        for v in graph.get(u1, []):
            if v in v2: # Intersection!
                path = []
                curr = u1
                while curr is not None:
                    path.append(curr)
                    curr = v1[curr]
                path.reverse()
                curr = v
                while curr is not None:
                    path.append(curr)
                    curr = v2[curr]
                return path
            if v not in v1:
                v1[v] = u1
                q1.append(v)
        # Expand from end side (assuming undirected or transpose access)
        u2 = q2.popleft()
        for v in graph.get(u2, []): # Note: This needs the graph to be undirected or use a transpose for directed
            if v in v1:
                path = []
                curr = v
                while curr is not None:
                    path.append(curr)
                    curr = v1[curr]
                path.reverse()
                curr = u2
                while curr is not None:
                    path.append(curr)
                    curr = v2[curr]
                return path
            if v not in v2:
                v2[v] = u2
                q2.append(v)
    return None


# --- Connectivity & Components (Advanced) ---

def tarjan_scc(graph: Dict[Any, List[Any]]) -> List[List[Any]]:
    """Tarjan's algorithm for Strongly Connected Components (SCC) in O(V+E)."""
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = set()
    sccs = []

    def strongconnect(node):
        index[node] = lowlink[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in index:
                strongconnect(neighbor)
                lowlink[node] = min(lowlink[node], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[node] = min(lowlink[node], index[neighbor])

        if lowlink[node] == index[node]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            sccs.append(scc)

    for node in graph:
        if node not in index:
            strongconnect(node)
    return sccs


def kosaraju_scc(graph: Dict[Any, List[Any]]) -> List[List[Any]]:
    """Kosaraju's algorithm for Strongly Connected Components."""
    visited = set()
    stack = []
    
    def fill_order(node):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                fill_order(neighbor)
        stack.append(node)

    for node in graph:
        if node not in visited:
            fill_order(node)
            
    transpose = get_transpose(graph)
    visited.clear()
    sccs = []
    
    def dfs_collect(node, current_scc):
        visited.add(node)
        current_scc.append(node)
        for neighbor in transpose.get(node, []):
            if neighbor not in visited:
                dfs_collect(neighbor, current_scc)

    while stack:
        node = stack.pop()
        if node not in visited:
            current_scc = []
            dfs_collect(node, current_scc)
            sccs.append(current_scc)
    return sccs


def is_bipartite(graph: Dict[Any, List[Any]]) -> bool:
    """Check if a graph is bipartite (2-colorable) using BFS."""
    color = {}
    for node in graph:
        if node not in color:
            color[node] = 0
            queue = deque([node])
            while queue:
                u = queue.popleft()
                for v in graph.get(u, []):
                    if v not in color:
                        color[v] = 1 - color[u]
                        queue.append(v)
                    elif color[v] == color[u]:
                        return False
    return True


def find_bridges(graph: Dict[Any, List[Any]]) -> List[Tuple[Any, Any]]:
    """Find all bridges in an undirected graph."""
    timer = [0]
    visited = set()
    tin = {}
    low = {}
    bridges = []

    def dfs(u, p=-1):
        visited.add(u)
        tin[u] = low[u] = timer[0]
        timer[0] += 1
        for v in graph.get(u, []):
            if v == p:
                continue
            if v in visited:
                low[u] = min(low[u], tin[v])
            else:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > tin[u]:
                    bridges.append((u, v))

    for node in graph:
        if node not in visited:
            dfs(node)
    return bridges


def find_articulation_points(graph: Dict[Any, List[Any]]) -> Set[Any]:
    """Find all articulation points in an undirected graph."""
    timer = [0]
    visited = set()
    tin = {}
    low = {}
    points = set()

    def dfs(u, p=-1):
        visited.add(u)
        tin[u] = low[u] = timer[0]
        timer[0] += 1
        children = 0
        for v in graph.get(u, []):
            if v == p:
                continue
            if v in visited:
                low[u] = min(low[u], tin[v])
            else:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] >= tin[u] and p != -1:
                    points.add(u)
                children += 1
        return children

    for node in graph:
        if node not in visited:
            if dfs(node) > 1:
                points.add(node)
    return points


# --- Cycle Detection ---

def has_cycle_directed(graph: Dict[Any, List[Any]]) -> bool:
    """Check if a directed graph has a cycle using DFS coloring."""
    visited = set()
    stack = set()
    
    def dfs(u):
        visited.add(u)
        stack.add(u)
        for v in graph.get(u, []):
            if v not in visited:
                if dfs(v):
                    return True
            elif v in stack:
                return True
        stack.remove(u)
        return False

    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False


def has_cycle_undirected(graph: Dict[Any, List[Any]]) -> bool:
    """Check if an undirected graph has a cycle."""
    visited = set()
    
    def dfs(u, p=-1):
        visited.add(u)
        for v in graph.get(u, []):
            if v == p:
                continue
            if v in visited:
                return True
            if dfs(v, u):
                return True
        return False

    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False


# --- Minimum Spanning Trees (MST) ---

def prim_mst(graph: Dict[Any, List[Tuple[Any, float]]]) -> List[Tuple[Any, Any, float]]:
    """Prim's algorithm to find the MST of a weighted undirected graph."""
    if not graph:
        return []
    start_node = next(iter(graph))
    mst = []
    visited = {start_node}
    edges = [(weight, start_node, neighbor) for neighbor, weight in graph[start_node]]
    heapq.heapify(edges)
    
    while edges:
        weight, u, v = heapq.heappop(edges)
        if v not in visited:
            visited.add(v)
            mst.append((u, v, weight))
            for next_neighbor, next_weight in graph.get(v, []):
                if next_neighbor not in visited:
                    heapq.heappush(edges, (next_weight, v, next_neighbor))
    return mst


def kruskal_mst(graph: Dict[Any, List[Tuple[Any, float]]]) -> List[Tuple[Any, Any, float]]:
    """Kruskal's algorithm for MST using Disjoint Set Union (DSU)."""
    parent = {node: node for node in graph}
    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]
    
    def union(i, j):
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True
        return False

    all_edges = []
    for u in graph:
        for v, weight in graph[u]:
            all_edges.append((weight, u, v))
    all_edges.sort()
    
    mst = []
    for weight, u, v in all_edges:
        if union(u, v):
            mst.append((u, v, weight))
    return mst


# --- Network Flow ---

def ford_fulkerson(graph: Dict[Any, Dict[Any, float]], source: Any, sink: Any) -> float:
    """Find the maximum flow in a network using the Edmonds-Karp implementation."""
    # Build residual graph
    residual = {u: dict(v_dict) for u, v_dict in graph.items()}
    max_flow = 0
    
    while True:
        # Find path using BFS
        parent = {source: None}
        queue = deque([source])
        path_found = False
        while queue:
            u = queue.popleft()
            for v, cap in residual.get(u, {}).items():
                if v not in parent and cap > 0:
                    parent[v] = u
                    queue.append(v)
                    if v == sink:
                        path_found = True
                        break
            if path_found:
                break
        
        if not path_found:
            break
        
        # Determine bottleneck capacity
        path_flow = float('inf')
        s = sink
        while s != source:
            path_flow = min(path_flow, residual[parent[s]][s])
            s = parent[s]
            
        # Update residual capacities
        max_flow += path_flow
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow
            residual.setdefault(v, {})
            residual[v][u] = residual[v].get(u, 0) + path_flow
            v = parent[v]
            
    return max_flow


# --- Analysis & Centrality ---

def degree_centrality(graph: Dict[Any, List[Any]]) -> Dict[Any, float]:
    """Calculate the normalized degree centrality for all nodes."""
    n = len(graph)
    if n <= 1:
        return {node: 0.0 for node in graph}
    return {node: len(neighbors) / (n - 1) for node, neighbors in graph.items()}


def closeness_centrality(graph: Dict[Any, List[Any]]) -> Dict[Any, float]:
    """Calculate the closeness centrality for all nodes."""
    centrality = {}
    nodes = list(graph.keys())
    for u in nodes:
        # Use BFS to find shortest paths in unweighted graph
        dists = {u: 0}
        queue = deque([u])
        while queue:
            curr = queue.popleft()
            for v in graph.get(curr, []):
                if v not in dists:
                    dists[v] = dists[curr] + 1
                    queue.append(v)
        
        sum_dists = sum(dists.values())
        if sum_dists > 0 and len(dists) > 1:
            centrality[u] = (len(dists) - 1) / sum_dists
        else:
            centrality[u] = 0.0
    return centrality


def page_rank_simple(graph: Dict[Any, List[Any]], iterations: int = 10, d: float = 0.85) -> Dict[Any, float]:
    """A simplified PageRank algorithm for node importance ranking."""
    nodes = list(graph.keys())
    n = len(nodes)
    if n == 0:
        return {}
    rank = {node: 1.0 / n for node in nodes}
    
    for _ in range(iterations):
        new_rank = {node: (1 - d) / n for node in nodes}
        for u in nodes:
            neighbors = graph.get(u, [])
            if not neighbors:
                for v in nodes:
                    new_rank[v] += d * rank[u] / n
            else:
                for v in neighbors:
                    new_rank[v] += d * rank[u] / len(neighbors)
        rank = new_rank
    return rank


# --- Utilities & Advanced Search ---

def get_transpose(graph: Dict[Any, List[Any]]) -> Dict[Any, List[Any]]:
    """Return a new graph with all edges reversed."""
    transpose = {node: [] for node in graph}
    for u, neighbors in graph.items():
        for v in neighbors:
            transpose.setdefault(v, [])
            transpose[v].append(u)
    return transpose


def bron_kerbosch(graph: Dict[Any, Set[Any]], r: Set[Any], p: Set[Any], x: Set[Any], cliques: List[Set[Any]]):
    """Bron-Kerbosch algorithm with pivoting to find all maximal cliques."""
    if not p and not x:
        cliques.append(r)
        return
    if not p:
        return
    
    pivot = max(p | x, key=lambda u: len(graph.get(u, set()) & p))
    for v in list(p - graph.get(pivot, set())):
        neighbors = graph.get(v, set())
        bron_kerbosch(graph, r | {v}, p & neighbors, x & neighbors, cliques)
        p.remove(v)
        x.add(v)


def graph_diameter(graph: Dict[Any, List[Any]]) -> int:
    """Find the diameter (longest shortest path) of an unweighted graph."""
    max_dist = 0
    for node in graph:
        # Use BFS for each node
        dists = {node: 0}
        queue = deque([node])
        while queue:
            u = queue.popleft()
            max_dist = max(max_dist, dists[u])
            for v in graph.get(u, []):
                if v not in dists:
                    dists[v] = dists[u] + 1
                    queue.append(v)
    return max_dist


def find_all_paths(graph: Dict[Any, List[Any]], start: Any, end: Any, path: List[Any] = []) -> List[List[Any]]:
    """Find all simple paths between start and end node."""
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths
