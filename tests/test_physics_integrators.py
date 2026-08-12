import pytekt.physics.integrators as ig


def test_integrate_trajectory_euler():
    def derivative(_t, state):
        return [state[1], -9.0]

    trajectory = ig.integrate_trajectory(
        derivative,
        [0.0, 10.0],
        dt=0.1,
        steps=2,
        method="euler",
    )
    assert len(trajectory) == 3
    assert trajectory[1][0] == 1.0


def test_rk4_harmonic_oscillator_period():
    def derivative(_t, state):
        return [state[1], -state[0]]

    trajectory = ig.integrate_trajectory(
        derivative,
        [1.0, 0.0],
        dt=0.01,
        steps=628,
        method="rk4",
    )
    assert abs(trajectory[-1][0] - trajectory[0][0]) < 0.15
