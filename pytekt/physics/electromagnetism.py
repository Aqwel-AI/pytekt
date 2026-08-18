#!/usr/bin/env python3
"""Basic electromagnetism helpers."""

from __future__ import annotations

from math import pi

from .constants import VACUUM_PERMITTIVITY

_COULOMB_CONSTANT = 1.0 / (4.0 * pi * VACUUM_PERMITTIVITY)


def coulomb_force(charge1: float, charge2: float, distance: float) -> float:
    """Return Coulomb force magnitude ``k * q1 * q2 / r^2``."""
    if distance <= 0:
        raise ValueError("distance must be positive")
    return _COULOMB_CONSTANT * charge1 * charge2 / (distance * distance)


def electric_field_point_charge(charge: float, distance: float) -> float:
    """Return electric field magnitude from a point charge."""
    if distance <= 0:
        raise ValueError("distance must be positive")
    return _COULOMB_CONSTANT * abs(charge) / (distance * distance)


def ohms_law_voltage(current: float, resistance: float) -> float:
    """Return voltage from ``V = I * R``."""
    return current * resistance


def ohms_law_current(voltage: float, resistance: float) -> float:
    """Return current from ``I = V / R``."""
    if resistance == 0:
        raise ValueError("resistance must be non-zero")
    return voltage / resistance


def ohms_law_resistance(voltage: float, current: float) -> float:
    """Return resistance from ``R = V / I``."""
    if current == 0:
        raise ValueError("current must be non-zero")
    return voltage / current


def electrical_power(voltage: float, current: float) -> float:
    """Return electrical power ``P = V * I``."""
    return voltage * current
