#!/usr/bin/env python3
"""Basic Newtonian mechanics helpers."""

from __future__ import annotations

from .constants import GRAVITATIONAL_ACCELERATION, GRAVITATIONAL_CONSTANT


def force(mass: float, acceleration: float) -> float:
    """Return force in newtons from ``F = m * a``."""
    return mass * acceleration


def momentum(mass: float, velocity: float) -> float:
    """Return linear momentum from ``p = m * v``."""
    return mass * velocity


def kinetic_energy(mass: float, velocity: float) -> float:
    """Return kinetic energy from ``0.5 * m * v^2``."""
    return 0.5 * mass * velocity * velocity


def potential_energy(mass: float, height: float, gravity: float = GRAVITATIONAL_ACCELERATION) -> float:
    """Return gravitational potential energy from ``m * g * h``."""
    return mass * gravity * height


def gravitational_force(mass1: float, mass2: float, distance: float) -> float:
    """Return Newtonian gravitational force between two masses."""
    if distance <= 0:
        raise ValueError("distance must be positive")
    return GRAVITATIONAL_CONSTANT * mass1 * mass2 / (distance * distance)


def projectile_range(initial_speed: float, launch_angle_degrees: float, gravity: float = GRAVITATIONAL_ACCELERATION) -> float:
    """Return ideal projectile range without drag."""
    from math import radians, sin

    angle = radians(2.0 * launch_angle_degrees)
    return (initial_speed * initial_speed * sin(angle)) / gravity
