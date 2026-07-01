import aion


def test_force_and_kinetic_energy():
    assert aion.physics.mechanics.force(2.0, 3.0) == 6.0
    assert aion.physics.mechanics.kinetic_energy(2.0, 3.0) == 9.0


def test_ideal_gas_pressure():
    pressure = aion.physics.thermo.ideal_gas_pressure(1.0, 300.0, 0.1)
    assert round(pressure, 6) == round(8.314462618 * 300.0 / 0.1, 6)


def test_unit_conversions():
    assert aion.physics.units.celsius_to_kelvin(0.0) == 273.15
    assert aion.physics.units.kilometers_to_meters(2.5) == 2500.0


def test_integrate_trajectory_euler():
    def derivative(_t, state):
        return [state[1], -9.0]

    trajectory = aion.physics.integrators.integrate_trajectory(
        derivative,
        [0.0, 10.0],
        dt=0.1,
        steps=2,
        method="euler",
    )
    assert len(trajectory) == 3
    assert trajectory[1][0] == 1.0


def test_solve_physics_query():
    result = aion.physics.solve_physics_query("kinetic energy mass=2 velocity=3")
    assert result.task == "kinetic_energy"
    assert result.output_value == 9.0


def test_supported_physics_tasks():
    tasks = aion.physics.pipeline.supported_physics_tasks()
    assert any("force" in task for task in tasks)
