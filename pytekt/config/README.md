# `pytekt.config`

Small, dependency-light helpers to load **TOML** and **YAML**, merge **`PYTEKT_*` environment** overrides, and combine **layered** config files.

## Install

```bash
pip install pytekt[config]
```

- **Python 3.11+:** TOML via `tomllib` (stdlib).
- **Python &lt; 3.11:** `tomli` (pulled in by the `[config]` extra).
- **YAML:** `PyYAML` (same extra).

## Examples

- **Index:** [`examples/README.md`](examples/README.md)
- **Notebook:** [`examples/01_config_loading_merge.ipynb`](examples/01_config_loading_merge.ipynb)
- **Sample files:** [`examples/sample.toml`](examples/sample.toml), [`examples/sample_override.yaml`](examples/sample_override.yaml)

Open the notebook from the repo root or after `pip install -e .` so `import pytekt.config` resolves.

## API overview

| Function | Purpose |
|----------|---------|
| `load_toml_file` / `load_yaml_file` | Load one file into a `dict`. |
| `load_config(path)` | Pick parser by extension; optional `merge_env=True`. |
| `load_config_typed` | Like `load_config`, then coerce string leaves (bools, ints, floats). |
| `merge_env_overrides` | Apply `PYTEKT_KEY` or `PYTEKT_section__key` env vars. |
| `deep_merge(base, override)` | Recursive dict merge; override wins. |
| `get_nested` / `set_nested` | Dotted paths (`"db.host"`). |
| `load_first_existing` | Try a list of paths; return `(cfg, path_or_none)`. |
| `load_layered` | Merge multiple existing files in order, then optional env. |
| `require_keys` | Raise `KeyError` if any dotted path is missing. |
| `pick_subset` | Flat dict of existing dotted keys. |
| `coerce_string_scalar` / `coerce_string_values` | Parse `"true"`, `"42"`, `"3.14"` from strings. |
| `save_yaml_file` | Write a dict as YAML (needs PyYAML). |
| `config_as_dict` | Deep copy for logging or safe mutation. |

## Environment naming

- Top-level: `PYTEKT_LOGLEVEL=debug` → `cfg["loglevel"] == "debug"` (keys lowercased after the prefix).
- Nested: `PYTEKT_DB__HOST=postgres` → `cfg["db"]["host"] == "postgres"`.

Values are **strings** until you call `coerce_string_values` or `load_config_typed`.

## Design notes

- No global singleton: load and merge in your app entrypoint.
- For secrets, prefer env vars or a secrets manager; do not commit real keys in repo configs.
