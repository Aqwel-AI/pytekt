"""Basic orbital mechanics."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .constants import AU, J2000, MU_SUN
from .time import julian_centuries
from .units import deg_to_rad, rad_to_deg


@dataclass
class OrbitalElements:
    """Classical Keplerian elements."""

    a: float  # semi-major axis (m or AU depending on mu)
    e: float  # eccentricity
    i: float  # inclination deg
    raan: float  # right ascension of ascending node deg
    argp: float  # argument of periapsis deg
    nu: float  # true anomaly deg at epoch


def _kepler_third_law_py(a: float, mu: float) -> float:
    return 2.0 * math.pi * math.sqrt(a**3 / mu)


def kepler_third_law(a: float, mu: float) -> float:
    """Orbital period (seconds) from semi-major axis and mu."""
    from ._native import kepler_third_law as _ktl

    return _ktl(a, mu)


def _mean_anomaly_from_true_py(nu_deg: float, e: float) -> float:
    nu = deg_to_rad(nu_deg)
    ea = 2.0 * math.atan2(math.sqrt(1 - e) * math.sin(nu / 2), math.sqrt(1 + e) * math.cos(nu / 2))
    return rad_to_deg(ea - e * math.sin(ea))


def mean_anomaly_from_true(nu_deg: float, e: float) -> float:
    from ._native import mean_anomaly_from_true as _mft

    return _mft(nu_deg, e)


def _true_anomaly_from_mean_py(M_deg: float, e: float, *, tol: float = 1e-8) -> float:
    M = deg_to_rad(M_deg % 360.0)
    E = M if e < 0.8 else math.pi
    for _ in range(50):
        dE = (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
        E -= dE
        if abs(dE) < tol:
            break
    nu = 2.0 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2), math.sqrt(1 - e) * math.cos(E / 2))
    return rad_to_deg(nu) % 360.0


def true_anomaly_from_mean(M_deg: float, e: float, *, tol: float = 1e-8) -> float:
    """Solve Kepler's equation for true anomaly (degrees)."""
    from ._native import true_anomaly_from_mean as _tfm

    return _tfm(M_deg, e, tol=tol)


def _position_from_elements_py(
    a: float,
    e: float,
    i_deg: float,
    raan_deg: float,
    argp_deg: float,
    nu_deg: float,
    jd: float,
    mu: float,
    *,
    epoch_jd: float,
) -> Tuple[float, float, float]:
    n = math.sqrt(mu / a**3)
    dt = (jd - epoch_jd) * 86400.0
    M0 = _mean_anomaly_from_true_py(nu_deg, e)
    M = math.radians(M0) + n * dt
    nu = _true_anomaly_from_mean_py(rad_to_deg(M), e)
    r = a * (1 - e**2) / (1 + e * math.cos(deg_to_rad(nu)))
    i, raan, argp, nu_r = map(deg_to_rad, (i_deg, raan_deg, argp_deg, nu))
    x_orb = r * (math.cos(nu_r))
    y_orb = r * (math.sin(nu_r))
    cos_raan, sin_raan = math.cos(raan), math.sin(raan)
    cos_i, sin_i = math.cos(i), math.sin(i)
    cos_argp, sin_argp = math.cos(argp), math.sin(argp)
    x = (
        (cos_raan * cos_argp - sin_raan * sin_argp * cos_i) * x_orb
        + (-cos_raan * sin_argp - sin_raan * cos_argp * cos_i) * y_orb
    )
    y = (
        (sin_raan * cos_argp + cos_raan * sin_argp * cos_i) * x_orb
        + (-sin_raan * sin_argp + cos_raan * cos_argp * cos_i) * y_orb
    )
    z = sin_argp * sin_i * x_orb + cos_argp * sin_i * y_orb
    return x, y, z


def position_from_elements(
    elements: OrbitalElements,
    jd: float,
    mu: float,
    *,
    epoch_jd: float = J2000,
) -> Tuple[float, float, float]:
    """ECI position (x, y, z) in same units as *a*."""
    from ._native import position_from_elements as _pfe

    return _pfe(
        elements.a,
        elements.e,
        elements.i,
        elements.raan,
        elements.argp,
        elements.nu,
        jd,
        mu,
        epoch_jd=epoch_jd,
    )


def _hohmann_transfer_py(r1: float, r2: float, mu: float) -> Dict[str, float]:
    if r2 < r1:
        r1, r2 = r2, r1
    v1 = math.sqrt(mu / r1)
    v2 = math.sqrt(mu / r2)
    a_transfer = (r1 + r2) / 2.0
    v_peri = math.sqrt(mu * (2 / r1 - 1 / a_transfer))
    v_apo = math.sqrt(mu * (2 / r2 - 1 / a_transfer))
    return {
        "dv1": v_peri - v1,
        "dv2": v2 - v_apo,
        "total_dv": (v_peri - v1) + (v2 - v_apo),
        "transfer_time_s": math.pi * math.sqrt(a_transfer**3 / mu),
    }


def hohmann_transfer(r1: float, r2: float, mu: float) -> Dict[str, float]:
    """Hohmann transfer delta-v (same units as mu, r)."""
    from ._native import hohmann_transfer as _hohmann

    return _hohmann(r1, r2, mu)


def _planet_ecliptic_position_py(
    L0_deg: float, period_yr: float, a_au: float, t_centuries: float
) -> Dict[str, float]:
    years = t_centuries * 100.0
    L = math.radians((L0_deg + 360.0 / period_yr * years) % 360.0)
    x = a_au * math.cos(L)
    y = a_au * math.sin(L)
    lon = rad_to_deg(math.atan2(y, x)) % 360.0
    return {"x_au": x, "y_au": y, "z_au": 0.0, "lon_deg": lon, "lat_deg": 0.0, "r_au": a_au}


def planet_position(planet_name: str, jd: float) -> Dict[str, float]:
    """
    Low-precision heliocentric ecliptic position (AU, degrees).

    Uses mean longitude from builtin catalog.
    """
    from .catalogs import load_planets
    from ._native import planet_ecliptic_position

    name = planet_name.lower()
    planets = {p["name"].lower(): p for p in load_planets()}
    if name not in planets:
        raise ValueError(f"Unknown planet {planet_name!r}")
    p = planets[name]
    t = julian_centuries(jd)
    return planet_ecliptic_position(p["L"], p["period_yr"], p["a"], t)
