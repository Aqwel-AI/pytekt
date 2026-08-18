import pytest

import pytekt.physics.pipeline as p


@pytest.mark.parametrize(
    "query,task",
    [
        ("kinetic energy mass=2 velocity=3", "kinetic_energy"),
        ("force mass=2 acceleration=3", "force"),
        ("potential energy mass=2 height=5", "potential_energy"),
        ("momentum mass=2 velocity=3", "momentum"),
        ("ideal gas pressure moles=1 temperature=300 volume=0.1", "ideal_gas_pressure"),
        ("heat energy mass=1 c=4200 delta_t=10", "heat_energy"),
        ("free fall height=10", "free_fall"),
        ("projectile range v0=20 angle=45", "projectile_range"),
        ("coulomb force q1=1e-6 q2=1e-6 distance=0.1", "coulomb_force"),
    ],
)
def test_solve_physics_query_tasks(query, task):
    result = p.solve_physics_query(query)
    assert result.task == task
    assert result.output_value == result.output_value  # not nan


def test_supported_tasks_non_empty():
    tasks = p.supported_physics_tasks()
    assert len(tasks) >= 10
