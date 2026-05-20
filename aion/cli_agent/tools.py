"""Coding-agent tool registry and OpenAI tool schemas."""

from __future__ import annotations

from typing import Any, Dict, List

from ..tools.code_agent import (
    edit_file,
    glob_search,
    grep_search,
    list_files,
    read_file,
    run_command,
    write_file,
)
from ..tools.registry import ToolRegistry
from ..tools.schemas import function_tool
from ..tools.workspace import Workspace


def build_tool_registry(*, workspace_root: str, is_trusted: bool) -> ToolRegistry:
    ws = Workspace(workspace_root)
    registry = ToolRegistry()

    registry.register("read_file", lambda path, offset=1, limit=500: read_file(ws, path, offset, limit))
    registry.register("list_files", lambda path=".", recursive=False: list_files(ws, path, recursive=recursive))
    registry.register("grep", lambda pattern, path=".", glob="*": grep_search(ws, pattern, path, glob))
    registry.register("glob", lambda pattern: glob_search(ws, pattern))

    if is_trusted:
        registry.register("write_file", lambda path, content: write_file(ws, path, content))
        registry.register(
            "edit_file",
            lambda path, old_string, new_string: edit_file(ws, path, old_string, new_string),
        )
        registry.register(
            "run_command",
            lambda command, timeout=60: run_command(ws, command, timeout),
        )

    return registry


def tools_schema(*, is_trusted: bool) -> List[Dict[str, Any]]:
    tools = [
        function_tool(
            "read_file",
            "Read a source file with line numbers. Use before editing.",
            properties={
                "path": {"type": "string", "description": "File path relative to project root."},
                "offset": {
                    "type": "integer",
                    "description": "1-based line to start reading (default 1).",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max lines to read (default 500).",
                },
            },
            required=["path"],
        ),
        function_tool(
            "list_files",
            "List files in a directory.",
            properties={
                "path": {"type": "string", "description": "Directory path (default .)."},
                "recursive": {
                    "type": "boolean",
                    "description": "List all files recursively (default false).",
                },
            },
        ),
        function_tool(
            "grep",
            "Search file contents with a regex pattern.",
            properties={
                "pattern": {"type": "string", "description": "Regex pattern to search for."},
                "path": {"type": "string", "description": "File or directory (default .)."},
                "glob": {
                    "type": "string",
                    "description": "Filename glob filter, e.g. *.py (default *).",
                },
            },
            required=["pattern"],
        ),
        function_tool(
            "glob",
            "Find files by glob pattern, e.g. **/*.py or src/**/*.ts.",
            properties={
                "pattern": {"type": "string", "description": "Glob pattern."},
            },
            required=["pattern"],
        ),
    ]
    if is_trusted:
        tools.extend(
            [
                function_tool(
                    "write_file",
                    "Create or overwrite an entire file. Prefer edit_file for small changes.",
                    properties={
                        "path": {"type": "string", "description": "File path."},
                        "content": {"type": "string", "description": "Full file content."},
                    },
                    required=["path", "content"],
                ),
                function_tool(
                    "edit_file",
                    "Replace exact text in a file (old_string must appear once). Read the file first.",
                    properties={
                        "path": {"type": "string", "description": "File path."},
                        "old_string": {
                            "type": "string",
                            "description": "Exact text to replace (include enough context to be unique).",
                        },
                        "new_string": {
                            "type": "string",
                            "description": "Replacement text.",
                        },
                    },
                    required=["path", "old_string", "new_string"],
                ),
                function_tool(
                    "run_command",
                    "Run a shell command in the project directory (tests, pip, git, etc.).",
                    properties={
                        "command": {"type": "string", "description": "Shell command to run."},
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds (default 60, max 120).",
                        },
                    },
                    required=["command"],
                ),
            ]
        )
    return tools
