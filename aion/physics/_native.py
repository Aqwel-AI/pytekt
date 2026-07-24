"""
Optional C++ extension bridge for :mod:`aion.physics`.

Uses ``aion._aion_physics`` when built; otherwise pure-Python fallbacks.
"""

from __future__ import annotations

from typing import Callable, List, Sequence

try:
    from aion._aion_physics import (
        integrate_trajectory_rk4 as _integrate_trajectory_rk4_native,
        pendulum_trajectory as _pendulum_trajectory_native,
        rk4_step as _rk4_step_native,
    )

    _NATIVE_AVAILABLE = True
except ImportError:
    _NATIVE_AVAILABLE = False


State = Sequence[float]
DerivativeFn = Callable[[float, State], List[float]]


def using_native_extension() -> bool:
    return _NATIVE_AVAILABLE


def rk4_step(derivative_fn: DerivativeFn, t: float, state: State, dt: float) -> List[float]:
    if _NATIVE_AVAILABLE:
        return list(_rk4_step_native(derivative_fn, t, list(state), dt))
    from .integrators import rk4_step as _rk4_step_py

    return _rk4_step_py(derivative_fn, t, state, dt)


def integrate_trajectory(
    derivative_fn: DerivativeFn,
    initial_state: State,
    *,
    dt: float,
    steps: int,
    method: str = "rk4",
    t0: float = 0.0,
) -> List[List[float]]:
    if method == "rk4" and _NATIVE_AVAILABLE:
        return _integrate_trajectory_rk4_native(derivative_fn, list(initial_state), dt, steps, t0)
    from .integrators import _integrate_trajectory_py

    return _integrate_trajectory_py(
        derivative_fn, initial_state, dt=dt, steps=steps, method=method, t0=t0
    )


def pendulum_trajectory(
    length: float,
    theta0: float,
    dt: float,
    steps: int,
    gravity: float = 9.80665,
    omega0: float = 0.0,
) -> List[List[float]]:
    if _NATIVE_AVAILABLE:
        return _pendulum_trajectory_native(length, theta0, dt, steps, gravity, omega0)
    from .systems import _pendulum_derivative
    from .integrators import _integrate_trajectory_py

    derivative = _pendulum_derivative(length, gravity)
    return _integrate_trajectory_py(
        derivative, [theta0, omega0], dt=dt, steps=steps, method="rk4"
    )
