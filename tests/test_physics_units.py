import aion.physics.units as u


def test_temperature_roundtrip():
    assert u.kelvin_to_celsius(u.celsius_to_kelvin(25.0)) == 25.0


def test_length_roundtrip():
    assert u.kilometers_to_meters(u.meters_to_kilometers(2500.0)) == 2500.0
    assert u.cm_to_m(u.m_to_cm(2.5)) == 2.5


def test_energy_roundtrip():
    assert u.joules_to_ev(u.ev_to_joules(1.0)) == 1.0


def test_angle_roundtrip():
    assert u.radians_to_degrees(u.degrees_to_radians(90.0)) == 90.0
