"""Physical AI agent tools (when physics kernels exist)."""

from __future__ import annotations

import os
from typing import Any, Dict, List

from ..tools.registry import ToolRegistry
from ..tools.schemas import function_tool


def physics_available(workspace_root: str) -> bool:
    return os.path.isdir(os.path.join(workspace_root, "aion", "physics"))


def register_physics_tools(registry: ToolRegistry) -> None:
    """Register stub physics tools when module is importable."""

    def simulate_stub(description: str = "") -> str:
        try:
            from ...physics import __version__  # type: ignore[attr-defined]

            return f"Physics kernel available (version {__version__}). Query: {description}"
        except ImportError:
            return "Physics module not installed. See docs/ADDING_PHYSICAL_AI.md"

    registry.register("physics_simulate", simulate_stub)


def physics_tool_schemas() -> List[Dict[str, Any]]:
    return [
        function_tool(
            "physics_simulate",
            "Run a physics simulation query when aion.physics is available.",
            properties={
                "description": {
                    "type": "string",
                    "description": "Natural language simulation request.",
                },
            },
        ),
    ]


def physics_system_hint(workspace_root: str) -> str:
    if physics_available(workspace_root):
        return (
            "\n\nPhysical AI: this workspace includes aion/physics/. "
            "Use physics_simulate for simulation tasks when relevant."
        )
    return ""
