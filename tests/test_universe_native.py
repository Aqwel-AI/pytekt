"""Tests for optional C++ universe extension."""

import math

import numpy as np

from aion.universe._native import using_native_extension
from aion.universe.constants import AU, J2000, MU_SUN
from aion.universe.coordinates import angular_separation, equatorial_to_horizontal, horizontal_to_equatorial
from aion.universe.cosmology import Cosmology, luminosity_distance_mpc, redshift_from_velocity
from aion.universe.magnitude import absolute_magnitude, apparent_magnitude
from aion.universe.observing import air_mass, ecliptic_to_equatorial, moon_illumination, rise_set_approx
from aion.universe.orbits import hohmann_transfer, kepler_third_law, planet_position, true_anomaly_from_mean
from aion.universe.time import gmst, lst


def test_gmst_matches_py():
    g = gmst(J2000)
    from aion.universe.time import _gmst_py

    assert abs(g - _gmst_py(J2000)) < 1e-9


def test_lst_matches_gmst_plus_lon():
    lon = 44.5
    assert abs(lst(J2000, lon) - (gmst(J2000) + lon / 15.0) % 24.0) < 1e-9


def test_equatorial_horizontal_roundtrip_native_path():
    alt, az = equatorial_to_horizontal(6.75, -16.7, 40.0, 44.5, J2000)
    assert -90 <= alt <= 90
    assert 0 <= az < 360
    ra2, dec2 = horizontal_to_equatorial(alt, az, 40.0, 44.5, J2000)
    assert abs(ra2 - 6.75) < 0.05
    assert abs(dec2 - (-16.7)) < 0.5


def test_angular_separation_sirius_pollux():
    sep = angular_separation(6.7525, -16.7161, 7.7553, 28.0262)
    assert 45 < sep < 50


def test_cosmology_native_path():
    d = luminosity_distance_mpc(0.1, Cosmology(H0=70, Om0=0.3))
    assert 430 < d < 490


def test_air_mass_zenith():
    assert abs(air_mass(90.0) - 1.0) < 1e-6


def test_ecliptic_to_equatorial_sun_near_zero():
    ra, dec = ecliptic_to_equatorial(0.0, 0.0)
    assert 0 <= ra < 24
    assert -30 < dec < 30


def test_rise_set_approx_keys():
    result = rise_set_approx(6.75, -16.7, 40.0, 44.5, J2000)
    assert "rise" in result and "transit" in result and "set" in result


def test_kepler_and_hohmann():
    period = kepler_third_law(AU, MU_SUN)
    year_sec = 365.25 * 86400
    assert abs(period - year_sec) / year_sec < 0.02
    h = hohmann_transfer(AU, 1.524 * AU, MU_SUN)
    assert h["total_dv"] > 0


def test_true_anomaly_circular():
    nu = true_anomaly_from_mean(45.0, 0.0)
    assert abs(nu - 45.0) < 0.1


def test_planet_position_native():
    pos = planet_position("earth", J2000)
    assert "lon_deg" in pos and "x_au" in pos


def test_magnitude_roundtrip():
    m = apparent_magnitude(5.0, 100.0)
    assert abs(absolute_magnitude(m, 100.0) - 5.0) < 1e-9


def test_redshift_from_velocity():
    z = redshift_from_velocity(21000.0)
    assert 0.06 < z < 0.08


def test_moon_illumination_bounds():
    illum = moon_illumination(J2000)
    assert 0.0 <= illum <= 1.0


def test_using_native_extension_bool():
    assert isinstance(using_native_extension(), bool)


def test_batch_separation_if_native():
    from aion.universe._native import angular_separation_from_target_batch

    ra = np.array([7.7553, 6.0])
    dec = np.array([28.0262, 0.0])
    seps = angular_separation_from_target_batch(6.7525, -16.7161, ra, dec)
    assert len(seps) == 2
    assert 45 < seps[0] < 50
