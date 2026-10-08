"""
Interactive & CLI API Connection Engine for PyTekt Agent.
Handles API key input, real ping verification, and persistent configuration.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import getpass
import os
import sys
from typing import Any, Dict, Optional, Tuple

from ..providers.factory import create_provider, supported_providers
from ..user_config import get_config, save_config


def test_provider_connection(
    provider_name: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Test real API connectivity with a minimal test message.
    """
    p_name = provider_name.lower().strip()
    kwargs: Dict[str, Any] = {}
    if api_key:
        kwargs["api_key"] = api_key
    if model:
        kwargs["model"] = model
    if base_url:
        kwargs["base_url"] = base_url

    try:
        prov = create_provider(p_name, **kwargs)
        # Test quick turn
        reply = prov.chat([{"role": "user", "content": "ping"}], max_tokens=5, temperature=0.0)
        return True, "Connection successful!"
    except Exception as e:
        return False, str(e)


def save_provider_connection(
    provider_name: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Persist provider preferences and credentials to ~/.pytekt.yaml.
    """
    cfg = get_config()
    p_name = provider_name.lower().strip()
    
    agent_cfg = cfg.setdefault("agent", {})
    agent_cfg["provider"] = p_name
    if model:
        agent_cfg["model"] = model
    if base_url:
        agent_cfg["custom_base_url"] = base_url

    if api_key:
        keys_cfg = cfg.setdefault("keys", {})
        keys_cfg[f"{p_name}_api_key"] = api_key
        # Also handle aliases
        if p_name in ("gemini", "google"):
            keys_cfg["gemini_api_key"] = api_key
            keys_cfg["google_api_key"] = api_key
        elif p_name in ("anthropic", "claude"):
            keys_cfg["anthropic_api_key"] = api_key
            keys_cfg["claude_api_key"] = api_key

    save_config(cfg)
    return cfg


def run_connect_interactive(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> int:
    """
    Interactive CLI wizard to connect AI providers.
    """
    print()
    print("  \033[1;37mPyTekt Agent — Provider Connection Wizard\033[0m")
    print("  ─────────────────────────────────────────────")

    available = [
        ("openai", "OpenAI (GPT-4o, GPT-4o-mini, o3-mini)"),
        ("anthropic", "Anthropic Claude (Claude 3.5 Sonnet, Claude 3.5 Haiku)"),
        ("gemini", "Google Gemini (Gemini 2.0 Flash, Gemini 1.5 Pro)"),
        ("deepseek", "DeepSeek (DeepSeek V3, DeepSeek R1)"),
        ("ollama", "Ollama Local (llama3.2, mistral)"),
        ("nvidia", "NVIDIA NIM (LLaMA 3.3 70B, Nemotron)"),
        ("openai_compatible", "Custom OpenAI Compatible Endpoint"),
    ]

    selected_provider = provider
    if not selected_provider:
        print("\n  Available Providers:")
        for idx, (p_id, desc) in enumerate(available, 1):
            print(f"    \033[36m{idx}\033[0m) {desc}")
        try:
            choice = input("\n  Select provider [1-7]: ").strip()
            if not choice:
                print("  Cancelled.")
                return 1
            idx_int = int(choice) - 1
            selected_provider = available[idx_int][0]
        except (ValueError, IndexError):
            print("  \033[31mInvalid choice.\033[0m")
            return 1

    selected_provider = selected_provider.lower().strip()
    
    # Base URL for custom
    base_url = None
    if selected_provider == "openai_compatible":
        base_url = input("  Enter Base URL (e.g. http://localhost:1234/v1): ").strip()
    elif selected_provider == "ollama":
        base_url = input("  Enter Ollama Host (default http://localhost:11434): ").strip() or "http://localhost:11434"

    # API key prompt
    entered_key = api_key
    if selected_provider not in ("ollama",) and not entered_key:
        cfg = get_config()
        existing_key = (cfg.get("keys") or {}).get(f"{selected_provider}_api_key")
        prompt_txt = f"  Enter API Key for {selected_provider}"
        if existing_key:
            prompt_txt += " [press Enter to keep existing]"
        prompt_txt += ": "
        
        try:
            val = getpass.getpass(prompt_txt)
            entered_key = val.strip() or existing_key
        except Exception:
            val = input(prompt_txt)
            entered_key = val.strip() or existing_key

    # Model prompt
    selected_model = model
    if not selected_model:
        default_model = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-latest",
            "gemini": "gemini-2.0-flash",
            "deepseek": "deepseek-chat",
            "ollama": "llama3.2",
            "nvidia": "meta/llama-3.1-8b-instruct",
            "openai_compatible": "default",
        }.get(selected_provider, "default")
        
        model_input = input(f"  Enter Model name [default: {default_model}]: ").strip()
        selected_model = model_input or default_model

    # Verify connection
    print(f"\n  Testing connection to \033[33m{selected_provider}\033[0m ({selected_model})...", end="", flush=True)
    success, msg = test_provider_connection(
        provider_name=selected_provider,
        api_key=entered_key,
        model=selected_model,
        base_url=base_url,
    )
    if success:
        print(" \033[32m[OK] Verified!\033[0m")
        save_provider_connection(
            provider_name=selected_provider,
            api_key=entered_key,
            model=selected_model,
            base_url=base_url,
        )
        print("  \033[32mSaved credentials to ~/.pytekt.yaml\033[0m")
        print(f"  PyTekt Agent is now configured to use \033[1;37m{selected_provider} / {selected_model}\033[0m.\n")
        return 0
    else:
        print(" \033[31m[ERR] Failed!\033[0m")
        print(f"  \033[31mError:\033[0m {msg}\n")
        save_anyway = input("  Save configuration anyway? [y/N]: ").strip().lower()
        if save_anyway == "y":
            save_provider_connection(
                provider_name=selected_provider,
                api_key=entered_key,
                model=selected_model,
                base_url=base_url,
            )
            print("  Saved to ~/.pytekt.yaml.")
            return 0
        return 1
