"""Tests for pytekt.universe domain subpackages."""

import pytest
from pytekt.universe import (
    # Subpackages
    core,
    astrometry,
    ephemeris,
    cosmology_pkg,
    catalogs_pkg,
    service,
    # Core Constants & Functions
    AU,
    C,
    deg_to_rad,
    rad_to_deg,
    now_jd,
    # Astrometry
    angular_separation,
    equatorial_to_horizontal,
    # Ephemeris
    moon_phase,
    kepler_third_law,
    # Cosmology
    Cosmology,
    comoving_distance_mpc,
    # Catalogs
    load_bright_stars,
    load_messier,
)


def test_universe_subpackages_structure():
    assert hasattr(core, "constants")
    assert hasattr(core, "units")
    assert hasattr(core, "time")
    assert hasattr(astrometry, "coordinates")
    assert hasattr(astrometry, "magnitude")
    assert hasattr(ephemeris, "orbits")
    assert hasattr(ephemeris, "observing")
    assert hasattr(ephemeris, "observations")
    assert hasattr(cosmology_pkg, "cosmology")
    assert hasattr(catalogs_pkg, "catalogs")
    assert hasattr(service, "pipeline")
    assert hasattr(service, "viz")
    assert hasattr(service, "server")


def test_core_calculations():
    assert core.constants.C == C
    assert rad_to_deg(deg_to_rad(180.0)) == pytest.approx(180.0)
    jd = now_jd()
    assert jd > 2450000.0


def test_astrometry_calculations():
    sep = angular_separation(0.0, 0.0, 1.0, 0.0)
    assert sep == pytest.approx(15.0)


def test_ephemeris_calculations():
    phase, name = moon_phase(2451545.0)
    assert 0.0 <= phase <= 1.0
    from pytekt.universe.core.constants import MU_SUN, AU
    period = kepler_third_law(AU, MU_SUN)
    assert period > 0.0


def test_cosmology_calculations():
    cosmo = Cosmology(H0=70.0, Om0=0.3)
    assert cosmo.h == 0.7
    dist = comoving_distance_mpc(1.0, cosmo)
    assert dist > 0.0


def test_catalogs_loading():
    stars = load_bright_stars()
    assert len(stars) >= 15
    messier = load_messier()
    assert len(messier) >= 10
