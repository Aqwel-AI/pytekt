# Adding Physical AI to PyTekt

Step-by-step guide for contributors who want to add a **Physical AI** capability to PyTekt.

This document is **documentation only**. It does not add code to the repository. Follow it when you are ready to implement.

---

## What “Physical AI” means in PyTekt

In this library, **Physical AI** means:

1. **Deterministic physics kernels** — equations, integrators, unit conversions, constraints (fast C++ where it matters).
2. **Python API** — simple imports like `from pytekt.physics import simulate_pendulum`.
3. **Optional AI layer** — agents and tools that call physics functions instead of guessing numbers.
4. **Same patterns as `pytekt.universe`** — native extension + Python fallbacks, CLI, tests, optional dashboard.

Physical AI is **not** “replace physics with an LLM.” The LLM plans and explains; the physics code computes.

### Example use cases

| Domain | Physics kernel | AI role |
|--------|----------------|---------|
| Mechanics | ODE integrator, collisions | “Simulate this setup and explain the result” |
| Thermodynamics | ideal gas, heat transfer | Parameter sweeps, natural-language queries |
| Astronomy | already in `pytekt.universe` | `/sky`, cosmology, orbits |
| Control | PID, state-space step | Tune gains, interpret stability |
| Materials | stress/strain approximations | Compare scenarios |

Start with **one domain** (e.g. classical mechanics). Expand later.

---

## Before you start

### Read these files (reference implementation)

| Topic | Path |
|-------|------|
| Astronomy module layout | `pytekt/universe/` |
| C++ fast path | `src/pytekt_universe.cpp` |
| Python ↔ C++ bridge | `pytekt/universe/_native.py` |
| Public exports | `pytekt/universe/__init__.py` |
| CLI subcommands | `pytekt/universe/cli.py`, `pytekt/cli.py` |
| Agent slash commands | Not available in 0.2.0 (`archived/aion_agent/` when restored) |
| Native extension build | `setup.py` → `_get_extensions()` |
| Tests | `tests/test_universe_*.py` |
| Module README | `pytekt/universe/README.md` |
| Project map | `docs/PROJECT_STRUCTURE.md` |

### Decide scope (write this down first)

Answer on one page:

1. **Module name** — e.g. `pytekt.physics` or `pytekt.physical` (pick one import path and keep it).
2. **v1 equations** — list exactly which formulas/simulations ship in v1.
3. **Inputs/outputs** — SI units, arrays, time steps, JSON schema for results.
4. **Precision level** — educational vs engineering (document limitations).
5. **What is C++** — only hot loops (integration, N-body, linear algebra).
6. **What stays Python** — I/O, plotting, agent tools, config.

---

## Step 1 — Create the package skeleton

Create a new directory under `pytekt/`:

```text
pytekt/physics/          # example name; adjust if you choose another
├── __init__.py        # public exports
├── constants.py       # c, G, k_B, standard units
├── units.py           # conversions (keep aligned with pytekt.universe.units where possible)
├── _native.py         # try C++ import, fall back to Python
├── mechanics.py       # e.g. pendulum, projectile, spring
├── thermo.py          # optional v1 subdomain
├── integrators.py     # Euler, RK4 — Python fallbacks live here
├── cli.py             # `pytekt physics ...` subcommands
├── pipeline.py        # optional Pipeline steps
├── examples/
│   └── demo_pendulum.py
└── README.md          # quick start for users
```

**Rules:**

- One concept per file (same style as `pytekt/universe/coordinates.py`, `orbits.py`).
- Keep pure math in small functions; avoid giant “god” modules.
- Reuse `pytekt.maths` / NumPy where it already fits; do not duplicate linear algebra.

---

## Step 2 — Define the public API (`__init__.py`)

Export only what users need. Mirror `pytekt/universe/__init__.py`:

```python
# pytekt/physics/__init__.py  (example — not in repo yet)

from .constants import G, C, K_B
from .mechanics import simulate_pendulum, projectile_motion
from ._native import using_native_extension

__all__ = [
    "G", "C", "K_B",
    "simulate_pendulum",
    "projectile_motion",
    "using_native_extension",
]
```

