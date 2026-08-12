#!/usr/bin/env python3
"""Basic optics helpers."""

from __future__ import annotations

from math import asin, degrees, radians, sin


def snells_law(n1: float, n2: float, incident_angle_deg: float) -> float:
    """Return refracted angle (degrees) from Snell's law."""
    if n1 <= 0 or n2 <= 0:
        raise ValueError("refractive indices must be positive")
    sin_theta2 = (n1 / n2) * sin(radians(incident_angle_deg))
    if abs(sin_theta2) > 1.0:
        raise ValueError("total internal reflection — no refracted angle")
    return degrees(asin(sin_theta2))


def critical_angle(n1: float, n2: float) -> float:
    """Return critical angle (degrees) for total internal reflection."""
    if n1 <= 0 or n2 <= 0:
        raise ValueError("refractive indices must be positive")
    if n2 >= n1:
        raise ValueError("critical angle exists only when n1 > n2")
    return degrees(asin(n2 / n1))


def thin_lens_equation(object_distance: float, image_distance: float) -> float:
    """Return focal length from ``1/f = 1/u + 1/v``."""
    if object_distance == 0 or image_distance == 0:
        raise ValueError("object and image distances must be non-zero")
    return 1.0 / (1.0 / object_distance + 1.0 / image_distance)
