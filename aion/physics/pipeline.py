#!/usr/bin/env python3
"""Minimal physical-AI query pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from . import mechanics, thermo


@dataclass
class PhysicsQueryResult:
    """Structured result returned by the physics MVP query router."""

    task: str
    inputs: Dict[str, float]
    output_name: str
    output_value: float
    unit: str
    explanation: str


def simulate_free_fall(*, height: float, gravity: float = 9.80665) -> Dict[str, float]:
    """Return time-to-impact and final speed for ideal free fall from rest."""
    if height < 0:
        raise ValueError("height must be non-negative")
    from math import sqrt

    time_seconds = sqrt((2.0 * height) / gravity) if height > 0 else 0.0
    impact_speed = gravity * time_seconds
    return {"time_seconds": time_seconds, "impact_speed_m_per_s": impact_speed}


def solve_physics_query(description: str) -> PhysicsQueryResult:
    """
    Solve a small set of natural-language physics tasks.

    This is the MVP “AI part”: a lightweight rule-based router that turns a
    human request into a concrete physics computation.
    """
    normalized = description.casefold()
    values = _extract_named_numbers(description)

    if "kinetic" in normalized and {"mass", "velocity"} <= values.keys():
        energy = mechanics.kinetic_energy(values["mass"], values["velocity"])
        return PhysicsQueryResult(
            task="kinetic_energy",
            inputs={"mass": values["mass"], "velocity": values["velocity"]},
            output_name="kinetic_energy",
            output_value=energy,
            unit="J",
            explanation="Computed kinetic energy using 0.5 * m * v^2.",
        )

    if "force" in normalized and {"mass", "acceleration"} <= values.keys():
        result = mechanics.force(values["mass"], values["acceleration"])
        return PhysicsQueryResult(
            task="force",
            inputs={"mass": values["mass"], "acceleration": values["acceleration"]},
            output_name="force",
            output_value=result,
            unit="N",
            explanation="Computed force using F = m * a.",
        )

    if "pressure" in normalized and {"moles", "temperature", "volume"} <= values.keys():
        pressure = thermo.ideal_gas_pressure(values["moles"], values["temperature"], values["volume"])
        return PhysicsQueryResult(
            task="ideal_gas_pressure",
            inputs={
                "moles": values["moles"],
                "temperature": values["temperature"],
                "volume": values["volume"],
            },
            output_name="pressure",
            output_value=pressure,
            unit="Pa",
            explanation="Computed pressure using the ideal gas law P = nRT / V.",
        )

    if "free fall" in normalized and "height" in values:
        result = simulate_free_fall(height=values["height"])
        return PhysicsQueryResult(
            task="free_fall",
            inputs={"height": values["height"]},
            output_name="impact_speed_m_per_s",
            output_value=result["impact_speed_m_per_s"],
            unit="m/s",
            explanation="Solved ideal free fall from rest and returned the impact speed.",
        )

    raise ValueError(
        "Unsupported physics query. Supported tasks currently include force, "
        "kinetic energy, ideal gas pressure, and free fall."
    )


def _extract_named_numbers(description: str) -> Dict[str, float]:
    """Extract ``name=value`` style parameters from natural-language requests."""
    import re

    matches = re.findall(r"([a-zA-Z_]+)\s*=\s*([-+]?(?:\d*\.\d+|\d+))", description)
    return {name.casefold(): float(value) for name, value in matches}


def supported_physics_tasks() -> List[str]:
    """Return the tasks understood by the physics MVP router."""
    return [
        "force: mass=<kg>, acceleration=<m/s^2>",
        "kinetic energy: mass=<kg>, velocity=<m/s>",
        "ideal gas pressure: moles=<mol>, temperature=<K>, volume=<m^3>",
        "free fall: height=<m>",
    ]
