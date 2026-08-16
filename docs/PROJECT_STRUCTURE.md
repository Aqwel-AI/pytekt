# PyTekt project structure

> **Aqwel AI product** — see [README](../README.md#pytekt-product-documentation).

**PyTekt 0.2.0** ships as a **research library** (`import pytekt`). The terminal coding agent is **not available** in this release (CLI stubs only; source under `archived/pytekt_agent/` locally).

| Focus | Package path | Entry |
|-------|--------------|-------|
| **Research library** | `pytekt/*` | `import pytekt` / `pytekt …` CLI |
| **Terminal agent** | **Not available** in 0.2.0 | — |

Shared today: `pytekt.providers`, `pytekt.tools`, `pytekt.rag`, Core ML, physics, universe, vision.

---

## Repository root

```
.
├── README.md                 # Main documentation
├── SECURITY.md
├── .env.example
├── docs/
│   ├── PROJECT_STRUCTURE.md  # This file
│   └── ADDING_PHYSICAL_AI.md # Guide for Physical AI modules
├── pyproject.toml
├── pytekt/                     # Python package (research library)
├── src/                      # Optional native C++ extensions
└── tests/
```

**Private (never commit):** `.env`, `~/.pytekt.yaml`, checkpoints, `wandb/`, `.cursor/`, `.pytekt/` — see [SECURITY.md](../SECURITY.md) and [.gitignore](../.gitignore).

**Local only (gitignored):** build artifacts and private config — not part of the installable package.

---

## Coding agent (not available)

In 0.2.0:

- `pytekt agent` / `pytekt api` / `pytekt auth` print **not available**
- No `pytekt/cli_agent/` in the wheel
- Do **not** add a new `pytekt/agent/` package path

Future work: a terminal coding agent is **not** part of this package.

---

## Research library (high level)

```
pytekt/
├── maths.py, algorithms/
├── preprocessing/, models/, metrics/, hyperopt/   # Core ML
├── data/, datasets/
├── providers/, tools/, rag/
├── former/, visualization/, ui/, hub/
├── tracker/, llm_eval/, db/, universe/, physics/, cache/, store/, pipeline/
├── experiments/, bench/, benchmarks/
├── io/, config/, env/, serve/, monitor/, vision/
├── user_config.py, install_splash.py
└── cli.py
```

Install extras: `[ai]`, `[viz]`, `[rag]`, `[config]`, `[db]`, `[universe]`, `[physics]`, `[vision]`, `[full]`.

**`pytekt/universe/`** — coordinates, time, observing, orbits, cosmology, catalogs, C++ extension (`_pytekt_universe`), optional viz, React web dashboard. See [`pytekt/universe/README.md`](../pytekt/universe/README.md). `pytekt/cosmos` is a deprecated import shim.

**`pytekt/physics/`** — classical mechanics, thermo, EM, optics, relativity, integrators, NL query router, C++ extension (`_pytekt_physics`), React web dashboard (port 3858). See [`pytekt/physics/README.md`](../pytekt/physics/README.md).

**`pytekt/vision/`** — computer vision on NumPy arrays (I/O, transforms, color, filters, draw, metrics, OpenCV). Extra: `[vision]`. CLI: `pytekt vision`. See [`pytekt/vision/README.md`](../pytekt/vision/README.md). Separate from `pytekt.visualization` (plots).

---

## CLI commands

| Command | Module |
|---------|--------|
| `pytekt config` | `pytekt.user_config` |
| `pytekt agent` / `api` / `auth` | Not available in 0.2.0 |
| `pytekt universe` / `pytekt universe-dashboard` | `pytekt.universe.cli` / `pytekt.universe.launch` |
| `pytekt physics` / `pytekt physics-dashboard` | `pytekt.physics.cli` / `pytekt.physics.launch` |
| `pytekt vision` | `pytekt.vision.cli` |
| `pytekt db` | `pytekt.db.cli` |
| `pytekt start` | `pytekt.hub` |
| `pytekt welcome` | `pytekt.install_splash` |
| `python -m pytekt` | `pytekt.cli` |

---

## Hygiene checklist

- [ ] No `pytekt/agent/` or `pytekt/code/` directories (only `code.py` module)
- [ ] No API keys in git — use `~/.pytekt.yaml` or `.env`
- [ ] `__pycache__/` not committed (in `.gitignore`)
- [ ] Docs match shipping surface (agent = not available in 0.2.0)
