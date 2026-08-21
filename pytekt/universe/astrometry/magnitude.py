"""Photometric magnitude utilities."""

from __future__ import annotations

import math


def distance_modulus(distance_pc: float) -> float:
    """Distance modulus mu = 5 log10(d/10 pc)."""
    from pytekt.universe.core._native import distance_modulus as _dm

    return _dm(distance_pc)


def absolute_magnitude(apparent_m: float, distance_pc: float) -> float:
    from pytekt.universe.core._native import absolute_magnitude as _abs_mag

    return _abs_mag(apparent_m, distance_pc)


def apparent_magnitude(absolute_m: float, distance_pc: float) -> float:
    from pytekt.universe.core._native import apparent_magnitude as _app_mag

    return _app_mag(absolute_m, distance_pc)


def color_index(b_mag: float, v_mag: float) -> float:
    return b_mag - v_mag
