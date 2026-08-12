# pytekt.config — Example notebooks and sample files

This folder contains Jupyter notebooks and static config samples for **`pytekt.config`**: TOML/YAML loading, environment overlays, deep merge, and dotted key helpers.

## Install

Config examples need the optional **`[config]`** extra (PyYAML; on Python &lt; 3.11, `tomli` for TOML):

```bash
pip install -e ".[config]"
```

## Notebooks

| Notebook | Content |
|----------|---------|
| **01_config_loading_merge.ipynb** | Resolve paths next to the package, `load_toml_file` / layered YAML, `get_nested` / `set_nested`, `deep_merge`, `load_layered`, `merge_env_overrides` with `coerce_string_values`, `load_first_existing`, `require_keys`, `save_yaml_file`. |

## Sample files

| File | Role |
|------|------|
| **sample.toml** | Base app/db/llm settings used as the first layer in the notebook. |
| **sample_override.yaml** | Second layer: overrides `app.debug`, `db.host`, adds `logging` (merged on top of the TOML). |

## How to run

From the project root:

```bash
pip install -e ".[config]"
jupyter notebook aion/config/examples/
```

Or open **`01_config_loading_merge.ipynb`** in JupyterLab or VS Code. Cells assume `import pytekt.config` works (editable install or a normal install of `pytekt`).

More API detail: [`../README.md`](../README.md) (parent `pytekt.config` module readme).
