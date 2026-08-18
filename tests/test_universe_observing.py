"""Tests for pytekt.universe.observing and catalogs."""

import math

from pytekt.universe.catalogs import load_bright_stars, load_messier, load_planets
from pytekt.universe.constants import J2000
from pytekt.universe.observing import air_mass, build_sky_catalog, moon_phase, whats_up, whats_up_all


def test_moon_phase_bounds():
    phase, name = moon_phase(J2000)
    assert 0.0 <= phase <= 1.0
    assert isinstance(name, str) and name


def test_air_mass_zenith():
    assert abs(air_mass(90.0) - 1.0) < 1e-6


def test_air_mass_below_horizon():
    assert math.isinf(air_mass(0.0))


def test_whats_up_returns_sorted():
    visible = whats_up(40.0, 44.5, J2000)
    assert isinstance(visible, list)
    if len(visible) >= 2:
        assert visible[0]["altitude"] >= visible[1]["altitude"]
    for row in visible:
        assert "altitude" in row and row["altitude"] >= 10.0


def test_build_sky_catalog_all():
    rows = build_sky_catalog("all", J2000)
    kinds = {r.get("kind") for r in rows}
    assert "star" in kinds
    assert "messier" in kinds
    assert "planet" in kinds


def test_whats_up_all_sorted():
    visible = whats_up_all(40.0, 44.5, J2000, catalog_mode="all", min_altitude=0.0)
    if len(visible) >= 2:
        assert visible[0]["altitude"] >= visible[1]["altitude"]


def test_builtin_catalogs_nonempty():
    assert len(load_bright_stars()) >= 10
    assert len(load_messier()) >= 10
    assert len(load_planets()) >= 8


def test_log_observation_sqlite(tmp_path, monkeypatch):
    from pytekt.universe.observations import list_observations, log_observation

    monkeypatch.chdir(tmp_path)
    db_url = "sqlite://./cosmos.db"
    log_observation(
        latitude=40.0,
        longitude=44.5,
        objects=[{"name": "Sirius", "altitude": 20.0}],
        notes="test",
        db_url=db_url,
    )
    rows = list_observations(db_url=db_url)
    assert len(rows) == 1
    assert rows[0]["object_count"] == 1
