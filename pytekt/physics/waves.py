#!/usr/bin/env python3
"""Wave and simple harmonic motion helpers."""

from __future__ import annotations

from math import pi, sin, sqrt


def wave_speed(frequency: float, wavelength: float) -> float:
    """Return wave speed ``v = f * lambda``."""
    return frequency * wavelength


def period_from_frequency(frequency: float) -> float:
    """Return period ``T = 1 / f``."""
    if frequency == 0:
        raise ValueError("frequency must be non-zero")
    return 1.0 / frequency


def simple_harmonic_position(
    amplitude: float,
    angular_frequency: float,
    time: float,
    *,
    phase: float = 0.0,
) -> float:
    """Return displacement ``x = A * sin(omega*t + phi)``."""
    return amplitude * sin(angular_frequency * time + phase)


def simple_harmonic_period(mass: float, spring_constant: float) -> float:
    """Return period of a mass-spring oscillator ``T = 2*pi*sqrt(m/k)``."""
    if spring_constant <= 0:
        raise ValueError("spring_constant must be positive")
    return 2.0 * pi * sqrt(mass / spring_constant)
