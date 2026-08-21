"""
Universe Ephemeris, Orbits & Observation Planning
=================================================

Provides orbital mechanics, planetary positions, lunar almanac, and observation tools:
- Keplerian orbits, true anomaly calculation, and Hohmann orbital transfers
- Planetary positions and Kepler's third law
- Moon phase, illumination fraction, air mass, circumpolar checks, and rise/set times
- "What's up" tonight visibility calculator
- Observation logging and journaling
"""

from __future__ import annotations

from pytekt.universe.ephemeris.observations import (
    list_observations,
    log_observation,
)
from pytekt.universe.ephemeris.observing import (
    air_mass,
    is_circumpolar,
    moon_illumination,
    moon_phase,
    rise_set_approx,
    whats_up,
)
from pytekt.universe.ephemeris.orbits import (
    OrbitalElements,
    hohmann_transfer,
    kepler_third_law,
    planet_position,
    position_from_elements,
    true_anomaly_from_mean,
)

__all__ = [
    # Orbits & Mechanics
    "OrbitalElements",
    "kepler_third_law",
    "hohmann_transfer",
    "true_anomaly_from_mean",
    "position_from_elements",
    "planet_position",
    # Observing & Almanac
    "air_mass",
    "is_circumpolar",
    "moon_phase",
    "moon_illumination",
    "rise_set_approx",
    "whats_up",
    # Observations
    "log_observation",
    "list_observations",
]
