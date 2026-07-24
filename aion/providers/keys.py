"""Resolve API keys from environment and config (with provider aliases)."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# Config keys checked in order (first match wins).
_CONFIG_KEY_ALIASES: Dict[str, List[str]] = {
    "gemini": ["gemini_api_key", "google_api_key"],
    "google": ["google_api_key", "gemini_api_key"],
    "openai": ["openai_api_key"],
    "deepseek": ["deepseek_api_key"],
    "nvidia": ["nvidia_api_key"],
    "nim": ["nvidia_api_key"],
    "anthropic": ["anthropic_api_key"],
    "claude": ["anthropic_api_key", "claude_api_key"],
}

# Environment variables checked in order.
_ENV_KEY_ALIASES: Dict[str, List[str]] = {
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "openai": ["OPENAI_API_KEY"],
    "deepseek": ["DEEPSEEK_API_KEY"],
    "nvidia": ["NVIDIA_API_KEY"],
    "nim": ["NVIDIA_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "claude": ["ANTHROPIC_API_KEY"],
}


def resolve_api_key(provider: str, cfg: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Return an API key for *provider* from env vars or ``~/.aion.yaml`` keys.

    Supports aliases (e.g. Gemini accepts ``GEMINI_API_KEY``, ``GOOGLE_API_KEY``,
    and config keys ``gemini_api_key`` / ``google_api_key``).
    """
    name = provider.lower().strip()
    for env_name in _ENV_KEY_ALIASES.get(name, [f"{name.upper()}_API_KEY"]):
        value = os.environ.get(env_name)
        if value and value.strip():
            return value.strip()

    keys = (cfg or {}).get("keys") or {}
    for cfg_name in _CONFIG_KEY_ALIASES.get(name, [f"{name}_api_key"]):
        value = keys.get(cfg_name)
        if value and str(value).strip():
            return str(value).strip()
    return None


def config_key_names(provider: str) -> List[str]:
    """Config file keys used for this provider's API token."""
    name = provider.lower().strip()
    return list(_CONFIG_KEY_ALIASES.get(name, [f"{name}_api_key"]))
