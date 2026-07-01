"""DAG-style execution graph for agent plans."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class ExecutionNode:
    """One executable node in a task graph."""

    node_id: str
    run: Callable[[], str]
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"
    result: str = ""


class ExecutionGraph:
    """Execute a small acyclic graph of dependent tasks."""

    def __init__(self) -> None:
        self.nodes: Dict[str, ExecutionNode] = {}

    def add_node(self, node: ExecutionNode) -> None:
        """Add one node to the graph."""
        self.nodes[node.node_id] = node

    def execute(self) -> Dict[str, str]:
        """Execute the graph in topological order."""
        results: Dict[str, str] = {}
        remaining = set(self.nodes)
        while remaining:
            progressed = False
            for node_id in list(remaining):
                node = self.nodes[node_id]
                if all(dep in results for dep in node.depends_on):
                    node.status = "running"
                    node.result = node.run()
                    node.status = "done"
                    results[node_id] = node.result
                    remaining.remove(node_id)
                    progressed = True
            if not progressed:
                raise ValueError("Execution graph contains a cycle or missing dependency.")
        return results
