"""Celestial coordinate transforms."""

from __future__ import annotations

import math
from typing import Tuple

from pytekt.universe.core.time import gmst, julian_centuries
from pytekt.universe.core.units import deg_to_rad, hours_to_deg, rad_to_deg


def _angular_separation_py(
    ra1_hours: float,
    dec1_deg: float,
    ra2_hours: float,
    dec2_deg: float,
) -> float:
    a1, d1 = deg_to_rad(hours_to_deg(ra1_hours)), deg_to_rad(dec1_deg)
    a2, d2 = deg_to_rad(hours_to_deg(ra2_hours)), deg_to_rad(dec2_deg)
    cos_sep = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(a1 - a2)
    cos_sep = max(-1.0, min(1.0, cos_sep))
    return rad_to_deg(math.acos(cos_sep))


def angular_separation(
    ra1_hours: float,
    dec1_deg: float,
    ra2_hours: float,
    dec2_deg: float,
) -> float:
    """Great-circle separation in degrees."""
    from pytekt.universe.core._native import angular_separation_deg

    return angular_separation_deg(ra1_hours, dec1_deg, ra2_hours, dec2_deg)


def _equatorial_to_galactic_py(ra_hours: float, dec_deg: float) -> Tuple[float, float]:
    """Equatorial J2000 (RA hours, Dec deg) to galactic (l, b) degrees."""
    ra = deg_to_rad(hours_to_deg(ra_hours))
    dec = deg_to_rad(dec_deg)
    ra_gp = deg_to_rad(192.85948)
    dec_gp = deg_to_rad(27.12825)
    l_cp = deg_to_rad(122.93192)
    sin_b = math.sin(dec_gp) * math.sin(dec) + math.cos(dec_gp) * math.cos(dec) * math.cos(ra - ra_gp)
    b = math.asin(max(-1.0, min(1.0, sin_b)))
    y = math.cos(dec) * math.sin(ra - ra_gp)
    x = math.sin(dec_gp) * math.cos(dec) * math.cos(ra - ra_gp) - math.cos(dec_gp) * math.sin(dec)
    l = math.atan2(y, x) + l_cp
    if l < 0:
        l += 2 * math.pi
    return rad_to_deg(l), rad_to_deg(b)


def equatorial_to_galactic(ra_hours: float, dec_deg: float) -> Tuple[float, float]:
    """Equatorial J2000 (RA hours, Dec deg) to galactic (l, b) degrees."""
    from pytekt.universe.core._native import equatorial_to_galactic as _eq_gal

    return _eq_gal(ra_hours, dec_deg)


def _equatorial_to_horizontal_py(
    ra_hours: float,
    dec_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Tuple[float, float]:
    """
    Equatorial to horizontal coordinates.

    Returns (altitude_deg, azimuth_deg) where azimuth is measured from north eastward.
    """
    ha = (gmst(jd) + longitude_deg / 15.0 - ra_hours) * 15.0
    ha_rad = deg_to_rad(ha)
    dec_rad = deg_to_rad(dec_deg)
    lat_rad = deg_to_rad(latitude_deg)
    sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    alt = math.asin(max(-1.0, min(1.0, sin_alt)))
    cos_az = (math.sin(dec_rad) - math.sin(alt) * math.sin(lat_rad)) / (
        math.cos(alt) * math.cos(lat_rad) + 1e-15
    )
    cos_az = max(-1.0, min(1.0, cos_az))
    sin_az = -math.cos(dec_rad) * math.sin(ha_rad) / (math.cos(alt) + 1e-15)
    az = math.atan2(sin_az, cos_az)
    if az < 0:
        az += 2 * math.pi
    return rad_to_deg(alt), rad_to_deg(az)


def equatorial_to_horizontal(
    ra_hours: float,
    dec_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Tuple[float, float]:
    """
    Equatorial to horizontal coordinates.

    Returns (altitude_deg, azimuth_deg) where azimuth is measured from north eastward.
    """
    from pytekt.universe.core._native import equatorial_to_horizontal as _eq_hor

    return _eq_hor(ra_hours, dec_deg, latitude_deg, longitude_deg, jd)


def _horizontal_to_equatorial_py(
    alt_deg: float,
    az_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Tuple[float, float]:
    """Horizontal to equatorial (RA hours, Dec deg)."""
    alt = deg_to_rad(alt_deg)
    az = deg_to_rad(az_deg)
    lat = deg_to_rad(latitude_deg)
    sin_dec = math.sin(alt) * math.sin(lat) + math.cos(alt) * math.cos(lat) * math.cos(az)
    dec = math.asin(max(-1.0, min(1.0, sin_dec)))
    cos_ha = (math.sin(alt) - math.sin(dec) * math.sin(lat)) / (
        math.cos(dec) * math.cos(lat) + 1e-15
    )
    cos_ha = max(-1.0, min(1.0, cos_ha))
    sin_ha = -math.cos(alt) * math.sin(az) / (math.cos(dec) + 1e-15)
    ha = math.atan2(sin_ha, cos_ha)
    ha_deg = rad_to_deg(ha)
    ra_deg = (gmst(jd) * 15.0 + longitude_deg - ha_deg) % 360.0
    return ra_deg / 15.0, rad_to_deg(dec)


def horizontal_to_equatorial(
    alt_deg: float,
    az_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Tuple[float, float]:
    """Horizontal to equatorial (RA hours, Dec deg)."""
    from pytekt.universe.core._native import horizontal_to_equatorial as _hor_eq

    return _hor_eq(alt_deg, az_deg, latitude_deg, longitude_deg, jd)


def _precess_py(
    ra_hours: float,
    dec_deg: float,
    from_epoch: float = 2000.0,
    to_epoch: float = 2000.0,
) -> Tuple[float, float]:
    """Simplified precession (low precision, educational use)."""
    if abs(from_epoch - to_epoch) < 1e-9:
        return ra_hours, dec_deg
    t0 = (from_epoch - 2000.0) / 100.0
    t = (to_epoch - 2000.0) / 100.0
    zeta_a = (2306.2181 + 1.39656 * t0 - 0.000139 * t0 * t0) * (t - t0) / 3600.0
    z_a = (2306.2181 + 1.39656 * t0) * (t - t0) / 3600.0 + (0.30188 - 0.000344 * t0) * (t - t0) ** 2 / 3600.0
    theta_a = (2004.3109 - 0.85330 * t0) * (t - t0) / 3600.0 - (0.42665 + 0.000217 * t0) * (t - t0) ** 2 / 3600.0
    ra = hours_to_deg(ra_hours)
    dec_new = dec_deg + theta_a * math.cos(deg_to_rad(ra))
    ra_new = ra + z_a + zeta_a / math.cos(deg_to_rad(dec_deg + 1e-6))
    return ra_new / 15.0, dec_new


def precess(
    ra_hours: float,
    dec_deg: float,
    from_epoch: float = 2000.0,
    to_epoch: float = 2000.0,
) -> Tuple[float, float]:
    """
    Simplified precession (low precision, educational use).

    Uses IAU 1976-ish polynomials for small epoch differences.
    """
    from pytekt.universe.core._native import precess as _precess_native

    return _precess_native(ra_hours, dec_deg, from_epoch, to_epoch)
