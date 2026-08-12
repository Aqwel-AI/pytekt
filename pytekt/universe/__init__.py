"""
Aion Universe — lightweight astronomy toolkit (optional C++ acceleration).

Coordinates, time, observing, orbits, cosmology, catalogs, and optional plots.

Examples
--------
>>> from pytekt.universe import equatorial_to_horizontal, moon_phase, now_jd
>>> alt, az = equatorial_to_horizontal(6.75, -16.7, 40.0, 44.5, now_jd())
>>> moon_phase(now_jd())
"""

from .constants import AU, C, G, H0_DEFAULT, J2000, LIGHT_YEAR, MU_SUN, PARSEC
from .coordinates import (
    angular_separation,
    equatorial_to_galactic,
    equatorial_to_horizontal,
    horizontal_to_equatorial,
    precess,
)
from .cosmology import (
    Cosmology,
    comoving_distance_mpc,
    hubble_flow_velocity,
    lookback_time_gyr,
    luminosity_distance_mpc,
    redshift_from_velocity,
)
from .catalogs import load_bright_stars, load_messier, load_planets, catalog_to_dataset
from .magnitude import (
    absolute_magnitude,
    apparent_magnitude,
    color_index,
    distance_modulus,
)
from .observing import (
    air_mass,
    is_circumpolar,
    moon_illumination,
    moon_phase,
    rise_set_approx,
    whats_up,
)
from .orbits import (
    OrbitalElements,
    hohmann_transfer,
    kepler_third_law,
    planet_position,
    position_from_elements,
    true_anomaly_from_mean,
)
from .time import datetime_to_jd, gmst, jd_to_datetime, lst, now_jd, mjd
from .units import (
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
from .observations import log_observation, list_observations
from .pipeline import UniverseCatalogStep, UniversePlotStep
from ._native import using_native_extension

# Deprecated aliases
CosmosCatalogStep = UniverseCatalogStep
CosmosPlotStep = UniversePlotStep

__all__ = [
    "AU",
    "C",
    "Cosmology",
    "UniverseCatalogStep",
    "UniversePlotStep",
    "CosmosCatalogStep",
    "CosmosPlotStep",
    "using_native_extension",
    "G",
    "H0_DEFAULT",
    "J2000",
    "LIGHT_YEAR",
    "MU_SUN",
    "PARSEC",
    "OrbitalElements",
    "absolute_magnitude",
    "air_mass",
    "angular_separation",
    "apparent_magnitude",
    "catalog_to_dataset",
    "color_index",
    "comoving_distance_mpc",
    "datetime_to_jd",
    "deg_to_rad",
    "distance_modulus",
    "equatorial_to_galactic",
    "equatorial_to_horizontal",
    "flux_to_magnitude",
    "format_dec",
    "format_ra",
    "gmst",
    "hohmann_transfer",
    "horizontal_to_equatorial",
    "hours_to_deg",
    "hubble_flow_velocity",
    "is_circumpolar",
    "jd_to_datetime",
    "kepler_third_law",
    "list_observations",
    "load_bright_stars",
    "load_messier",
    "load_planets",
    "log_observation",
    "lookback_time_gyr",
    "luminosity_distance_mpc",
    "lst",
    "ly_to_pc",
    "magnitude_to_flux",
    "mjd",
    "moon_illumination",
    "moon_phase",
    "now_jd",
    "parse_dec",
    "parse_ra",
    "planet_position",
    "position_from_elements",
    "precess",
    "rad_to_deg",
    "redshift_from_velocity",
    "rise_set_approx",
    "true_anomaly_from_mean",
    "whats_up",
]