**Checklist:**

- [ ] Every name in `__all__` is stable (treat as public API).
- [ ] Docstring at top of package with a minimal example.
- [ ] `using_native_extension()` returns `True` when C++ is loaded.

---

## Step 3 — Add C++ for hot calculations

### 3.1 Create the source file

Add e.g. `src/pytekt_physics.cpp` next to `src/pytekt_universe.cpp`.

Put here only functions that are:

- Called in tight loops (time integration, N-body steps).
- Called on large batches (many particles, many time steps).

Keep out of C++: string parsing, file I/O, matplotlib, LLM calls.

### 3.2 Register the extension in `setup.py`

In `_get_extensions()`, add a block like the universe extension:

```python
physics_src = "src/pytekt_physics.cpp"
if os.path.isfile(physics_src):
    exts.append(
        Extension(
            "pytekt._pytekt_physics",
            sources=[physics_src],
            include_dirs=include,
            extra_compile_args=cxx_args,
            language="c++",
        )
    )
```

### 3.3 Build requirements

```bash
pip install pybind11
pip install -e .
python -c "from pytekt.physics._native import using_native_extension; print(using_native_extension())"
```

Requires **C++14** and a compiler (clang++/g++ on macOS/Linux).

### 3.4 C++ function design tips

| Do | Avoid |
|----|--------|
| `double` scalars and 1D `py::array_t<double>` batches | Returning huge nested Python dicts from C++ |
| Fixed max iterations with clear errors | Silent NaNs |
| Same formulas as Python `_foo_py` helpers | Different algorithms in C++ vs Python |
| `clamp` trig arguments to [-1, 1] | Copy-paste without tests |

---

## Step 4 — Bridge layer (`_native.py`)

Copy the pattern from `pytekt/universe/_native.py`:

```text
try:
    from pytekt._pytekt_physics import rk4_step as _rk4_step_native
    _NATIVE_AVAILABLE = True
except ImportError:
    _NATIVE_AVAILABLE = False

def using_native_extension() -> bool:
    return _NATIVE_AVAILABLE

def rk4_step(...):
    if _NATIVE_AVAILABLE:
        return _rk4_step_native(...)
    from .integrators import _rk4_step_py
    return _rk4_step_py(...)
```

**Rules:**

1. Every accelerated function has a `_*_py` twin in a normal module.
2. Native and Python paths must pass the **same tests** (within documented tolerance).
3. Never import heavy optional deps at module top level in `_native.py`.

---

## Step 5 — Wire Python modules to `_native`

High-level modules call `_native`, not C++ directly:

```python
# pytekt/physics/mechanics.py  (example)

def simulate_pendulum(length_m, theta0_rad, dt, steps):
    from ._native import pendulum_trajectory
    return pendulum_trajectory(length_m, theta0_rad, dt, steps)
```

Keep `_pendulum_trajectory_py` in the same file or in `integrators.py` for fallbacks.

---

## Step 6 — Tests

Add under `tests/`:

```text
tests/test_physics_units.py
tests/test_physics_mechanics.py
tests/test_physics_integrators.py
tests/test_physics_native.py    # optional C++ path; skip if extension missing
```

**Minimum tests:**

| Test | Purpose |
|------|---------|
| Unit conversion roundtrip | m ↔ km, J ↔ eV |
| Known analytic solution | e.g. harmonic oscillator period |
| Energy drift bound | integrator sanity (if conservative system) |
| Native vs Python | same inputs → `abs(a-b) < tol` |
| Edge cases | zero mass, negative time step → clear errors |

Run:

```bash
python -m pytest tests/test_physics_*.py -q
```

Add the new tests to `.github/workflows/ci.yml` (same line as universe tests).

---

## Step 7 — CLI (`pytekt physics`)

### 7.1 Module CLI

