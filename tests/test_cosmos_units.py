"""Tests for aion.cosmos.units."""

import math

import pytest

from aion.cosmos.units import (
    flux_to_magnitude,
    format_dec,
    format_ra,
    ly_to_pc,
    magnitude_to_flux,
    parse_dec,
    parse_ra,
    pc_to_ly,
)


def test_parse_ra_sexagesimal():
    ra = parse_ra("12h 30m 15s")
    assert abs(ra - 12.504166666) < 1e-5


def test_parse_dec_signed():
    dec = parse_dec("-16d 42m 58s")
    assert abs(dec - (-16.716111)) < 1e-4


def test_format_ra_dec_roundtrip():
    ra = parse_ra("6h 45m 08s")
    dec = parse_dec("-16d 42m 58s")
    assert "6h" in format_ra(ra)
    assert "-" in format_dec(dec)


def test_ly_pc_roundtrip():
    ly = 3.26
    assert abs(pc_to_ly(ly_to_pc(ly)) - ly) < 1e-10


def test_pogson_flux_magnitude():
    m = flux_to_magnitude(100.0, flux_zero=100.0)
    assert m == 0.0
    assert abs(magnitude_to_flux(m, flux_zero=100.0) - 100.0) < 1e-12


def test_flux_to_magnitude_invalid():
    with pytest.raises(ValueError):
        flux_to_magnitude(0.0)
