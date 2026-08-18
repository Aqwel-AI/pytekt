#!/usr/bin/env python3
"""Special relativity helpers (educational precision)."""

from __future__ import annotations

from .constants import SPEED_OF_LIGHT


def lorentz_factor(velocity: float) -> float:
    """Return Lorentz factor ``gamma = 1 / sqrt(1 - v^2/c^2)``."""
    if abs(velocity) >= SPEED_OF_LIGHT:
        raise ValueError("velocity must be less than the speed of light")
    beta = velocity / SPEED_OF_LIGHT
    return 1.0 / (1.0 - beta * beta) ** 0.5


def time_dilation(proper_time: float, velocity: float) -> float:
    """Return dilated time ``t = gamma * tau``."""
    return lorentz_factor(velocity) * proper_time


def length_contraction(proper_length: float, velocity: float) -> float:
    """Return contracted length ``L = L0 / gamma``."""
    return proper_length / lorentz_factor(velocity)


def relativistic_energy(mass: float, velocity: float) -> float:
    """Return total relativistic energy ``gamma * m * c^2``."""
    gamma = lorentz_factor(velocity)
    return gamma * mass * SPEED_OF_LIGHT * SPEED_OF_LIGHT


def mass_energy_equivalence(mass: float) -> float:
    """Return rest energy ``E = m * c^2``."""
    return mass * SPEED_OF_LIGHT * SPEED_OF_LIGHT
