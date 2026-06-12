"""Tests for aion.cosmos.web_api."""

from aion.cosmos.constants import J2000
from aion.cosmos.observing import build_sky_catalog, whats_up_all
from aion.cosmos.web_api import (
    coords_payload,
    cosmology_payload,
    library_info,
    moon_payload,
    observer_payload,
    sky_payload,
)


def test_library_info_app():
    info = library_info()
    assert info["app"] == "cosmos"
    assert "version" in info


def test_moon_payload_bounds():
    data = moon_payload(J2000)
    assert 0 <= data["phase"] <= 1
    assert data["name"]


def test_sky_payload_all_catalog():
    data = sky_payload(latitude=40.0, longitude=44.5, jd=J2000, catalog="all")
    assert data["count"] == len(data["objects"])
    kinds = {o.get("kind") for o in data["objects"]}
    assert "star" in kinds or len(data["objects"]) >= 0


def test_coords_equatorial_to_horizontal():
    data = coords_payload(
        mode="equatorial_to_horizontal",
        latitude=40.0,
        longitude=44.5,
        jd=J2000,
        ra="6h 45m 08s",
        dec="-16d 42m 58s",
    )
    assert "altitude" in data["output"]
    assert "azimuth" in data["output"]


def test_cosmology_payload_z01():
    data = cosmology_payload(0.1, h0=70, om0=0.3)
    assert 430 < data["luminosity_distance_mpc"] < 490
    assert data["lookback_time_gyr"] > 0


def test_observer_payload_defaults():
    data = observer_payload(latitude=35.0, longitude=10.0, jd=J2000)
    assert data["latitude"] == 35.0
    assert data["jd"] == J2000


def test_whats_up_all_includes_planets():
    visible = whats_up_all(0.0, 0.0, J2000, catalog_mode="planets", min_altitude=-90.0)
    assert len(visible) == 8
