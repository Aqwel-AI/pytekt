"""
Optional C++ extension bridge for :mod:`pytekt.universe`.

Uses ``pytekt._pytekt_universe`` when built; otherwise pure-Python fallbacks.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

try:
    from pytekt._pytekt_universe import (
        absolute_magnitude as _absolute_magnitude_native,
        air_mass as _air_mass_native,
        air_mass_batch as _air_mass_batch_native,
        angular_diameter_distance_mpc as _angular_diameter_distance_native,
        angular_separation_deg as _angular_separation_native,
        angular_separation_from_target_batch as _angular_separation_batch_native,
        apparent_magnitude as _apparent_magnitude_native,
        comoving_distance_mpc as _comoving_distance_native,
        distance_modulus as _distance_modulus_native,
        ecliptic_to_equatorial as _ecliptic_to_equatorial_native,
        ecliptic_to_equatorial_batch as _ecliptic_to_equatorial_batch_native,
        equatorial_to_galactic as _equatorial_to_galactic_native,
        equatorial_to_horizontal as _equatorial_to_horizontal_native,
        equatorial_to_horizontal_batch as _equatorial_to_horizontal_batch_native,
        flux_to_magnitude as _flux_to_magnitude_native,
        gmst_hours as _gmst_hours_native,
        horizontal_to_equatorial as _horizontal_to_equatorial_native,
        hohmann_transfer as _hohmann_transfer_native,
        hubble_flow_velocity as _hubble_flow_velocity_native,
        is_circumpolar as _is_circumpolar_native,
        kepler_third_law as _kepler_third_law_native,
        lookback_time_gyr as _lookback_time_gyr_native,
        lst_hours as _lst_hours_native,
        luminosity_distance_mpc as _luminosity_distance_mpc_native,
        magnitude_to_flux as _magnitude_to_flux_native,
        mean_anomaly_from_true as _mean_anomaly_from_true_native,
        moon_illumination as _moon_illumination_native,
        moon_phase_fraction as _moon_phase_fraction_native,
        planet_ecliptic_position as _planet_ecliptic_position_native,
        position_from_elements as _position_from_elements_native,
        precess as _precess_native,
        redshift_from_velocity as _redshift_from_velocity_native,
        rise_set_approx as _rise_set_approx_native,
        true_anomaly_from_mean as _true_anomaly_from_mean_native,
    )

    _NATIVE_AVAILABLE = True
except ImportError:
    _NATIVE_AVAILABLE = False


def using_native_extension() -> bool:
    return _NATIVE_AVAILABLE


def gmst_hours(jd: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_gmst_hours_native(jd))
    from .time import _gmst_py

    return _gmst_py(jd)


def lst_hours(jd: float, longitude_deg: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_lst_hours_native(jd, longitude_deg))
    return (gmst_hours(jd) + longitude_deg / 15.0) % 24.0


def equatorial_to_horizontal(
    ra_hours: float,
    dec_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Tuple[float, float]:
    if _NATIVE_AVAILABLE:
        alt, az = _equatorial_to_horizontal_native(
            ra_hours, dec_deg, latitude_deg, longitude_deg, jd
        )
        return float(alt), float(az)
    from . import coordinates

    return coordinates._equatorial_to_horizontal_py(
        ra_hours, dec_deg, latitude_deg, longitude_deg, jd
    )


def horizontal_to_equatorial(
    alt_deg: float,
    az_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Tuple[float, float]:
    if _NATIVE_AVAILABLE:
        ra, dec = _horizontal_to_equatorial_native(
            alt_deg, az_deg, latitude_deg, longitude_deg, jd
        )
        return float(ra), float(dec)
    from . import coordinates

    return coordinates._horizontal_to_equatorial_py(
        alt_deg, az_deg, latitude_deg, longitude_deg, jd
    )


def equatorial_to_horizontal_batch(
    ra_hours: np.ndarray,
    dec_deg: np.ndarray,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Tuple[np.ndarray, np.ndarray]:
    ra = np.asarray(ra_hours, dtype=np.float64)
    dec = np.asarray(dec_deg, dtype=np.float64)
    if _NATIVE_AVAILABLE:
        alt, az = _equatorial_to_horizontal_batch_native(
            ra, dec, latitude_deg, longitude_deg, jd
        )
        return np.asarray(alt), np.asarray(az)
    from . import coordinates

    alts = []
    azs = []
    for r, d in zip(ra, dec):
        a, z = coordinates._equatorial_to_horizontal_py(
            float(r), float(d), latitude_deg, longitude_deg, jd
        )
        alts.append(a)
        azs.append(z)
    return np.array(alts), np.array(azs)


def angular_separation_deg(
    ra1_hours: float,
    dec1_deg: float,
    ra2_hours: float,
    dec2_deg: float,
) -> float:
    if _NATIVE_AVAILABLE:
        return float(
            _angular_separation_native(ra1_hours, dec1_deg, ra2_hours, dec2_deg)
        )
    from . import coordinates

    return coordinates._angular_separation_py(ra1_hours, dec1_deg, ra2_hours, dec2_deg)


def angular_separation_from_target_batch(
    ra0_hours: float,
    dec0_deg: float,
    ra_hours: np.ndarray,
    dec_deg: np.ndarray,
) -> np.ndarray:
    ra = np.asarray(ra_hours, dtype=np.float64)
    dec = np.asarray(dec_deg, dtype=np.float64)
    if _NATIVE_AVAILABLE:
        return np.asarray(
            _angular_separation_batch_native(ra0_hours, dec0_deg, ra, dec)
        )
    out = [
        angular_separation_deg(ra0_hours, dec0_deg, float(r), float(d))
        for r, d in zip(ra, dec)
    ]
    return np.array(out)


def equatorial_to_galactic(ra_hours: float, dec_deg: float) -> Tuple[float, float]:
    if _NATIVE_AVAILABLE:
        l, b = _equatorial_to_galactic_native(ra_hours, dec_deg)
        return float(l), float(b)
    from . import coordinates

    return coordinates._equatorial_to_galactic_py(ra_hours, dec_deg)


def ecliptic_to_equatorial(lon_deg: float, lat_deg: float = 0.0) -> Tuple[float, float]:
    if _NATIVE_AVAILABLE:
        ra, dec = _ecliptic_to_equatorial_native(lon_deg, lat_deg)
        return float(ra), float(dec)
    from . import observing

    return observing._ecliptic_to_equatorial_py(lon_deg, lat_deg)


def ecliptic_to_equatorial_batch(
    lon_deg: np.ndarray, lat_deg: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    lon = np.asarray(lon_deg, dtype=np.float64)
    lat = np.asarray(lat_deg, dtype=np.float64)
    if _NATIVE_AVAILABLE:
        ra, dec = _ecliptic_to_equatorial_batch_native(lon, lat)
        return np.asarray(ra), np.asarray(dec)
    from . import observing

    ras, decs = [], []
    for lo, la in zip(lon, lat):
        r, d = observing._ecliptic_to_equatorial_py(float(lo), float(la))
        ras.append(r)
        decs.append(d)
    return np.array(ras), np.array(decs)


def precess(
    ra_hours: float,
    dec_deg: float,
    from_epoch: float = 2000.0,
    to_epoch: float = 2000.0,
) -> Tuple[float, float]:
    if _NATIVE_AVAILABLE:
        ra, dec = _precess_native(ra_hours, dec_deg, from_epoch, to_epoch)
        return float(ra), float(dec)
    from . import coordinates

    return coordinates._precess_py(ra_hours, dec_deg, from_epoch, to_epoch)


def air_mass(altitude_deg: float, *, pickering: bool = False) -> float:
    if _NATIVE_AVAILABLE:
        return float(_air_mass_native(altitude_deg, pickering))
    from . import observing

    return observing._air_mass_py(altitude_deg, pickering=pickering)


def air_mass_batch(altitude_deg: np.ndarray, *, pickering: bool = False) -> np.ndarray:
    alts = np.asarray(altitude_deg, dtype=np.float64)
    if _NATIVE_AVAILABLE:
        return np.asarray(_air_mass_batch_native(alts, pickering))
    return np.array([air_mass(float(a), pickering=pickering) for a in alts])


def is_circumpolar(dec_deg: float, latitude_deg: float) -> bool:
    if _NATIVE_AVAILABLE:
        return bool(_is_circumpolar_native(dec_deg, latitude_deg))
    return dec_deg > (90.0 - abs(latitude_deg))


def rise_set_approx(
    ra_hours: float,
    dec_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    jd: float,
) -> Dict[str, Any]:
    if _NATIVE_AVAILABLE:
        return dict(_rise_set_approx_native(ra_hours, dec_deg, latitude_deg, longitude_deg, jd))
    from . import observing

    return observing._rise_set_approx_py(
        ra_hours, dec_deg, latitude_deg, longitude_deg, jd
    )


def moon_phase_fraction(jd: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_moon_phase_fraction_native(jd))
    from .observing import _moon_phase_fraction_py as _py

    return _py(jd)


def moon_illumination(jd: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_moon_illumination_native(jd))
    import math

    phase = moon_phase_fraction(jd)
    return abs(math.cos(math.pi * phase))


def comoving_distance_mpc(
    z: float, H0: float, Om0: float, Ode0: float, *, steps: int = 200
) -> float:
    if _NATIVE_AVAILABLE:
        return float(_comoving_distance_native(z, H0, Om0, Ode0, steps))
    from .cosmology import _comoving_distance_py

    return _comoving_distance_py(z, H0, Om0, Ode0, steps=steps)


def luminosity_distance_mpc(
    z: float, H0: float, Om0: float, Ode0: float, *, steps: int = 200
) -> float:
    if _NATIVE_AVAILABLE:
        return float(_luminosity_distance_mpc_native(z, H0, Om0, Ode0, steps))
    return comoving_distance_mpc(z, H0, Om0, Ode0, steps=steps) * (1.0 + z)


def lookback_time_gyr(
    z: float, H0: float, Om0: float, Ode0: float, *, steps: int = 200
) -> float:
    if _NATIVE_AVAILABLE:
        return float(_lookback_time_gyr_native(z, H0, Om0, Ode0, steps))
    from .cosmology import _lookback_time_py

    return _lookback_time_py(z, H0, Om0, Ode0, steps=steps)


def angular_diameter_distance_mpc(
    z: float, H0: float, Om0: float, Ode0: float, *, steps: int = 200
) -> float:
    if _NATIVE_AVAILABLE:
        return float(_angular_diameter_distance_native(z, H0, Om0, Ode0, steps))
    d_l = luminosity_distance_mpc(z, H0, Om0, Ode0, steps=steps)
    return d_l / (1.0 + z) ** 2


def redshift_from_velocity(v_kms: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_redshift_from_velocity_native(v_kms))
    from .cosmology import _redshift_from_velocity_py

    return _redshift_from_velocity_py(v_kms)


def hubble_flow_velocity(distance_mpc: float, H0: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_hubble_flow_velocity_native(distance_mpc, H0))
    return H0 * distance_mpc


def flux_to_magnitude(flux: float, flux_zero: float = 1.0) -> float:
    if flux <= 0:
        raise ValueError("flux must be positive")
    if _NATIVE_AVAILABLE:
        return float(_flux_to_magnitude_native(flux, flux_zero))
    import math

    return -2.5 * math.log10(flux / flux_zero)


def magnitude_to_flux(magnitude: float, flux_zero: float = 1.0) -> float:
    if _NATIVE_AVAILABLE:
        return float(_magnitude_to_flux_native(magnitude, flux_zero))
    return flux_zero * 10.0 ** (-0.4 * magnitude)


def distance_modulus(distance_pc: float) -> float:
    if distance_pc <= 0:
        raise ValueError("distance_pc must be positive")
    if _NATIVE_AVAILABLE:
        return float(_distance_modulus_native(distance_pc))
    import math

    return 5.0 * math.log10(distance_pc / 10.0)


def absolute_magnitude(apparent_m: float, distance_pc: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_absolute_magnitude_native(apparent_m, distance_pc))
    return apparent_m - distance_modulus(distance_pc)


def apparent_magnitude(absolute_m: float, distance_pc: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_apparent_magnitude_native(absolute_m, distance_pc))
    return absolute_m + distance_modulus(distance_pc)


def true_anomaly_from_mean(M_deg: float, e: float, *, tol: float = 1e-8) -> float:
    if _NATIVE_AVAILABLE:
        return float(_true_anomaly_from_mean_native(M_deg, e, tol))
    from . import orbits

    return orbits._true_anomaly_from_mean_py(M_deg, e, tol=tol)


def mean_anomaly_from_true(nu_deg: float, e: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_mean_anomaly_from_true_native(nu_deg, e))
    from . import orbits

    return orbits._mean_anomaly_from_true_py(nu_deg, e)


def kepler_third_law(a: float, mu: float) -> float:
    if _NATIVE_AVAILABLE:
        return float(_kepler_third_law_native(a, mu))
    from . import orbits

    return orbits._kepler_third_law_py(a, mu)


def hohmann_transfer(r1: float, r2: float, mu: float) -> Dict[str, float]:
    if _NATIVE_AVAILABLE:
        return dict(_hohmann_transfer_native(r1, r2, mu))
    from . import orbits

    return orbits._hohmann_transfer_py(r1, r2, mu)


def planet_ecliptic_position(
    L0_deg: float, period_yr: float, a_au: float, t_centuries: float
) -> Dict[str, float]:
    if _NATIVE_AVAILABLE:
        return dict(_planet_ecliptic_position_native(L0_deg, period_yr, a_au, t_centuries))
    from . import orbits

    return orbits._planet_ecliptic_position_py(L0_deg, period_yr, a_au, t_centuries)


def position_from_elements(
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
    if _NATIVE_AVAILABLE:
        x, y, z = _position_from_elements_native(
            a, e, i_deg, raan_deg, argp_deg, nu_deg, jd, mu, epoch_jd
        )
        return float(x), float(y), float(z)
    from . import orbits

    return orbits._position_from_elements_py(
        a, e, i_deg, raan_deg, argp_deg, nu_deg, jd, mu, epoch_jd=epoch_jd
    )
