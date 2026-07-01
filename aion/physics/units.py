#!/usr/bin/env python3
"""Small unit-conversion helpers for the physics MVP."""

from __future__ import annotations


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
