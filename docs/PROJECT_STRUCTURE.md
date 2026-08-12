# Aion project structure

> **Aqwel AI product** — see [README](../README.md#aion-product-documentation).

**Aion 0.2.0** ships as a **research library** (`import pytekt`). The terminal coding agent is **not available** in this release (CLI stubs only; source under `archived/aion_agent/` locally).

| Focus | Package path | Entry |
|-------|--------------|-------|
| **Research library** | `aion/*` | `import pytekt` / `aion …` CLI |
| **Terminal agent** | **Not available** in 0.2.0 | — |

Shared today: `aion.providers`, `aion.tools`, `aion.rag`, Core ML, physics, universe, vision.

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
├── aion/                     # Python package (research library)
├── src/                      # Optional native C++ extensions
└── tests/
```

**Private (never commit):** `.env`, `~/.aion.yaml`, checkpoints, `wandb/`, `.cursor/`, `.aion/` — see [SECURITY.md](../SECURITY.md) and [.gitignore](../.gitignore).

**Local only (gitignored):** build artifacts and private config — not part of the installable package.

---

## Coding agent (not available)

In 0.2.0:

- `pytekt agent` / `aion api` / `aion auth` print **not available**
- No `aion/cli_agent/` in the wheel
- Do **not** add a new `aion/agent/` package path

Future work: a terminal coding agent is **not** part of this package.

---

## Research library (high level)

```
aion/
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

**`aion/universe/`** — coordinates, time, observing, orbits, cosmology, catalogs, C++ extension (`_aion_universe`), optional viz, React web dashboard. See [`aion/universe/README.md`](../aion/universe/README.md). `aion/cosmos` is a deprecated import shim.

**`aion/physics/`** — classical mechanics, thermo, EM, optics, relativity, integrators, NL query router, C++ extension (`_aion_physics`), React web dashboard (port 3858). See [`aion/physics/README.md`](../aion/physics/README.md).

**`aion/vision/`** — computer vision on NumPy arrays (I/O, transforms, color, filters, draw, metrics, OpenCV). Extra: `[vision]`. CLI: `pytekt vision`. See [`aion/vision/README.md`](../aion/vision/README.md). Separate from `aion.visualization` (plots).

---

## CLI commands

| Command | Module |
|---------|--------|
| `aion config` | `aion.user_config` |
| `pytekt agent` / `api` / `auth` | Not available in 0.2.0 |
| `pytekt universe` / `pytekt universe-dashboard` | `pytekt.universe.cli` / `pytekt.universe.launch` |
| `pytekt physics` / `pytekt physics-dashboard` | `pytekt.physics.cli` / `pytekt.physics.launch` |
| `pytekt vision` | `pytekt.vision.cli` |
| `aion db` | `aion.db.cli` |
| `aion start` | `aion.hub` |
| `aion welcome` | `aion.install_splash` |
| `python -m pytekt` | `aion.cli` |

---

## Hygiene checklist

- [ ] No `aion/agent/` or `aion/code/` directories (only `code.py` module)
- [ ] No API keys in git — use `~/.aion.yaml` or `.env`
- [ ] `__pycache__/` not committed (in `.gitignore`)
- [ ] Docs match shipping surface (agent = not available in 0.2.0)
