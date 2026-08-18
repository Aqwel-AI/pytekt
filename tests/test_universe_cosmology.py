"""Tests for cosmology, magnitude, and orbits."""

from pytekt.universe.cosmology import (
    Cosmology,
    hubble_flow_velocity,
    lookback_time_gyr,
    luminosity_distance_mpc,
    redshift_from_velocity,
)
from pytekt.universe.magnitude import absolute_magnitude, apparent_magnitude, distance_modulus
from pytekt.universe.orbits import (
    OrbitalElements,
    hohmann_transfer,
    kepler_third_law,
    planet_position,
    true_anomaly_from_mean,
)
from pytekt.universe.constants import AU, J2000, MU_SUN


def test_distance_modulus_10pc():
    assert abs(distance_modulus(10.0)) < 1e-12


def test_apparent_absolute_roundtrip():
    m = apparent_magnitude(5.0, 100.0)
    assert abs(absolute_magnitude(m, 100.0) - 5.0) < 1e-9


def test_luminosity_distance_z01():
    d_l = luminosity_distance_mpc(0.1, Cosmology(H0=70, Om0=0.3))
    assert 430 < d_l < 490


def test_hubble_flow():
    v = hubble_flow_velocity(100.0)
    assert abs(v - 7000.0) < 1.0


def test_redshift_from_velocity_low():
    z = redshift_from_velocity(21000.0)
    assert 0.06 < z < 0.08


def test_lookback_z01_gyr():
    t = lookback_time_gyr(0.1, Cosmology(H0=70, Om0=0.3))
    assert 1.0 < t < 1.6


def test_kepler_third_law_earth():
    period = kepler_third_law(AU, MU_SUN)
    year_sec = 365.25 * 86400
    assert abs(period - year_sec) / year_sec < 0.02


def test_true_anomaly_circular():
    nu = true_anomaly_from_mean(45.0, 0.0)
    assert abs(nu - 45.0) < 0.1


def test_hohmann_transfer_positive_dv():
    result = hohmann_transfer(AU, 1.524 * AU, MU_SUN)
    assert result["dv1"] > 0 and result["dv2"] > 0
    assert result["total_dv"] > 0


def test_planet_position_keys():
    pos = planet_position("earth", J2000)
    assert set(pos.keys()) >= {"x_au", "y_au", "z_au", "r_au"}
