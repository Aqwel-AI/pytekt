"""Specialist subagents: explore / edit / test, plus parallel /multi."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from ..agents.memory import SlidingWindowMemory
from ..agents.react import ReActAgent
from ..agents.skills import SKILL_PROMPTS
from ..tools.code_agent import (
    edit_file,
    grep_search,
    list_files,
    read_file,
    run_command,
    write_file,
)
from ..tools.registry import ToolRegistry
from ..tools.schemas import function_tool
from ..tools.workspace import Workspace


def _read_only_registry(workspace_root: str) -> ToolRegistry:
    ws = Workspace(workspace_root)
    reg = ToolRegistry()
    reg.register("read_file", lambda path, offset=1, limit=500: read_file(ws, path, offset, limit))
    reg.register("list_files", lambda path=".", recursive=False: list_files(ws, path, recursive=recursive))
    reg.register("grep", lambda pattern, path=".", glob="*": grep_search(ws, pattern, path, glob))
    return reg


def _edit_registry(workspace_root: str) -> ToolRegistry:
    ws = Workspace(workspace_root)
    reg = _read_only_registry(workspace_root)
    # Re-bind workspace for write tools (new Workspace ok — same root)
    ws = Workspace(workspace_root)
    reg.register("write_file", lambda path, content: write_file(ws, path, content))
    reg.register(
        "edit_file",
        lambda path, old_string, new_string: edit_file(ws, path, old_string, new_string),
    )
    return reg


def _test_registry(workspace_root: str) -> ToolRegistry:
    ws = Workspace(workspace_root)
    reg = _read_only_registry(workspace_root)
    reg.register("run_command", lambda command, timeout=60: run_command(ws, command, timeout))
    return reg


_READ_TOOLS = [
    function_tool(
        "read_file",
        "Read a file.",
        properties={"path": {"type": "string"}},
        required=["path"],
    ),
    function_tool(
        "list_files",
        "List files in a directory.",
        properties={
            "path": {"type": "string"},
            "recursive": {"type": "boolean"},
        },
    ),
    function_tool(
        "grep",
        "Search files.",
        properties={
            "pattern": {"type": "string"},
            "path": {"type": "string"},
            "glob": {"type": "string"},
        },
        required=["pattern"],
    ),
]

_EDIT_TOOLS = _READ_TOOLS + [
    function_tool(
        "write_file",
        "Write a file.",
        properties={
            "path": {"type": "string"},
            "content": {"type": "string"},
        },
        required=["path", "content"],
    ),
    function_tool(
        "edit_file",
        "Replace text in a file.",
        properties={
            "path": {"type": "string"},
            "old_string": {"type": "string"},
            "new_string": {"type": "string"},
        },
        required=["path", "old_string", "new_string"],
    ),
]

_TEST_TOOLS = _READ_TOOLS + [
    function_tool(
        "run_command",
        "Run a shell command in the workspace.",
        properties={
            "command": {"type": "string"},
            "timeout": {"type": "integer"},
        },
        required=["command"],
    ),
]

_SPECIALIST_PROMPTS = {
    "explore": (
        "You are an explore/research subagent. Use read-only tools to answer briefly "
        "with evidence from the codebase."
    ),
    "edit": (
        SKILL_PROMPTS.get("code", "")
        + "\nUse write_file/edit_file to apply minimal, correct changes. Read before edit."
    ),
    "test": (
        SKILL_PROMPTS.get("debug", "")
        + "\nFocus on running tests and diagnosing failures with read_file/grep/run_command."
    ),
}


def run_specialist_subagent(
    provider: Any,
    query: str,
    *,
    kind: str,
    workspace_root: str,
    max_steps: int = 5,
    test_command: Optional[str] = None,
) -> str:
    """Run explore | edit | test specialist ReAct loop."""
    kind = (kind or "explore").lower().strip()
    if kind in ("research", "explore", "read"):
        kind = "explore"
        registry = _read_only_registry(workspace_root)
        tools = _READ_TOOLS
    elif kind in ("edit", "code", "write"):
        kind = "edit"
        registry = _edit_registry(workspace_root)
        tools = _EDIT_TOOLS
    elif kind in ("test", "debug"):
        kind = "test"
        registry = _test_registry(workspace_root)
        tools = _TEST_TOOLS
        if test_command and "run" not in query.lower() and "test" not in query.lower():
            query = f"{query}\n\nPrefer this test command when appropriate: {test_command}"
    else:
        raise ValueError(f"Unknown specialist kind: {kind!r}")

    agent = ReActAgent(
        provider=provider,
        registry=registry,
        tools=tools,
        system_prompt=_SPECIALIST_PROMPTS[kind],
        memory=SlidingWindowMemory(window_size=20),
        max_steps=max_steps,
    )
    agent.force_tools = True  # type: ignore[attr-defined]
    return agent.run(query)


def run_research_subagent(
    provider: Any,
    query: str,
    *,
    workspace_root: str,
    max_steps: int = 5,
) -> str:
    """Short ReAct loop with read-only tools; returns summary text."""
    return run_specialist_subagent(
        provider,
        query,
        kind="explore",
        workspace_root=workspace_root,
        max_steps=max_steps,
    )


def run_parallel_specialists(
    provider: Any,
    task: str,
    *,
    workspace_root: str,
    kinds: Optional[List[str]] = None,
    max_steps: int = 5,
    test_command: Optional[str] = None,
) -> str:
    """
    Run explore + edit + test specialists in parallel and synthesize one summary.
    """
    selected = kinds or ["explore", "edit", "test"]
    results: Dict[str, str] = {}

    def _run(kind: str) -> Tuple[str, str]:
        try:
            text = run_specialist_subagent(
                provider,
                task,
                kind=kind,
                workspace_root=workspace_root,
                max_steps=max_steps,
                test_command=test_command,
            )
            return kind, text
        except Exception as e:  # noqa: BLE001
            return kind, f"[error] {e}"

    with ThreadPoolExecutor(max_workers=max(1, len(selected))) as pool:
        futures = [pool.submit(_run, k) for k in selected]
        for fut in as_completed(futures):
            kind, text = fut.result()
            results[kind] = text

    sections = []
    for kind in selected:
        body = results.get(kind, "").strip() or "(no output)"
        sections.append(f"## {kind}\n{body}")
    return (
        f"Parallel specialists for: {task}\n\n"
        + "\n\n".join(sections)
        + "\n\n## synthesis\n"
        "Combine the explore findings, edit outcomes, and test results above. "
        "Prefer concrete next steps if work remains."
    )
