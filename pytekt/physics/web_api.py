"""JSON API helpers for the physics web dashboard."""

from __future__ import annotations

from math import pi
from typing import Any, Dict, List

from .pipeline import solve_physics_query, supported_physics_tasks


def library_info() -> Dict[str, Any]:
    from . import __version__
    from ._native import using_native_extension

    return {
        "app": "physics",
        "version": __version__,
        "native": using_native_extension(),
    }


def tasks_payload() -> Dict[str, Any]:
    return {"tasks": supported_physics_tasks()}


def query_payload(text: str) -> Dict[str, Any]:
    result = solve_physics_query(text)
    return {
        "task": result.task,
        "inputs": result.inputs,
        "output_name": result.output_name,
        "output_value": result.output_value,
        "unit": result.unit,
        "explanation": result.explanation,
    }


def pendulum_payload(
    *,
    length: float = 1.0,
    angle_deg: float = 15.0,
    dt: float = 0.01,
    steps: int = 1000,
) -> Dict[str, Any]:
    from .systems import simulate_pendulum

    steps = min(max(steps, 1), 20000)
    result = simulate_pendulum(length, angle_deg * pi / 180.0, dt=dt, steps=steps)
    return {
        "summary": result.summary,
        "times": result.times,
        "theta": [row[0] for row in result.trajectory],
        "omega": [row[1] for row in result.trajectory],
    }


def projectile_payload(
    *,
    v0: float = 20.0,
    angle_deg: float = 45.0,
    dt: float = 0.01,
    steps: int = 1000,
    drag: float = 0.0,
) -> Dict[str, Any]:
    from .systems import projectile_motion

    steps = min(max(steps, 1), 20000)
    result = projectile_motion(v0, angle_deg, dt=dt, steps=steps, drag_coeff=drag)
    return {
        "summary": result.summary,
        "x": [row[0] for row in result.trajectory],
        "y": [row[1] for row in result.trajectory],
        "times": result.times,
    }
