"""Tests for aion.cosmos.coordinates."""

from aion.cosmos.constants import J2000
from aion.cosmos.coordinates import (
    angular_separation,
    equatorial_to_galactic,
    equatorial_to_horizontal,
    horizontal_to_equatorial,
)
from aion.cosmos.units import parse_dec, parse_ra


def test_angular_separation_sirius_pollux():
    sirius_ra = parse_ra("6h 45m 08s")
    sirius_dec = parse_dec("-16d 42m 58s")
    pollux_ra = 7.7553
    pollux_dec = 28.0262
    sep = angular_separation(sirius_ra, sirius_dec, pollux_ra, pollux_dec)
    assert 45 < sep < 50


def test_polaris_altitude_near_latitude():
    ra, dec = 2.5303, 89.2641
    lat, lon = 40.0, 0.0
    alt, _ = equatorial_to_horizontal(ra, dec, lat, lon, J2000)
    assert abs(alt - lat) < 2.0


def test_horizontal_equatorial_roundtrip():
    ra, dec = 6.75, -16.7
    lat, lon, jd = 40.0, 44.5, J2000
    alt, az = equatorial_to_horizontal(ra, dec, lat, lon, jd)
    ra2, dec2 = horizontal_to_equatorial(alt, az, lat, lon, jd)
    assert abs(ra2 - ra) < 0.05
    assert abs(dec2 - dec) < 0.5


def test_equatorial_to_galactic_sirius():
    l, b = equatorial_to_galactic(6.75, -16.7)
    assert -100 < l < 100
    assert -90 <= b <= 90
