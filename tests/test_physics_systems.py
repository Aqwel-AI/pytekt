from math import pi

import aion.physics.systems as sys


def test_pendulum_small_angle_period():
    result = sys.simulate_pendulum(1.0, 0.1, dt=0.01, steps=500)
    assert result.summary["small_angle_period_s"] > 1.9


def test_projectile_no_drag():
    result = sys.projectile_motion(20.0, 45.0, dt=0.01, steps=500, drag_coeff=0.0)
    assert result.summary["range_m"] > 30.0
    assert result.summary["max_height_m"] > 5.0


def test_spring_mass():
    result = sys.simulate_spring_mass(1.0, 4.0, 1.0, 0.0, dt=0.01, steps=200)
    assert result.summary["period_s"] == pi
