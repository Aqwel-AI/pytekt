# Aion project structure

> **Aqwel AI product** — see [README](../README.md#aion-product-documentation) and [aion/cli_agent/README.md](../aion/cli_agent/README.md).

Aion is **one repository, two products**:

| Pillar | Package path | CLI / import |
|--------|--------------|--------------|
| **Research library** | `aion/*` (except `cli_agent`) | `import aion` |
| **Terminal agent** | `aion/cli_agent/` | `aion agent` |

Shared: `aion.providers`, `aion.agents`, `aion.tools`.

---

## Repository root

```
.
├── README.md                 # Main documentation
├── SECURITY.md
├── .env.example
├── docs/
│   └── PROJECT_STRUCTURE.md  # This file
├── pyproject.toml
├── aion/                     # Python package
├── src/aion_core.cpp         # Optional native extension
└── tests/
```

**Private (never commit):** `.env`, `~/.aion.yaml`, checkpoints, `wandb/`, `.cursor/` — see [SECURITY.md](../SECURITY.md) and [.gitignore](../.gitignore).

---

## Terminal agent (`aion/cli_agent/`)

```
aion/cli_agent/
├── app.py              # Main loop, slash commands (/sky, /db, …)
├── universe_cmds.py    # /sky moon and whats_up
├── connect.py          # OpenAI, Gemini, Ollama, DeepSeek, …
├── connect_args.py     # /connect, /disconnect, /reconnect parsing
├── session_prefs.py    # Saved provider, model, trust, idle
├── config.py           # ~/.aion.yaml
├── tools.py            # Agent tool registry
├── api.py              # aion api
├── auth.py             # aion auth
├── trust.py
├── constants.py
├── commands.py
└── ui/                 # Dashboard, glitch intro, messages, help
```

**CLI entry shims** (backward compatible, thin re-exports):

| File | Delegates to |
|------|----------------|
| `aion/cli.py` | All subcommands via `main()` |
| `aion/agent_cli.py` | `cli_agent.run_agent_command` |
| `aion/api_cli.py` | `cli_agent.api_main` |
| `aion/auth_cli.py` | `cli_agent.auth_main` |
| `aion/agent_ui/` | `cli_agent.ui` |

**Do not add** an `aion/agent/` package — that path was removed; use `cli_agent` only.

---

## Research library (high level)

```
aion/
├── maths.py, algorithms/
├── preprocessing/, models/, metrics/, hyperopt/   # Core ML
├── data/, datasets/
├── providers/, tools/, rag/, agents/
├── former/, visualization/, ui/, hub/
├── tracker/, llm_eval/, db/, universe/, cache/, store/, pipeline/
├── experiments/, bench/, benchmarks/
├── io/, config/, env/, serve/, monitor/, vision/
└── cli.py
```

Install extras: `[ai]`, `[viz]`, `[rag]`, `[config]`, `[db]`, `[universe]`, `[full]`.

**`aion/universe/`** — coordinates, time, observing, orbits, cosmology, catalogs, C++ extension (`_aion_universe`), optional viz, React web dashboard (`web/` → `static/`). See [`aion/universe/README.md`](../aion/universe/README.md). `aion/cosmos` is a deprecated import shim.

---

## CLI commands

| Command | Module |
|---------|--------|
| `aion agent` | `aion.cli_agent.app` |
| `aion api` | `aion.cli_agent.api` |
| `aion config` | `aion.cli_agent.config` |
| `aion auth` | `aion.cli_agent.auth` |
| `aion universe` / `aion universe-dashboard` (`cosmos` aliases deprecated) | `aion.universe.cli` / `aion.universe.launch` |
| `aion db` | `aion.db.cli` |
| `aion start` | `aion.hub` |
| `python -m aion` | `aion.cli` |

---

## Hygiene checklist

- [ ] No `aion/agent/` or `aion/code/` directories (only `code.py` module)
- [ ] No API keys in git — use `~/.aion.yaml` or `.env`
- [ ] `__pycache__/` not committed (in `.gitignore`)
