"""Observing utilities: moon, air mass, rise/set."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .coordinates import equatorial_to_horizontal
from .time import gmst, julian_centuries, now_jd
from .units import deg_to_rad, rad_to_deg


def moon_phase(jd: float) -> Tuple[float, str]:
    """
    Approximate Moon phase.

    Returns (phase 0=new..1=new, name).
    """
    t = julian_centuries(jd)
    # Mean elongation of Moon from Sun (deg)
    d = (297.8501921 + 445267.1114034 * t) % 360.0
    phase = (1.0 - math.cos(deg_to_rad(d))) / 2.0
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
    name = "New Moon"
    for threshold, label in names:
        if phase <= threshold:
            name = label
            break
    else:
        name = "Waning Crescent"
    return phase, name


def moon_illumination(jd: float) -> float:
    phase, _ = moon_phase(jd)
    return abs(math.cos(math.pi * phase))


def air_mass(altitude_deg: float, *, pickering: bool = False) -> float:
    """Air mass at given altitude (degrees above horizon)."""
    if altitude_deg <= 0:
        return float("inf")
    if pickering:
        z = deg_to_rad(90.0 - altitude_deg)
        return 1.0 / (math.sin(altitude_deg * math.pi / 180.0) + 0.50572 * (altitude_deg + 6.07995) ** -1.6364)
    return 1.0 / math.sin(deg_to_rad(altitude_deg))


def is_circumpolar(dec_deg: float, latitude_deg: float) -> bool:
    return dec_deg > (90.0 - abs(latitude_deg))


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
    lat = deg_to_rad(latitude_deg)
    dec = deg_to_rad(dec_deg)
    cos_h0 = -math.tan(lat) * math.tan(dec)
    if cos_h0 > 1:
        return {"rise": None, "transit": None, "set": None, "circumpolar": False, "never_rises": True}
    if cos_h0 < -1:
        return {"rise": None, "transit": None, "set": None, "circumpolar": True, "never_rises": False}
    h0 = math.acos(cos_h0)
    h0_hours = rad_to_deg(h0) / 15.0
    lst_transit = ra_hours
    gmst0 = gmst(jd)
    transit_offset = ((lst_transit - gmst0 - longitude_deg / 15.0) % 24.0)
    rise_offset = (transit_offset - h0_hours) % 24.0
    set_offset = (transit_offset + h0_hours) % 24.0
    day_frac = 1.0
    return {
        "rise": jd - (jd % 1) + rise_offset / 24.0,
        "transit": jd - (jd % 1) + transit_offset / 24.0,
        "set": jd - (jd % 1) + set_offset / 24.0,
        "circumpolar": False,
        "never_rises": False,
        "hour_angle_at_rise": h0_hours,
    }


_OBLIQUITY_DEG = 23.4392911


def ecliptic_to_equatorial(lon_deg: float, lat_deg: float = 0.0) -> Tuple[float, float]:
    """Ecliptic J2000 (lon, lat) degrees to (RA hours, Dec deg)."""
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
    visible: List[Dict[str, Any]] = []
    for obj in objects:
        ra = obj.get("ra_hours", obj.get("ra", 0))
        dec = obj.get("dec_deg", obj.get("dec", 0))
        alt, az = equatorial_to_horizontal(ra, dec, latitude_deg, longitude_deg, jd)
        if alt >= min_altitude:
            row = dict(obj)
            row["altitude"] = round(alt, 2)
            row["azimuth"] = round(az, 2)
            visible.append(row)
    visible.sort(key=lambda x: -x["altitude"])
    return visible
