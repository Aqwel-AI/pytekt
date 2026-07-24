import pytest

from aion.physics._native import using_native_extension
from aion.physics.integrators import _integrate_trajectory_py


@pytest.mark.skipif(not using_native_extension(), reason="C++ physics extension not built")
def test_native_pendulum_matches_python():
    from aion.physics._native import pendulum_trajectory

    native = pendulum_trajectory(1.0, 0.2, 0.01, 100, 9.80665, 0.0)

    def deriv(_t, state):
        from math import sin

        theta, omega = state
        g = 9.80665
        return [omega, -(g / 1.0) * sin(theta)]

    python = _integrate_trajectory_py(deriv, [0.2, 0.0], dt=0.01, steps=100, method="rk4")
    for n_row, p_row in zip(native, python):
        for n, p in zip(n_row, p_row):
            assert abs(n - p) < 1e-9
