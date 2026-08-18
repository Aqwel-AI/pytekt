#!/usr/bin/env python3
"""High-level physics simulations built on integrators."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, radians, sin, sqrt
from typing import Dict, List, Sequence

from .constants import GRAVITATIONAL_ACCELERATION
from .integrators import DerivativeFn, integrate_trajectory
from .mechanics import projectile_range


@dataclass
class SimulationResult:
    """Structured output from a physics simulation."""

    trajectory: List[List[float]]
    times: List[float]
    summary: Dict[str, float]


def _pendulum_derivative(length: float, gravity: float) -> DerivativeFn:
    def derivative(_t: float, state: Sequence[float]) -> List[float]:
        theta, omega = state
        alpha = -(gravity / length) * sin(theta)
        return [omega, alpha]

    return derivative


def simulate_pendulum(
    length_m: float,
    theta0_rad: float,
    *,
    dt: float = 0.01,
    steps: int = 1000,
    gravity: float = GRAVITATIONAL_ACCELERATION,
    omega0: float = 0.0,
) -> SimulationResult:
    """Simulate a simple pendulum; state is ``[theta, omega]``."""
    if length_m <= 0:
        raise ValueError("length_m must be positive")
    derivative = _pendulum_derivative(length_m, gravity)
    trajectory = integrate_trajectory(
        derivative,
        [theta0_rad, omega0],
        dt=dt,
        steps=steps,
        method="rk4",
    )
    times = [i * dt for i in range(len(trajectory))]
    small_angle_period = 2.0 * pi * sqrt(length_m / gravity)
    max_theta = max(abs(row[0]) for row in trajectory)
    return SimulationResult(
        trajectory=trajectory,
        times=times,
        summary={
            "length_m": length_m,
            "small_angle_period_s": small_angle_period,
            "max_theta_rad": max_theta,
            "steps": float(steps),
            "dt": dt,
        },
    )


def _spring_derivative(mass: float, spring_constant: float) -> DerivativeFn:
    def derivative(_t: float, state: Sequence[float]) -> List[float]:
        x, v = state
        return [v, -(spring_constant / mass) * x]

    return derivative


def simulate_spring_mass(
    mass: float,
    spring_constant: float,
    x0: float,
    v0: float,
    *,
    dt: float = 0.01,
    steps: int = 1000,
) -> SimulationResult:
    """Simulate a mass on a spring; state is ``[x, v]``."""
    if mass <= 0:
        raise ValueError("mass must be positive")
    if spring_constant <= 0:
        raise ValueError("spring_constant must be positive")
    derivative = _spring_derivative(mass, spring_constant)
    trajectory = integrate_trajectory(
        derivative,
        [x0, v0],
        dt=dt,
        steps=steps,
        method="rk4",
    )
    times = [i * dt for i in range(len(trajectory))]
    period = 2.0 * pi * sqrt(mass / spring_constant)
    return SimulationResult(
        trajectory=trajectory,
        times=times,
        summary={
            "mass": mass,
            "spring_constant": spring_constant,
            "period_s": period,
            "steps": float(steps),
            "dt": dt,
        },
    )


def projectile_motion(
    v0: float,
    angle_deg: float,
    *,
    dt: float = 0.01,
    steps: int = 1000,
    gravity: float = GRAVITATIONAL_ACCELERATION,
    drag_coeff: float = 0.0,
) -> SimulationResult:
    """Simulate projectile motion; returns trajectory ``[[x, y, vx, vy], ...]``."""
    if v0 < 0:
        raise ValueError("v0 must be non-negative")
    angle = radians(angle_deg)
    vx0 = v0 * cos(angle)
    vy0 = v0 * sin(angle)

    if drag_coeff == 0.0:
        flight_time = 2.0 * vy0 / gravity if vy0 > 0 else 0.0
        max_height = (vy0 * vy0) / (2.0 * gravity) if vy0 > 0 else 0.0
        range_m = projectile_range(v0, angle_deg, gravity)
        n_steps = max(steps, int(flight_time / dt) + 1) if flight_time > 0 else 1
        trajectory: List[List[float]] = []
        times: List[float] = []
        for i in range(n_steps + 1):
            t = i * dt
            if t > flight_time and flight_time > 0:
                break
            x = vx0 * t
            y = vy0 * t - 0.5 * gravity * t * t
            if y < 0 and t > 0:
                y = 0.0
            trajectory.append([x, y, vx0, vy0 - gravity * t])
            times.append(t)
        return SimulationResult(
            trajectory=trajectory,
            times=times,
            summary={
                "range_m": range_m,
                "max_height_m": max_height,
                "flight_time_s": flight_time,
                "drag_coeff": 0.0,
            },
        )

    def derivative(_t: float, state: Sequence[float]) -> List[float]:
        x, y, vx, vy = state
        speed = sqrt(vx * vx + vy * vy)
        ax = -drag_coeff * vx * speed if speed > 0 else 0.0
        ay = -gravity - drag_coeff * vy * speed if speed > 0 else -gravity
        return [vx, vy, ax, ay]

    trajectory = integrate_trajectory(
        derivative,
        [0.0, 0.0, vx0, vy0],
        dt=dt,
        steps=steps,
        method="rk4",
    )
    times = [i * dt for i in range(len(trajectory))]
    max_height = max(row[1] for row in trajectory)
    range_m = trajectory[-1][0]
    return SimulationResult(
        trajectory=trajectory,
        times=times,
        summary={
            "range_m": range_m,
            "max_height_m": max_height,
            "flight_time_s": times[-1],
            "drag_coeff": drag_coeff,
        },
    )
