"""Policy controls for agent execution and tool usage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional, Set


@dataclass
class ToolPolicy:
    """Simple allow/deny policy for tools and side effects."""

    read_only: bool = False
    allow_network: bool = True
    require_approval_for_write: bool = False
    max_tool_calls: Optional[int] = None
    allowlist: Set[str] = field(default_factory=set)
    denylist: Set[str] = field(default_factory=set)
    write_tools: Set[str] = field(
        default_factory=lambda: {"write_file", "edit_file", "delete_file", "move_file"}
    )

    def __post_init__(self) -> None:
        self.allowlist = set(self.allowlist)
        self.denylist = set(self.denylist)
        self.write_tools = set(self.write_tools)

    @classmethod
    def from_lists(
        cls,
        *,
        allowlist: Optional[Iterable[str]] = None,
        denylist: Optional[Iterable[str]] = None,
        **kwargs,
    ) -> "ToolPolicy":
        """Convenience constructor from iterable tool lists."""
        return cls(
            allowlist=set(allowlist or []),
            denylist=set(denylist or []),
            **kwargs,
        )

    def validate_tool(self, tool_name: str, call_count: int = 0) -> Optional[str]:
        """Return a rejection reason when a tool call violates the policy."""
        if self.max_tool_calls is not None and call_count >= self.max_tool_calls:
            return "tool_call_budget_exceeded"
        if tool_name in self.denylist:
            return "tool_denied"
        if self.allowlist and tool_name not in self.allowlist:
            return "tool_not_in_allowlist"
        if self.read_only and tool_name in self.write_tools:
            return "read_only_policy"
        if self.require_approval_for_write and tool_name in self.write_tools:
            return "approval_required_for_write"
        return None
