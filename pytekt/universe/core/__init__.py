"""
Universe Core: Constants, Units, Time & Acceleration
===================================================

Provides foundational physical constants, unit parsers, astronomical timekeeping, and C++ native acceleration:
- Physical and astronomical constants (AU, C, G, H0, J2000, LIGHT_YEAR, PARSEC)
- Angle, coordinate formatting/parsing, and flux/magnitude conversions
- Julian dates (JD, MJD), Greenwich Mean Sidereal Time (GMST), Local Sidereal Time (LST)
- Native acceleration status checking
"""

from __future__ import annotations

from pytekt.universe.core._native import using_native_extension
from pytekt.universe.core.constants import (
    AU,
    C,
    G,
    H0_DEFAULT,
    J2000,
    LIGHT_YEAR,
    MU_SUN,
    OMEGA_L_DEFAULT,
    OMEGA_M_DEFAULT,
    PARSEC,
    SOLAR_RADIUS_M,
)
from pytekt.universe.core.time import (
    datetime_to_jd,
    gmst,
    jd_to_datetime,
    julian_centuries,
    lst,
    mjd,
    now_jd,
)
from pytekt.universe.core.units import (
    deg_to_rad,
    flux_to_magnitude,
    format_dec,
    format_ra,
    hours_to_deg,
    ly_to_pc,
    magnitude_to_flux,
    parse_dec,
    parse_ra,
    rad_to_deg,
)

__all__ = [
    # Constants
    "AU",
    "C",
    "G",
    "H0_DEFAULT",
    "J2000",
    "LIGHT_YEAR",
    "MU_SUN",
    "OMEGA_M_DEFAULT",
    "OMEGA_L_DEFAULT",
    "PARSEC",
    "SOLAR_RADIUS_M",
    # Units
    "deg_to_rad",
    "rad_to_deg",
    "hours_to_deg",
    "format_ra",
    "format_dec",
    "parse_ra",
    "parse_dec",
    "flux_to_magnitude",
    "magnitude_to_flux",
    "ly_to_pc",
    # Time
    "datetime_to_jd",
    "jd_to_datetime",
    "now_jd",
    "mjd",
    "gmst",
    "lst",
    "julian_centuries",
    # Native
    "using_native_extension",
]