Create `pytekt/physics/cli.py` with `physics_main(args)` — copy structure from `pytekt/universe/cli.py`.

Example subcommands:

```bash
pytekt physics pendulum --length 1.0 --angle 30 --steps 1000
pytekt physics projectile --v0 20 --angle 45
pytekt physics units --convert 100 km_to_m
```

### 7.2 Register in `pytekt/cli.py`

1. Add parser: `subparsers.add_parser("physics", ...)`
2. Add subparsers for actions (`dest="physics_action"`).
3. In `main()`, dispatch:

```python
if args.command == "physics":
    from .physics.cli import physics_main
    physics_main(args)
```

### 7.3 Optional install extra

In `pyproject.toml`:

```toml
[project.optional-dependencies]
physics = [
    "matplotlib>=3.5.0",   # only if you add plots
]
```

---

## Step 8 — Agent integration (not available in 0.2.0)

Physical AI agent slash commands / tools land when the **terminal agent** returns. In **0.2.0**, `pytekt agent` is **not available** — ship the library CLI (`pytekt physics …`) first.

### 8.1 Slash commands (future)

When restoring from `archived/aion_agent/`, add `physics_cmds.py` (mirror universe cmds):

```text
/physics pendulum ...
/physics explain <last result>
/physics web          # optional dashboard
```

Register where slash commands are wired in the restored agent app.

### 8.2 Agent tools (future)

In the restored agent tool registry, add tools that wrap your API:

| Tool name | Calls | Returns |
|-----------|-------|---------|
| `physics_simulate_pendulum` | `simulate_pendulum(...)` | JSON trajectory summary |
| `physics_projectile` | `projectile_motion(...)` | range, max height, flight time |

**Rules for agent tools:**

- Validate inputs (positive mass, reasonable time step).
- Return **numbers from physics code**, not LLM estimates.
- Cap output size (downsample trajectories for the model).
- Document units in the tool description string.

### 8.3 Config in `~/.pytekt.yaml`

Optional section:

```yaml
physics:
  default_dt: 0.01
  max_steps: 100000
  prefer_native: true
```

Read it the same way as `universe.latitude` in `universe_cmds.py`.

---

## Step 9 — Pipeline integration (optional)

If simulations feed ML pipelines, add steps in `pytekt/physics/pipeline.py`:

```python
from pytekt.pipeline import Step

class PhysicsSimStep(Step):
    def run(self, data):
        # read params from data dict, write results back
        return data
```

Export from `pytekt/physics/__init__.py` if public.

---

## Step 10 — Optional web dashboard

Only if you need a UI (follow universe pattern):

```text
pytekt/physics/web/       # React + Vite
pytekt/physics/static/    # built assets
pytekt/physics/server.py  # stdlib HTTP server
pytekt/physics/launch.py  # port detection, browser open
```

Commands:

```bash
pytekt physics web
pytekt physics-dashboard   # alias
```

Add package data in `pyproject.toml`:

```toml
[tool.setuptools.package-data]
"pytekt.physics" = ["static/**/*", "data/*.json"]
```

This step is **optional** for v1. Ship CLI + Python API first.

---

## Step 11 — Register the package in the library

| File | Change |
|------|--------|
| `pytekt/__init__.py` | `from . import physics` |
| `docs/PROJECT_STRUCTURE.md` | Add `physics/` to tree and CLI table |
| `README.md` | Short bullet under features (link to `pytekt/physics/README.md`) |
| `pytekt/install_splash.py` | Add PHYSICS section if you use install splash |
| `MANIFEST.in` | Include static/data if any |

---

## Step 12 — Documentation for users

Write `pytekt/physics/README.md` with:

1. One-paragraph purpose and precision disclaimer.
2. Install: `pip install pytekt[physics]` and C++ build note.
3. Minimal Python example.
4. CLI examples.
5. Agent `/physics` commands.
6. Table of modules and constants.
7. List of C++-accelerated functions.

Do **not** duplicate the whole README in `docs/` — link to the module README.

---

