"""Tests for aion.universe.time."""

from datetime import datetime, timezone

from aion.universe.constants import J2000
from aion.universe.time import datetime_to_jd, gmst, jd_to_datetime, lst, mjd


def test_j2000_epoch():
    jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
    assert abs(jd - J2000) < 0.001


def test_jd_datetime_roundtrip():
    jd = 2451545.25
    dt = jd_to_datetime(jd)
    jd2 = datetime_to_jd(dt)
    assert abs(jd2 - jd) < 1 / 86400.0


def test_mjd_offset():
    assert abs(mjd(J2000) - 51544.5) < 1e-6


def test_gmst_lst_range():
    g = gmst(J2000)
    assert 0 <= g < 24
    l = lst(J2000, 44.5)
    assert 0 <= l < 24
