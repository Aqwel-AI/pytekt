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


def saved_interaction_mode(cfg: Dict[str, Any]) -> str:
    from .constants import DEFAULT_INTERACTION_MODE, normalize_interaction_mode

    value = (cfg.get("agent") or {}).get("interaction_mode")
    if value:
        normalized = normalize_interaction_mode(str(value))
        if normalized:
            return normalized
    return DEFAULT_INTERACTION_MODE


def save_interaction_mode(cfg: Dict[str, Any], mode: str) -> None:
    from .constants import normalize_interaction_mode

    normalized = normalize_interaction_mode(mode)
    if not normalized:
        raise ValueError(f"Unknown interaction mode: {mode!r}")
    cfg.setdefault("agent", {})["interaction_mode"] = normalized
    save_config(cfg)


def save_provider_key(cfg: Dict[str, Any], provider: str, api_key: str) -> None:
    """Persist an API key under all config aliases for this provider."""
    from ..providers.keys import config_key_names

    keys = cfg.setdefault("keys", {})
    for name in config_key_names(provider):
        keys[name] = api_key
    save_config(cfg)


def saved_pinned_paths(cfg: Dict[str, Any]) -> list:
    paths = (cfg.get("agent") or {}).get("pinned_paths") or []
    return [str(p) for p in paths if p]


def save_pinned_paths(cfg: Dict[str, Any], paths: list) -> None:
    cfg.setdefault("agent", {})["pinned_paths"] = list(paths)
    save_config(cfg)


def saved_workspace_roots(cfg: Dict[str, Any]) -> list:
    roots = (cfg.get("agent") or {}).get("workspace_roots") or []
    return [str(r) for r in roots if r]


def save_workspace_roots(cfg: Dict[str, Any], roots: list) -> None:
    cfg.setdefault("agent", {})["workspace_roots"] = list(roots)
    save_config(cfg)


def approval_gate_enabled(cfg: Dict[str, Any]) -> bool:
    return bool((cfg.get("agent") or {}).get("approval_gate"))


def saved_allowed_commands(cfg: Dict[str, Any]) -> list:
    cmds = (cfg.get("agent") or {}).get("allowed_commands") or []
    return [str(c) for c in cmds if c]


def force_tools_enabled(cfg: Dict[str, Any]) -> bool:
    return bool((cfg.get("agent") or {}).get("force_tools"))


def saved_safety_mode(cfg: Dict[str, Any]) -> str:
    from .constants import normalize_safety_mode

    value = (cfg.get("agent") or {}).get("safety_mode", "workspace-write")
    normalized = normalize_safety_mode(str(value))
    return normalized or "workspace-write"


def save_safety_mode(cfg: Dict[str, Any], mode: str) -> None:
    from .constants import normalize_safety_mode

    normalized = normalize_safety_mode(mode)
    if not normalized:
        raise ValueError(f"Unknown safety mode: {mode!r}")
    cfg.setdefault("agent", {})["safety_mode"] = normalized
    save_config(cfg)


def saved_specialist_mode(cfg: Dict[str, Any]) -> str:
    from .constants import normalize_specialist_mode

    value = (cfg.get("agent") or {}).get("specialist_mode", "general")
    normalized = normalize_specialist_mode(str(value))
    return normalized or "general"


def save_specialist_mode(cfg: Dict[str, Any], mode: str) -> None:
    from .constants import normalize_specialist_mode

    normalized = normalize_specialist_mode(mode)
    if not normalized:
        raise ValueError(f"Unknown specialist mode: {mode!r}")
    cfg.setdefault("agent", {})["specialist_mode"] = normalized
    save_config(cfg)


def saved_mcp_servers(cfg: Dict[str, Any]) -> list:
    servers = (cfg.get("agent") or {}).get("mcp_servers") or []
    return list(servers) if isinstance(servers, list) else []


def save_mcp_servers(cfg: Dict[str, Any], servers: list) -> None:
    cfg.setdefault("agent", {})["mcp_servers"] = list(servers)
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
