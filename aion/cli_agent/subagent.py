"""Subagent for short read-only research loops."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from ..agents.react import ReActAgent
from ..agents.memory import SlidingWindowMemory
from ..tools.registry import ToolRegistry
from ..tools.code_agent import grep_search, list_files, read_file
from ..tools.workspace import Workspace


def _read_only_registry(workspace_root: str) -> ToolRegistry:
    ws = Workspace(workspace_root)
    reg = ToolRegistry()
    reg.register("read_file", lambda path, offset=1, limit=500: read_file(ws, path, offset, limit))
    reg.register("list_files", lambda path=".", recursive=False: list_files(ws, path, recursive=recursive))
    reg.register("grep", lambda pattern, path=".", glob="*": grep_search(ws, pattern, path, glob))
    return reg


_READ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"},
                },
                "required": ["pattern"],
            },
        },
    },
]


def run_research_subagent(
    provider: Any,
    query: str,
    *,
    workspace_root: str,
    max_steps: int = 5,
) -> str:
    """Short ReAct loop with read-only tools; returns summary text."""
    registry = _read_only_registry(workspace_root)
    agent = ReActAgent(
        provider=provider,
        registry=registry,
        tools=_READ_TOOLS,
        system_prompt=(
            "You are a research subagent. Use read-only tools to answer the query briefly."
        ),
        memory=SlidingWindowMemory(window_size=20),
        max_steps=max_steps,
    )
    agent.force_tools = True  # type: ignore[attr-defined]
    return agent.run(query)
