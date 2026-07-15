"""``aion api`` — API token and provider management."""

from __future__ import annotations

import os
from typing import Any

from . import ui
from .config import get_config, save_config
from .session_prefs import clear_provider_keys, save_provider_key


def api_add(name: str, token: str) -> None:
    cfg = get_config()
    save_provider_key(cfg, name, token)
    ui.success_print(f"Saved API key for {ui.bold(name)}.")


def api_connect_menu() -> None:
    companies = ["Nvidia", "OpenAI", "Anthropic", "Gemini", "DeepSeek"]
    ui.print_menu(companies, "Add API key (Ollama is local — no key needed)")
    choice = ui.get_menu_choice(companies)
    company = companies[choice - 1]
    token = input(f"  {ui.ICON_AUTH} Enter API Token for {ui.bold(company)}: ").strip()
    if not token:
        ui.error_print("Token is required.")
        return
    api_add(company.lower(), token)


def api_list() -> None:
    cfg = get_config()
    keys = cfg.get("keys", {})
    if not keys:
        ui.info_print(f"No connected APIs. Use {ui.cyan('aion api connect')} to add one.")
        return
    ui.info_print(f"{ui.bold('Connected Companies:')}")
    for k, v in keys.items():
        masked = "********" + str(v)[-4:] if len(str(v)) > 8 else "********"
        provider = k.replace("_api_key", "").capitalize()
        print(f"    {ui.green('●')} {ui.bold(provider):12} | {ui.dim(masked)}")


def api_remove(name: str) -> None:
    cfg = get_config()
    from ..providers.keys import config_key_names

    names = config_key_names(name)
    keys = cfg.get("keys") or {}
    if any(n in keys for n in names):
        clear_provider_keys(cfg, name)
        ui.success_print(f"Removed saved API key for {ui.bold(name)}.")
    else:
        ui.error_print(f"No saved API key for {ui.bold(name)}.")


def api_main(args: Any) -> None:
    action = getattr(args, "api_action", None)
    if action == "connect":
        if getattr(args, "name", None) and getattr(args, "token", None):
            api_add(args.name, args.token)
        else:
            api_connect_menu()
    elif action == "add":
        if not getattr(args, "name", None) or not getattr(args, "token", None):
            api_connect_menu()
        else:
            api_add(args.name, args.token)
    elif action == "list":
        api_list()
    elif action in ("remove", "disconnect"):
        if not getattr(args, "name", None):
            ui.error_print(f"Usage: aion api {action} <name>")
            return
        api_remove(args.name)
    else:
        api_list()
