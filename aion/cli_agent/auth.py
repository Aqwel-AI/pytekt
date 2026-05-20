"""``aion auth`` — account sign-in (placeholder) and session status."""

from __future__ import annotations

from typing import Any

from . import ui
from .config import get_config, save_config


def login_command(provider: str = "google") -> None:
    ui.print_header()
    ui.coming_soon_banner(f"{provider.capitalize()} Login")
    ui.info_print(f"Please use {ui.cyan('aion api connect')} to manage your API tokens for now.")


def logout_command() -> None:
    cfg = get_config()
    if "auth" in cfg:
        del cfg["auth"]
        save_config(cfg)
        ui.success_print("Logged out from all accounts.")
    else:
        ui.info_print("No active sessions found.")


def status_command() -> None:
    cfg = get_config()
    auth = cfg.get("auth", {})
    if not auth:
        ui.info_print(f"Not signed in. Use {ui.cyan('aion auth login')} to connect.")
        return
    ui.info_print(f"{ui.bold('Active Sessions:')}")
    for provider, data in auth.items():
        status = data.get("status", "unknown")
        email = data.get("email", "N/A")
        mark = ui.green("●") if status == "connected" else ui.red("○")
        print(f"    {mark} {ui.bold(provider.capitalize()):10} | {email}")


def auth_main(args: Any) -> None:
    if args.action == "login":
        login_command(args.provider or "google")
    elif args.action == "logout":
        logout_command()
    elif args.action == "status":
        status_command()
    else:
        status_command()
