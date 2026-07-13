"""Physical AI agent tools."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from ..tools.registry import ToolRegistry
from ..tools.schemas import function_tool


def physics_available(workspace_root: str) -> bool:
    return os.path.isdir(os.path.join(workspace_root, "aion", "physics"))


def _physics_cfg(cfg: Dict[str, Any]) -> Dict[str, Any]:
    section = cfg.get("physics") or {}
    return {
        "default_dt": float(section.get("default_dt", 0.01)),
        "max_steps": int(section.get("max_steps", 10000)),
        "prefer_native": bool(section.get("prefer_native", True)),
    }


def _downsample(rows: List[List[float]], limit: int = 100) -> List[List[float]]:
    if len(rows) <= limit:
        return rows
    step = max(1, len(rows) // limit)
    return rows[::step][:limit]


def register_physics_tools(registry: ToolRegistry, *, cfg: Dict[str, Any] | None = None) -> None:
    """Register physics tools when module is importable."""
    settings = _physics_cfg(cfg or {})

    def physics_query(description: str = "") -> str:
        from ...physics import solve_physics_query

        result = solve_physics_query(description)
        return json.dumps(
            {
                "task": result.task,
                "output_name": result.output_name,
                "output_value": result.output_value,
                "unit": result.unit,
                "inputs": result.inputs,
                "explanation": result.explanation,
            }
        )

    def physics_simulate_pendulum(
        length_m: float = 1.0,
        angle_deg: float = 15.0,
        dt: float | None = None,
        steps: int = 1000,
    ) -> str:
        from math import pi

        from ...physics import simulate_pendulum

        dt = dt if dt is not None else settings["default_dt"]
        steps = min(steps, settings["max_steps"])
        result = simulate_pendulum(
            length_m,
            angle_deg * pi / 180.0,
            dt=dt,
            steps=steps,
        )
        return json.dumps(
            {
                "summary": result.summary,
                "trajectory": _downsample(result.trajectory),
                "times": result.times[:: max(1, len(result.times) // 100)][:100],
            }
        )

    def physics_projectile(
        v0: float = 20.0,
        angle_deg: float = 45.0,
        dt: float | None = None,
        steps: int = 1000,
        drag_coeff: float = 0.0,
    ) -> str:
        from ...physics import projectile_motion

        dt = dt if dt is not None else settings["default_dt"]
        steps = min(steps, settings["max_steps"])
        result = projectile_motion(
            v0,
            angle_deg,
            dt=dt,
            steps=steps,
            drag_coeff=drag_coeff,
        )
        return json.dumps(
            {
                "summary": result.summary,
                "trajectory": _downsample(result.trajectory),
            }
        )

    registry.register("physics_query", physics_query)
    registry.register("physics_simulate_pendulum", physics_simulate_pendulum)
    registry.register("physics_projectile", physics_projectile)


def physics_tool_schemas() -> List[Dict[str, Any]]:
    return [
        function_tool(
            "physics_query",
            "Solve a natural-language physics query using deterministic formulas.",
            properties={
                "description": {
                    "type": "string",
                    "description": "Query e.g. 'kinetic energy mass=2 velocity=3'",
                },
            },
            required=["description"],
        ),
        function_tool(
            "physics_simulate_pendulum",
            "Simulate a simple pendulum and return summary + downsampled trajectory.",
            properties={
                "length_m": {"type": "number", "description": "Pendulum length in meters"},
                "angle_deg": {"type": "number", "description": "Initial angle in degrees"},
                "dt": {"type": "number", "description": "Time step in seconds"},
                "steps": {"type": "integer", "description": "Number of integration steps"},
            },
        ),
        function_tool(
            "physics_projectile",
            "Simulate projectile motion; returns range, height, and trajectory sample.",
            properties={
                "v0": {"type": "number", "description": "Initial speed m/s"},
                "angle_deg": {"type": "number", "description": "Launch angle degrees"},
                "dt": {"type": "number"},
                "steps": {"type": "integer"},
                "drag_coeff": {"type": "number", "description": "Linear drag coefficient (0 = none)"},
            },
        ),
    ]


def physics_system_hint(workspace_root: str) -> str:
    if physics_available(workspace_root):
        return (
            "\n\nPhysical AI: this workspace includes aion/physics/. "
            "Use physics_query, physics_simulate_pendulum, or physics_projectile "
            "for quantitative physics tasks."
        )
    return ""