## Step 13 — Relationship to `pytekt.universe`

| Layer | `pytekt.universe` | New `pytekt.physics` |
|-------|-----------------|---------------------|
| Scope | Astronomy, cosmology, orbits | General classical / engineering physics |
| C++ module | `pytekt._pytekt_universe` | `pytekt._pytekt_physics` |
| Shared | `constants` (c, G), unit style, `_native` pattern | Reuse or import shared SI constants |

**Do not** stuff general physics into `universe/`. Keep astronomy separate.

You may share a tiny `pytekt/physical/constants.py` later if duplication hurts — only when you have a second consumer.

---

## Step 14 — Physical AI + LLM design patterns

When connecting agents to physics:

### Pattern A — Tool-first (recommended)

```text
User question → Agent plans → Tool runs simulation → Agent explains result
```

The model never invents numeric trajectories.

### Pattern B — Physics-informed validation

```text
LLM proposes parameters → Physics checks constraints → Reject or run
```

Example: reject negative mass, angle > 180°, dt too large.

### Pattern C — Surrogate models (later)

Train a small NN on physics simulation data. Keep the **ground-truth simulator** in the same package for comparison.

### Pattern D — RAG over physics docs

Use `pytekt.rag` with your module README and equation sheets. RAG does not replace the integrator.

---

## Step 15 — Release checklist

Before opening a PR:

- [ ] `python -m pytest tests/test_physics_*.py` passes
- [ ] Works **without** C++ (`using_native_extension()` → `False`)
- [ ] Works **with** C++ after `pip install -e .`
- [ ] No API keys or local paths committed
- [ ] `pytekt/physics/README.md` complete
- [ ] `docs/PROJECT_STRUCTURE.md` updated
- [ ] CI workflow includes new tests
- [ ] Agent tools bounded (max steps, max output rows)
- [ ] Precision limits stated in README

---

## Suggested v1 milestone (smallest useful slice)

Ship this first before fluids, FEM, or ML surrogates:

1. `constants.py` + `units.py`
2. `integrators.py` — Euler + RK4 (Python + C++ `rk4_step`)
3. `mechanics.py` — pendulum + projectile
4. `tests/test_physics_*.py`
5. `pytekt physics pendulum` CLI
6. One agent tool: `physics_simulate_pendulum`
7. `pytekt/physics/README.md`

Add dashboard, thermodynamics, and control in v2.

---

## File checklist (copy when implementing)

```text
[ ] pytekt/physics/__init__.py
[ ] pytekt/physics/constants.py
[ ] pytekt/physics/units.py
[ ] pytekt/physics/_native.py
[ ] pytekt/physics/integrators.py
[ ] pytekt/physics/mechanics.py
[ ] pytekt/physics/cli.py
[ ] pytekt/physics/README.md
[ ] pytekt/physics/examples/demo_pendulum.py
[ ] src/pytekt_physics.cpp
[ ] setup.py                    (register extension)
[ ] tests/test_physics_*.py
[ ] pytekt/cli.py                 (physics subcommand)
[ ] pytekt/cli_agent/physics_cmds.py
[ ] pytekt/__init__.py            (import physics)
[ ] pyproject.toml              (optional [physics] extra)
[ ] .github/workflows/ci.yml    (new tests)
[ ] docs/PROJECT_STRUCTURE.md
```

---

## Questions to resolve before coding

1. **Import path:** `pytekt.physics` vs `pytekt.physical` vs `pytekt.physical_ai`?
2. **License for third-party numerics:** if you vendor solvers, note licenses in README.
3. **GPU:** out of scope for v1 unless you add a separate extra `[physics-cuda]`.
4. **Uncertainty:** v1 deterministic only; stochastic physics is a later doc.

---

## See also

- [Project structure](PROJECT_STRUCTURE.md)
- [Universe module README](../pytekt/universe/README.md)
- [Physics module README](../pytekt/physics/README.md)
- [Main README](../README.md) (terminal agent: not available in 0.2.0)
