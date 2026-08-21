"""
Graphs Subpackage
=================

Provides comprehensive graph algorithms for network analysis, traversal, and optimization:
- Traversal & search: bfs, dfs, bidirectional_bfs, connected_components
- Shortest paths: dijkstra, a_star, bellman_ford, floyd_warshall, shortest_path_unweighted
- Topological sorting & cycle detection: toposort, has_cycle, kahn_toposort
- Minimum Spanning Trees: prim_mst, kruskal_mst
- Connectivity & components: tarjan_scc, kosaraju_scc, find_bridges, articulation_points, is_bipartite
- Flow & centrality: ford_fulkerson (max flow), min_cut, pagerank, closeness_centrality
"""

from __future__ import annotations

from . import graphs
from .graphs import *  # noqa: F401, F403

__all__ = [
    "graphs",
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
    "page_rank_simple",
    "connected_components",
    "shortest_path_unweighted",
]
