"""Observing utilities: moon, air mass, rise/set."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .coordinates import equatorial_to_horizontal
from .time import gmst, julian_centuries, now_jd
from .units import deg_to_rad, rad_to_deg


def _moon_phase_fraction_py(jd: float) -> float:
    t = julian_centuries(jd)
    d = (297.8501921 + 445267.1114034 * t) % 360.0
    return (1.0 - math.cos(deg_to_rad(d))) / 2.0


def _moon_phase_name(phase: float) -> str:
    names = [
        (0.03, "New Moon"),
        (0.22, "Waxing Crescent"),
        (0.28, "First Quarter"),
        (0.47, "Waxing Gibbous"),
        (0.53, "Full Moon"),
        (0.72, "Waning Gibbous"),
        (0.78, "Last Quarter"),
        (0.97, "Waning Crescent"),
    ]
    for threshold, label in names:
        if phase <= threshold:
            return label
    return "Waning Crescent"


def moon_phase(jd: float) -> Tuple[float, str]:
    """
    Approximate Moon phase.

    Returns (phase 0=new..1=new, name).
    """
    from ._native import moon_phase_fraction

    phase = moon_phase_fraction(jd)
    return phase, _moon_phase_name(phase)


def moon_illumination(jd: float) -> float:
    from ._native import moon_illumination as _moon_illum

    return _moon_illum(jd)


def _air_mass_py(altitude_deg: float, *, pickering: bool = False) -> float:
    if altitude_deg <= 0:
        return float("inf")
    if pickering:
        return 1.0 / (
            math.sin(altitude_deg * math.pi / 180.0)
            + 0.50572 * (altitude_deg + 6.07995) ** -1.6364
        )
    return 1.0 / math.sin(deg_to_rad(altitude_deg))


def air_mass(altitude_deg: float, *, pickering: bool = False) -> float:
    """Air mass at given altitude (degrees above horizon)."""
    from ._native import air_mass as _air_mass_native

    return _air_mass_native(altitude_deg, pickering=pickering)


def is_circumpolar(dec_deg: float, latitude_deg: float) -> bool:
    from ._native import is_circumpolar as _is_circ

    return _is_circ(dec_deg, latitude_deg)


def _rise_set_approx_py(
    ra_hours: float,
    dec_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Dict[str, Optional[float]]:
    lat = deg_to_rad(latitude_deg)
    dec = deg_to_rad(dec_deg)
    cos_h0 = -math.tan(lat) * math.tan(dec)
    if cos_h0 > 1:
        return {"rise": None, "transit": None, "set": None, "circumpolar": False, "never_rises": True}
    if cos_h0 < -1:
        return {"rise": None, "transit": None, "set": None, "circumpolar": True, "never_rises": False}
    h0 = math.acos(cos_h0)
    h0_hours = rad_to_deg(h0) / 15.0
    gmst0 = gmst(jd)
    transit_offset = ((ra_hours - gmst0 - longitude_deg / 15.0) % 24.0)
    rise_offset = (transit_offset - h0_hours) % 24.0
    set_offset = (transit_offset + h0_hours) % 24.0
    jd0 = jd - (jd % 1)
    return {
        "rise": jd0 + rise_offset / 24.0,
        "transit": jd0 + transit_offset / 24.0,
        "set": jd0 + set_offset / 24.0,
        "circumpolar": False,
        "never_rises": False,
        "hour_angle_at_rise": h0_hours,
    }


def rise_set_approx(
    ra_hours: float,
    dec_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Dict[str, Optional[float]]:
    """
    Approximate rise, transit, set times as Julian Date offsets from jd at 0h UT.

    Educational precision only (± several minutes).
    """
    from ._native import rise_set_approx as _rise_set

    return _rise_set(ra_hours, dec_deg, latitude_deg, longitude_deg, jd)


_OBLIQUITY_DEG = 23.4392911


def _ecliptic_to_equatorial_py(lon_deg: float, lat_deg: float = 0.0) -> Tuple[float, float]:
    lon = deg_to_rad(lon_deg)
    lat = deg_to_rad(lat_deg)
    eps = deg_to_rad(_OBLIQUITY_DEG)
    sin_dec = math.sin(lat) * math.cos(eps) + math.cos(lat) * math.sin(eps) * math.sin(lon)
    dec = math.asin(max(-1.0, min(1.0, sin_dec)))
    y = math.sin(lon) * math.cos(eps) - math.tan(lat) * math.sin(eps)
    x = math.cos(lon)
    ra = math.atan2(y, x)
    if ra < 0:
        ra += 2 * math.pi
    return rad_to_deg(ra) / 15.0, rad_to_deg(dec)


def ecliptic_to_equatorial(lon_deg: float, lat_deg: float = 0.0) -> Tuple[float, float]:
    """Ecliptic J2000 (lon, lat) degrees to (RA hours, Dec deg)."""
    from ._native import ecliptic_to_equatorial as _ecl_eq

    return _ecl_eq(lon_deg, lat_deg)


def planet_catalog_entries(jd: float) -> List[Dict[str, Any]]:
    """Builtin planets as equatorial catalog rows for observing."""
    from .catalogs import load_planets
    from .orbits import planet_position

    rows: List[Dict[str, Any]] = []
    for planet in load_planets():
        pos = planet_position(planet["name"], jd)
        ra, dec = ecliptic_to_equatorial(pos["lon_deg"], pos.get("lat_deg", 0.0))
        rows.append(
            {
                "name": planet["name"],
                "ra_hours": round(ra, 4),
                "dec_deg": round(dec, 4),
                "kind": "planet",
                "type": "planet",
            }
        )
    return rows


def build_sky_catalog(catalog_mode: str = "stars", jd: Optional[float] = None) -> List[Dict[str, Any]]:
    """Merge bright stars, Messier, and/or planets for sky queries."""
    from .catalogs import load_bright_stars, load_messier

    jd = jd if jd is not None else now_jd()
    mode = (catalog_mode or "stars").lower()
    if mode == "stars":
        return [dict(row, kind="star") for row in load_bright_stars()]
    if mode == "messier":
        return [
            dict(row, kind="messier", name=row.get("name") or row.get("id", "?"))
            for row in load_messier()
        ]
    if mode == "planets":
        return planet_catalog_entries(jd)
    stars = [dict(row, kind="star") for row in load_bright_stars()]
    messier = [
        dict(row, kind="messier", name=row.get("name") or row.get("id", "?"))
        for row in load_messier()
    ]
    planets = planet_catalog_entries(jd)
    return stars + messier + planets


def whats_up_all(
    latitude_deg: float,
    longitude_deg: float,
    jd: Optional[float] = None,
    *,
    catalog_mode: str = "all",
    min_altitude: float = 10.0,
) -> List[Dict[str, Any]]:
    """Return merged catalog objects above *min_altitude* degrees."""
    jd = jd if jd is not None else now_jd()
    catalog = build_sky_catalog(catalog_mode, jd)
    return whats_up(latitude_deg, longitude_deg, jd, catalog, min_altitude=min_altitude)


def whats_up(
    latitude_deg: float,
    longitude_deg: float,
    jd: Optional[float] = None,
    catalog: Optional[List[Dict[str, Any]]] = None,
    *,
    min_altitude: float = 10.0,
    catalog_mode: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return catalog objects above *min_altitude* degrees."""
    from .catalogs import load_bright_stars

    jd = jd if jd is not None else now_jd()
    if catalog is None and catalog_mode:
        catalog = build_sky_catalog(catalog_mode, jd)
    objects = catalog if catalog is not None else load_bright_stars()
    if not objects:
        return []
    import numpy as np
    from ._native import equatorial_to_horizontal_batch

    ra = np.array([float(o.get("ra_hours", o.get("ra", 0))) for o in objects], dtype=np.float64)
    dec = np.array([float(o.get("dec_deg", o.get("dec", 0))) for o in objects], dtype=np.float64)
    alts, azs = equatorial_to_horizontal_batch(ra, dec, latitude_deg, longitude_deg, jd)
    visible: List[Dict[str, Any]] = []
    for obj, alt, az in zip(objects, alts, azs):
        alt_f = float(alt)
        if alt_f >= min_altitude:
            row = dict(obj)
            row["altitude"] = round(alt_f, 2)
            row["azimuth"] = round(float(az), 2)
            visible.append(row)
    visible.sort(key=lambda x: -x["altitude"])
    return visible
