# Aion Physics

Classical physics toolkit for **teaching**, **simulation**, and **Physical AI** agent tools — NumPy-free scalar API, optional C++ acceleration for integrators.

> **Precision:** educational / prototyping quality, not publication-grade engineering.

## Quick start

```python
from aion.physics import (
    simulate_pendulum,
    projectile_motion,
    solve_physics_query,
    using_native_extension,
)

print("C++ extension:", using_native_extension())

result = solve_physics_query("kinetic energy mass=2 velocity=3")
print(result.output_value)  # 9.0

sim = simulate_pendulum(1.0, 0.2, steps=500)
print(sim.summary["small_angle_period_s"])
```

## CLI

```bash
aion physics query "kinetic energy mass=2 velocity=3"
aion physics pendulum --length 1 --angle-deg 15
aion physics projectile --v0 20 --angle 45
aion physics tasks
aion physics web              # browser dashboard (port 3858)
aion physics-dashboard
```

## Agent

```text
/physics query kinetic energy mass=2 velocity=3
/physics pendulum --length 1 --angle 30
/physics web
```

Agent tools: `physics_query`, `physics_simulate_pendulum`, `physics_projectile`.

Optional config in `~/.aion.yaml`:

```yaml
physics:
  default_dt: 0.01
  max_steps: 100000
  prefer_native: true
```

## Modules

| Module | Contents |
|--------|----------|
| `mechanics` | Force, momentum, energy, projectile range |
| `kinematics` | Constant-acceleration, circular motion |
| `thermo` | Ideal gas, heat energy |
| `waves` | Wave speed, SHM |
| `electromagnetism` | Coulomb, Ohm's law |
| `optics` | Snell, thin lens |
| `relativity` | Lorentz factor, E=mc² |
| `systems` | Pendulum, spring-mass, projectile simulators |
| `integrators` | Euler, RK4 |
| `pipeline` | Natural-language query router |

## C++ acceleration

When built (`pip install -e .` with pybind11 + C++14):

- `rk4_step`, `integrate_trajectory_rk4`, `pendulum_trajectory` via `aion._aion_physics`

Pure Python fallbacks always available.

## Web dashboard

```bash
./aion/physics/run_web.sh
# or
cd aion/physics/web && npm install && npm run dev   # proxies /api to 3858
```

## See also

- [Adding Physical AI](../../docs/ADDING_PHYSICAL_AI.md)
- [Universe module](../universe/README.md) — astronomy (separate scope)
