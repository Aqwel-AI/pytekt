#!/usr/bin/env python3
"""Small thermodynamics helpers for the physics MVP."""

from __future__ import annotations

from .constants import IDEAL_GAS_CONSTANT
from .units import celsius_to_kelvin


def ideal_gas_pressure(moles: float, temperature_kelvin: float, volume: float) -> float:
    """Return pressure from the ideal gas law ``P = nRT / V``."""
    if volume <= 0:
        raise ValueError("volume must be positive")
    return moles * IDEAL_GAS_CONSTANT * temperature_kelvin / volume


def ideal_gas_temperature(pressure: float, volume: float, moles: float) -> float:
    """Return temperature from the ideal gas law ``T = PV / (nR)``."""
    if moles <= 0:
        raise ValueError("moles must be positive")
    return pressure * volume / (moles * IDEAL_GAS_CONSTANT)


def heat_energy(mass: float, specific_heat_capacity: float, delta_temperature: float) -> float:
    """Return heat energy from ``Q = m * c * delta_T``."""
    return mass * specific_heat_capacity * delta_temperature


def ideal_gas_pressure_from_celsius(moles: float, temperature_celsius: float, volume: float) -> float:
    """Return ideal-gas pressure when temperature is provided in Celsius."""
    return ideal_gas_pressure(moles, celsius_to_kelvin(temperature_celsius), volume)
