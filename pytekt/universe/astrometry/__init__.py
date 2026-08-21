"""
Universe Astrometry & Photometry
================================

Provides coordinate transformations, precession, angular distances, and magnitudes:
- Equatorial to Horizontal (Alt/Az) and Horizontal to Equatorial
- Equatorial to Galactic transformations
- Precession corrections across epochs
- Great-circle angular separation
- Distance modulus, apparent and absolute magnitudes, color index
"""

from __future__ import annotations

from pytekt.universe.astrometry.coordinates import (
    angular_separation,
    equatorial_to_galactic,
    equatorial_to_horizontal,
    horizontal_to_equatorial,
    precess,
)
from pytekt.universe.astrometry.magnitude import (
    absolute_magnitude,
    apparent_magnitude,
    color_index,
    distance_modulus,
)

__all__ = [
    "angular_separation",
    "equatorial_to_galactic",
    "equatorial_to_horizontal",
    "horizontal_to_equatorial",
    "precess",
    "apparent_magnitude",
    "absolute_magnitude",
    "distance_modulus",
    "color_index",
]
