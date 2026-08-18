#!/usr/bin/env python3
"""Kinematics helpers for constant-acceleration and circular motion."""

from __future__ import annotations


def velocity_from_uat(initial_velocity: float, acceleration: float, time: float) -> float:
    """Return final velocity from ``v = u + a*t``."""
    return initial_velocity + acceleration * time


def displacement_from_uat(initial_velocity: float, acceleration: float, time: float) -> float:
    """Return displacement from ``s = u*t + 0.5*a*t^2``."""
    return initial_velocity * time + 0.5 * acceleration * time * time


def average_velocity(displacement: float, time: float) -> float:
    """Return average velocity ``s / t``."""
    if time == 0:
        raise ValueError("time must be non-zero")
    return displacement / time


def centripetal_acceleration(speed: float, radius: float) -> float:
    """Return centripetal acceleration ``v^2 / r``."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    return speed * speed / radius


def centripetal_force(mass: float, speed: float, radius: float) -> float:
    """Return centripetal force ``m * v^2 / r``."""
    return mass * centripetal_acceleration(speed, radius)
