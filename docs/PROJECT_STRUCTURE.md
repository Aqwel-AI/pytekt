# Aion project structure

> **Aqwel AI product** — see [README](../README.md#aion-product-documentation).

**Aion 0.2.0** ships as a **research library** (`import aion`) with a multi-purpose terminal CLI. The CLI includes research, data, provider, experiment, and safe workspace-inspection commands.

| Focus | Package path | Entry |
|-------|--------------|-------|
| **Research library** | `aion/*` | `import aion` / `aion …` CLI |
| **Terminal CLI** | `aion.cli` / `aion.cli_extensions` | `aion …` |

Shared today: `aion.providers`, `aion.tools`, `aion.rag`, Core ML, physics, universe, vision.

---

## Repository root

```
.
├── README.md                 # Main documentation
├── SECURITY.md
├── .env.example
├── docs/
│   ├── CLI.md                # Complete terminal command reference
│   ├── PROJECT_STRUCTURE.md  # This file
│   └── ADDING_PHYSICAL_AI.md # Guide for Physical AI modules
├── pyproject.toml
├── aion/                     # Python package (research library)
├── r_pytekt/                 # R language bindings (Rcpp, R ≥ 4.0)
├── src/                      # Optional native C++ extensions
└── tests/
```

**Private (never commit):** `.env`, `~/.aion.yaml`, checkpoints, `wandb/`, `.cursor/`, `.aion/` — see [SECURITY.md](../SECURITY.md) and [.gitignore](../.gitignore).

**Local only (gitignored):** build artifacts and private config — not part of the installable package.

---

## Workspace agent

The current lightweight workspace agent provides read/search inspection:

- `aion agent --root .`
- `aion agent read path/to/file.py`
- `aion agent search pattern`

It is not an autonomous coding agent and does not perform model-driven file
edits. API serving is available separately through `aion serve` / `aion api`.

An autonomous model-driven coding agent is not part of this package.

---

## Research library (high level)

```
aion/
├── maths/                         # Sectioned mathematics package
│   ├── maths.py                   # Flat compatibility API
│   ├── arithmetic/, random/       # Each contains functions.py and __init__.py
│   ├── linear_algebra/, statistics/
│   ├── trigonometry/, machine_learning/
│   ├── signal_processing/, probability/
│   └── number_theory/, utilities/
├── algorithms/
├── preprocessing/, models/, metrics/, hyperopt/   # Core ML
├── data/, datasets/
├── providers/, tools/, rag/
├── former/, visualization/, ui/, hub/
├── tracker/, llm_eval/, db/, universe/, physics/, cache/, store/, pipeline/
├── experiments/, bench/, benchmarks/
├── io/, config/, env/, serve/, monitor/, vision/
├── user_config.py, install_splash.py
├── cli.py                  # command entry point and command catalog
└── cli_extensions.py       # research, data, provider, and operations commands
```

Install extras: `[ai]`, `[viz]`, `[rag]`, `[config]`, `[db]`, `[universe]`, `[physics]`, `[vision]`, `[full]`.

**`aion/universe/`** — coordinates, time, observing, orbits, cosmology, catalogs, C++ extension (`_aion_universe`), optional viz, React web dashboard. See [`aion/universe/README.md`](../aion/universe/README.md). `aion/cosmos` is a deprecated import shim.

**`aion/physics/`** — classical mechanics, thermo, EM, optics, relativity, integrators, NL query router, C++ extension (`_aion_physics`), React web dashboard (port 3858). See [`aion/physics/README.md`](../aion/physics/README.md).

**`aion/vision/`** — computer vision on NumPy arrays (I/O, transforms, color, filters, draw, metrics, OpenCV). Extra: `[vision]`. CLI: `aion vision`. See [`aion/vision/README.md`](../aion/vision/README.md). Separate from `aion.visualization` (plots).

---

## CLI commands

| Command | Module |
|---------|--------|
| `aion config` | `aion.user_config` |
| `aion agent` / `api` / `auth` | `aion.cli_extensions` |
| `aion universe` / `aion universe-dashboard` | `aion.universe.cli` / `aion.universe.launch` |
| `aion physics` / `aion physics-dashboard` | `aion.physics.cli` / `aion.physics.launch` |
| `aion vision` | `aion.vision.cli` |
| `aion db` | `aion.db.cli` |
| `aion start` | `aion.hub` |
| `aion welcome` | `aion.install_splash` |
| `python -m aion` | `aion.cli` |

---

## Hygiene checklist

- [ ] No `aion/agent/` or `aion/code/` directories (only `code.py` module)
- [ ] No API keys in git — use `~/.aion.yaml` or `.env`
- [ ] `__pycache__/` not committed (in `.gitignore`)
- [ ] Docs match shipping surface (workspace agent is inspection-only)
