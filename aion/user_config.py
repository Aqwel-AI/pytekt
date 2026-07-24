"""Shared user config at ``~/.aion.yaml`` (no agent UI dependency)."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .config.core import get_nested, load_first_existing, save_yaml_file, set_nested

CONFIG_PATH = os.path.expanduser("~/.aion.yaml")


def get_config() -> Dict[str, Any]:
    cfg, _ = load_first_existing([CONFIG_PATH])
    return cfg


def save_config(cfg: Dict[str, Any]) -> None:
    save_yaml_file(CONFIG_PATH, cfg)


def config_command(key: Optional[str] = None, value: Optional[str] = None) -> None:
    """``aion config`` — show, get, or set dotted keys."""
    cfg = get_config()

    if key is None:
        if not cfg:
            print(f"No config at {CONFIG_PATH}. Set keys with: aion config <key> <value>")
            return
        print(f"Config file: {CONFIG_PATH}")
        for section, data in sorted(cfg.items()):
            if isinstance(data, dict):
                print(f"\n  {section}")
                for k, v in sorted(data.items()):
                    if k.endswith("_api_key") or "token" in k.lower() or "secret" in k.lower():
                        v = "********"
                    print(f"    {k} = {v}")
            else:
                print(f"  {section} = {data}")
        return

    if value is None:
        val = get_nested(cfg, key)
        if val is None:
            print(f"{key} is not set.")
        else:
            print(f"  {key} = {val}")
        return

    set_nested(cfg, key, value)
    save_config(cfg)
    print(f"Set {key} = {value}")
