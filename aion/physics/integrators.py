#!/usr/bin/env python3
"""Numerical integration helpers for simple physics simulations."""

from __future__ import annotations

from typing import Callable, List, Sequence


State = Sequence[float]
DerivativeFn = Callable[[float, State], List[float]]


def euler_step(derivative_fn: DerivativeFn, t: float, state: State, dt: float) -> List[float]:
    """Advance a dynamical system by one explicit Euler step."""
    derivatives = derivative_fn(t, state)
    return [value + dt * derivative for value, derivative in zip(state, derivatives)]


def rk4_step(derivative_fn: DerivativeFn, t: float, state: State, dt: float) -> List[float]:
    """Advance a dynamical system by one classical Runge-Kutta step."""
    k1 = derivative_fn(t, state)
    s2 = [value + 0.5 * dt * derivative for value, derivative in zip(state, k1)]
    k2 = derivative_fn(t + 0.5 * dt, s2)
    s3 = [value + 0.5 * dt * derivative for value, derivative in zip(state, k2)]
    k3 = derivative_fn(t + 0.5 * dt, s3)
    s4 = [value + dt * derivative for value, derivative in zip(state, k3)]
    k4 = derivative_fn(t + dt, s4)
    return [
        value + (dt / 6.0) * (d1 + 2.0 * d2 + 2.0 * d3 + d4)
        for value, d1, d2, d3, d4 in zip(state, k1, k2, k3, k4)
    ]


def integrate_trajectory(
    derivative_fn: DerivativeFn,
    initial_state: State,
    *,
    dt: float,
    steps: int,
    method: str = "rk4",
    t0: float = 0.0,
) -> List[List[float]]:
    """Integrate a trajectory and return every state, including the initial state."""
    if dt <= 0:
        raise ValueError("dt must be positive")
    if steps < 0:
        raise ValueError("steps must be non-negative")

    steppers = {"euler": euler_step, "rk4": rk4_step}
    if method not in steppers:
        raise ValueError("method must be 'euler' or 'rk4'")

    stepper = steppers[method]
    state = list(initial_state)
    time = t0
    trajectory = [list(state)]
    for _ in range(steps):
        state = stepper(derivative_fn, time, state, dt)
        time += dt
        trajectory.append(list(state))
    return trajectory
