"""
Universe Package
================

High-performance, domain-structured astronomy toolkit for celestial mechanics,
coordinate frames, lunar & planetary ephemerides, astronomical catalogs,
cosmological expansion, and interactive sky observation tools.

Subpackages
-----------
- ``pytekt.universe.core``        : Constants (AU, C, G, J2000), units, Julian time, and C++ native acceleration
- ``pytekt.universe.astrometry``  : Celestial coordinate frames (Equatorial/Horizontal/Galactic), precession, magnitudes
- ``pytekt.universe.ephemeris``   : Keplerian orbital mechanics, planetary positions, lunar almanac, observing visibility
- ``pytekt.universe.cosmology``   : FLRW cosmological distances, lookback time, Hubble flow velocity, redshift
- ``pytekt.universe.catalogs``    : Built-in star/Messier/planet catalogs, dataset conversion, remote SIMBAD queries
- ``pytekt.universe.service``     : Astronomy pipeline steps, sky map & orbit plots, CLI, REST API & dashboard
"""

from __future__ import annotations

import sys

# 1. Domain Subpackages
from . import (
    astrometry,
    catalogs as catalogs_pkg,
    core,
    cosmology as cosmology_pkg,
    ephemeris,
    service,
)

# 2. Subpackage Modules
from .astrometry import coordinates, magnitude
from .catalogs import catalog_fetch, catalogs as catalogs_module
from .core import _native, constants, time as time_module, units
from .cosmology import cosmology as cosmology_module
from .ephemeris import observations, observing, orbits
from .service import cli, launch, pipeline, server, viz, web_api

# 3. Backward-compatible sys.modules aliasing
_MODULE_ALIASES = {
    "pytekt.universe.constants": constants,
    "pytekt.universe.units": units,
    "pytekt.universe.time": time_module,
    "pytekt.universe._native": _native,
    "pytekt.universe.coordinates": coordinates,
    "pytekt.universe.magnitude": magnitude,
    "pytekt.universe.orbits": orbits,
    "pytekt.universe.observing": observing,
    "pytekt.universe.observations": observations,
    "pytekt.universe.cosmology": cosmology_module,
    "pytekt.universe.catalogs": catalogs_module,
    "pytekt.universe.catalog_fetch": catalog_fetch,
    "pytekt.universe.pipeline": pipeline,
    "pytekt.universe.viz": viz,
    "pytekt.universe.server": server,
    "pytekt.universe.cli": cli,
    "pytekt.universe.launch": launch,
    "pytekt.universe.web_api": web_api,
}
for _mod_name, _mod_obj in _MODULE_ALIASES.items():
    sys.modules.setdefault(_mod_name, _mod_obj)

# 4. Top-level Curated Exports

# Constants
from .core.constants import (
    AU,
    C,
    G,
    H0_DEFAULT,
    J2000,
    LIGHT_YEAR,
    MU_SUN,
    PARSEC,
)

# Astrometry & Coordinates
from .astrometry.coordinates import (
    angular_separation,
    equatorial_to_galactic,
    equatorial_to_horizontal,
    horizontal_to_equatorial,
    precess,
)
from .astrometry.magnitude import (
    absolute_magnitude,
    apparent_magnitude,
    color_index,
    distance_modulus,
)

# Cosmology
from .cosmology.cosmology import (
    Cosmology,
    comoving_distance_mpc,
    hubble_flow_velocity,
    lookback_time_gyr,
    luminosity_distance_mpc,
    redshift_from_velocity,
)

# Catalogs
from .catalogs.catalogs import (
    catalog_to_dataset,
    load_bright_stars,
    load_messier,
    load_planets,
)

# Ephemeris & Observing
from .ephemeris.observations import (
    list_observations,
    log_observation,
)
from .ephemeris.observing import (
    air_mass,
    is_circumpolar,
    moon_illumination,
    moon_phase,
    rise_set_approx,
    whats_up,
)
from .ephemeris.orbits import (
    OrbitalElements,
    hohmann_transfer,
    kepler_third_law,
    planet_position,
    position_from_elements,
    true_anomaly_from_mean,
)

# Time & Units
from .core.time import (
    datetime_to_jd,
    gmst,
    jd_to_datetime,
    lst,
    mjd,
    now_jd,
)
from .core.units import (
    deg_to_rad,
    flux_to_magnitude,
    format_dec,
    format_ra,
    hours_to_deg,
    ly_to_pc,
    magnitude_to_flux,
    parse_dec,
    parse_ra,
    rad_to_deg,
)

# Service & Pipeline
from .service.pipeline import (
    UniverseCatalogStep,
    UniversePlotStep,
)
from .core._native import using_native_extension

# Deprecated aliases
CosmosCatalogStep = UniverseCatalogStep
CosmosPlotStep = UniversePlotStep

__all__ = [
    # Subpackages
    "core",
    "astrometry",
    "ephemeris",
    "cosmology_pkg",
    "catalogs_pkg",
    "service",
    # Constants
    "AU",
    "C",
    "G",
    "H0_DEFAULT",
    "J2000",
    "LIGHT_YEAR",
    "MU_SUN",
    "PARSEC",
    # Core & Native
    "using_native_extension",
    "deg_to_rad",
    "rad_to_deg",
    "hours_to_deg",
    "format_ra",
    "format_dec",
    "parse_ra",
    "parse_dec",
    "flux_to_magnitude",
    "magnitude_to_flux",
    "ly_to_pc",
    "datetime_to_jd",
    "jd_to_datetime",
    "now_jd",
    "mjd",
    "gmst",
    "lst",
    # Astrometry & Coordinates
    "angular_separation",
    "equatorial_to_galactic",
    "equatorial_to_horizontal",
    "horizontal_to_equatorial",
    "precess",
    "apparent_magnitude",
    "absolute_magnitude",
    "distance_modulus",
    "color_index",
    # Ephemeris & Observing
    "OrbitalElements",
    "kepler_third_law",
    "hohmann_transfer",
    "true_anomaly_from_mean",
    "position_from_elements",
    "planet_position",
    "air_mass",
    "is_circumpolar",
    "moon_phase",
    "moon_illumination",
    "rise_set_approx",
    "whats_up",
    "log_observation",
    "list_observations",
    # Cosmology
    "Cosmology",
    "comoving_distance_mpc",
    "luminosity_distance_mpc",
    "lookback_time_gyr",
    "hubble_flow_velocity",
    "redshift_from_velocity",
    # Catalogs
    "load_bright_stars",
    "load_messier",
    "load_planets",
    "catalog_to_dataset",
    # Service & Pipelines
    "UniverseCatalogStep",
    "UniversePlotStep",
    "CosmosCatalogStep",
    "CosmosPlotStep",
]
