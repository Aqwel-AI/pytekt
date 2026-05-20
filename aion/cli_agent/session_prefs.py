"""Persist agent provider, model, and workspace trust in ~/.aion.yaml."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .config import save_config


def saved_provider(cfg: Dict[str, Any]) -> Optional[str]:
    value = (cfg.get("agent") or {}).get("provider")
    return str(value).strip() if value else None


def saved_model(cfg: Dict[str, Any]) -> Optional[str]:
    value = (cfg.get("agent") or {}).get("model")
    return str(value).strip() if value else None


def saved_trust(cfg: Dict[str, Any]) -> bool:
    return bool((cfg.get("agent") or {}).get("trust"))


def idle_disconnect_minutes(cfg: Dict[str, Any]) -> int:
    """0 = never auto-disconnect while idle (default)."""
    value = (cfg.get("agent") or {}).get("idle_disconnect_minutes", 0)
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def save_idle_disconnect_minutes(cfg: Dict[str, Any], minutes: int) -> None:
    cfg.setdefault("agent", {})["idle_disconnect_minutes"] = max(0, int(minutes))
    save_config(cfg)


def save_connection(cfg: Dict[str, Any], *, provider: str, model: str) -> None:
    agent = cfg.setdefault("agent", {})
    agent["provider"] = provider
    agent["model"] = model
    save_config(cfg)


def save_trust(cfg: Dict[str, Any], *, trusted: bool) -> None:
    cfg.setdefault("agent", {})["trust"] = bool(trusted)
    save_config(cfg)


def clear_connection(cfg: Dict[str, Any]) -> None:
    agent = cfg.setdefault("agent", {})
    agent.pop("provider", None)
    agent.pop("model", None)
    save_config(cfg)


def save_provider_key(cfg: Dict[str, Any], provider: str, api_key: str) -> None:
    """Persist an API key under all config aliases for this provider."""
    from ..providers.keys import config_key_names

    keys = cfg.setdefault("keys", {})
    for name in config_key_names(provider):
        keys[name] = api_key
    save_config(cfg)


def clear_provider_keys(cfg: Dict[str, Any], provider: str) -> None:
    """Remove saved API keys from ~/.aion.yaml (environment variables are unchanged)."""
    from ..providers.keys import config_key_names

    keys = cfg.get("keys")
    if not keys:
        return
    for name in config_key_names(provider):
        keys.pop(name, None)
    if not keys:
        cfg.pop("keys", None)
    save_config(cfg)
