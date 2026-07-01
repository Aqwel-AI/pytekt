#!/usr/bin/env python3
"""
Aqwel-Aion - Physics MVP
========================

Minimal physics and physical-AI toolkit for quick simulation, teaching, and
research prototyping.
"""

from . import constants
from . import integrators
from . import mechanics
from . import pipeline
from . import thermo
from . import units
from .pipeline import PhysicsQueryResult, solve_physics_query

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "constants",
    "integrators",
    "mechanics",
    "pipeline",
    "thermo",
    "units",
    "PhysicsQueryResult",
    "solve_physics_query",
]
