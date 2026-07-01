"""Explicit agent state for long-horizon execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentState:
    """Serializable state snapshot for an agent run."""

    goal: str = ""
    plan: List[str] = field(default_factory=list)
    current_step: int = 0
    status: str = "idle"
    artifacts_created: List[str] = field(default_factory=list)
    tool_history: List[Dict[str, Any]] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    final_answer: Optional[str] = None

    def start(self, goal: str, plan: Optional[List[str]] = None) -> None:
        """Initialize a new run state."""
        self.goal = goal
        self.plan = list(plan or [])
        self.current_step = 0
        self.status = "running"
        self.final_answer = None

    def record_tool_call(self, name: str, arguments_json: str, result: str) -> None:
        """Append one tool execution to the history."""
        self.tool_history.append(
            {"name": name, "arguments_json": arguments_json, "result": result}
        )

    def add_artifact(self, path: str) -> None:
        """Track a created or modified artifact path."""
        self.artifacts_created.append(path)

    def fail(self, message: str) -> None:
        """Record a failure and mark the run as degraded."""
        self.failures.append(message)
        self.status = "failed"

    def complete(self, final_answer: str) -> None:
        """Mark the run as complete."""
        self.final_answer = final_answer
        self.status = "completed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the state to a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Reconstruct state from a serialized dictionary."""
        return cls(**data)
