#!/usr/bin/env python3
"""Unit-conversion helpers for the physics toolkit."""

from __future__ import annotations

from math import pi


def celsius_to_kelvin(value: float) -> float:
    """Convert temperature from Celsius to Kelvin."""
    return value + 273.15


def kelvin_to_celsius(value: float) -> float:
    """Convert temperature from Kelvin to Celsius."""
    return value - 273.15


def meters_to_kilometers(value: float) -> float:
    """Convert meters to kilometers."""
    return value / 1000.0


def kilometers_to_meters(value: float) -> float:
    """Convert kilometers to meters."""
    return value * 1000.0


def joules_to_kilojoules(value: float) -> float:
    """Convert joules to kilojoules."""
    return value / 1000.0


def kilojoules_to_joules(value: float) -> float:
    """Convert kilojoules to joules."""
    return value * 1000.0


def m_to_cm(value: float) -> float:
    """Convert meters to centimeters."""
    return value * 100.0


def cm_to_m(value: float) -> float:
    """Convert centimeters to meters."""
    return value / 100.0


def ev_to_joules(value: float) -> float:
    """Convert electron-volts to joules."""
    return value * 1.602176634e-19


def joules_to_ev(value: float) -> float:
    """Convert joules to electron-volts."""
    return value / 1.602176634e-19


def newtons_to_kilonewtons(value: float) -> float:
    """Convert newtons to kilonewtons."""
    return value / 1000.0


def kilonewtons_to_newtons(value: float) -> float:
    """Convert kilonewtons to newtons."""
    return value * 1000.0


def pascals_to_kpa(value: float) -> float:
    """Convert pascals to kilopascals."""
    return value / 1000.0


def kpa_to_pascals(value: float) -> float:
    """Convert kilopascals to pascals."""
    return value * 1000.0


def watts_to_kilowatts(value: float) -> float:
    """Convert watts to kilowatts."""
    return value / 1000.0


def kilowatts_to_watts(value: float) -> float:
    """Convert kilowatts to watts."""
    return value * 1000.0


def degrees_to_radians(value: float) -> float:
    """Convert degrees to radians."""
    return value * pi / 180.0


def radians_to_degrees(value: float) -> float:
    """Convert radians to degrees."""
    return value * 180.0 / pi
