#!/usr/bin/env python3
"""
Aion Physics — classical mechanics, thermo, EM, and simulation toolkit.

Examples
--------
>>> from aion.physics import simulate_pendulum, solve_physics_query
>>> result = solve_physics_query("kinetic energy mass=2 velocity=3")
>>> result.output_value
9.0
>>> sim = simulate_pendulum(1.0, 0.2, steps=100)
>>> sim.summary["small_angle_period_s"] > 0
True
"""

from . import (
    constants,
    constraints,
    electromagnetism,
    integrators,
    kinematics,
    mechanics,
    optics,
    pipeline,
    relativity,
    systems,
    thermo,
    units,
    waves,
)
from ._native import using_native_extension
from .pipeline import PhysicsQueryResult, solve_physics_query, supported_physics_tasks
from .systems import SimulationResult, projectile_motion, simulate_pendulum, simulate_spring_mass

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "constants",
    "constraints",
    "electromagnetism",
    "integrators",
    "kinematics",
    "mechanics",
    "optics",
    "pipeline",
    "relativity",
    "systems",
    "thermo",
    "units",
    "waves",
    "PhysicsQueryResult",
    "SimulationResult",
    "projectile_motion",
    "simulate_pendulum",
    "simulate_spring_mass",
    "solve_physics_query",
    "supported_physics_tasks",
    "using_native_extension",
]
