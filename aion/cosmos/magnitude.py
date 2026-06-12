"""Photometric magnitude utilities."""

from __future__ import annotations

import math


def distance_modulus(distance_pc: float) -> float:
    """Distance modulus mu = 5 log10(d/10 pc)."""
    if distance_pc <= 0:
        raise ValueError("distance_pc must be positive")
    return 5.0 * math.log10(distance_pc / 10.0)


def absolute_magnitude(apparent_m: float, distance_pc: float) -> float:
    return apparent_m - distance_modulus(distance_pc)


def apparent_magnitude(absolute_m: float, distance_pc: float) -> float:
    return absolute_m + distance_modulus(distance_pc)


def color_index(b_mag: float, v_mag: float) -> float:
    return b_mag - v_mag
