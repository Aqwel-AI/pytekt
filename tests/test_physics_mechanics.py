import aion.physics.kinematics as k
import aion.physics.mechanics as m


def test_force_and_kinetic_energy():
    assert m.force(2.0, 3.0) == 6.0
    assert m.kinetic_energy(2.0, 3.0) == 9.0


def test_kinematics():
    assert k.velocity_from_uat(0.0, 2.0, 3.0) == 6.0
    assert k.displacement_from_uat(0.0, 2.0, 3.0) == 9.0


def test_centripetal_force():
    f = k.centripetal_force(2.0, 3.0, 1.5)
    assert round(f, 6) == round(2.0 * 9.0 / 1.5, 6)
