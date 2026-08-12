#!/usr/bin/env python3
"""Energy and momentum sanity checks for trajectories."""

from __future__ import annotations

from math import cos
from typing import List, Sequence


def kinetic_energy_from_state(mass: float, velocity: Sequence[float]) -> float:
    """Return kinetic energy from velocity components."""
    speed_sq = sum(v * v for v in velocity)
    return 0.5 * mass * speed_sq


def momentum_norm(mass: float, velocity: Sequence[float]) -> float:
    """Return linear momentum magnitude ``|p| = m * |v|``."""
    speed_sq = sum(v * v for v in velocity)
    return mass * speed_sq ** 0.5


def total_energy_drift(energies: Sequence[float]) -> float:
    """Return relative energy drift ``(max - min) / mean`` for a trajectory."""
    if not energies:
        raise ValueError("energies must be non-empty")
    e_min = min(energies)
    e_max = max(energies)
    e_mean = sum(energies) / len(energies)
    if e_mean == 0:
        return 0.0 if e_min == e_max else float("inf")
    return (e_max - e_min) / abs(e_mean)


def pendulum_energy_series(
    trajectory: Sequence[Sequence[float]],
    *,
    length: float,
    mass: float = 1.0,
    gravity: float = 9.80665,
) -> List[float]:
    """Return total mechanical energy at each pendulum state ``[theta, omega]``."""
    energies: List[float] = []
    for theta, omega in trajectory:
        ke = 0.5 * mass * (length * omega) ** 2
        pe = mass * gravity * length * (1.0 - cos(theta))
        energies.append(ke + pe)
    return energies
