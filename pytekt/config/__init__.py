"""
Load and merge application configuration from TOML/YAML files and environment.

Install optional parsers: ``pip install pytekt[config]`` (tomli on Python
<3.11, PyYAML). See ``aion/config/README.md`` and the ``examples/`` notebooks.

Quick start
-----------
>>> from pathlib import Path
>>> from pytekt.config import load_config, get_nested, deep_merge
>>> # cfg = load_config(Path("config.toml"))
>>> # host = get_nested(cfg, "db.host", "localhost")
"""

from __future__ import annotations

from .core import (
    coerce_string_scalar,
    coerce_string_values,
    config_as_dict,
    deep_merge,
    get_nested,
    load_config,
    load_config_typed,
    load_first_existing,
    load_layered,
    load_toml_file,
    load_yaml_file,
    merge_env_overrides,
    pick_subset,
    require_keys,
    save_yaml_file,
    set_nested,
)

__all__ = [
    "coerce_string_scalar",
    "coerce_string_values",
    "config_as_dict",
    "deep_merge",
    "get_nested",
    "load_config",
    "load_config_typed",
    "load_first_existing",
    "load_layered",
    "load_toml_file",
    "load_yaml_file",
    "merge_env_overrides",
    "pick_subset",
    "require_keys",
    "save_yaml_file",
    "set_nested",
]
