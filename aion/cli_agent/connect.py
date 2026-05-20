"""Connect the ReAct agent to cloud or Ollama providers."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from ..agents.memory import SlidingWindowMemory
from ..agents.react import ReActAgent
from ..providers.errors import ProviderError
from ..providers.factory import create_provider
from ..providers.gemini_provider import GeminiProvider
from ..providers.keys import resolve_api_key
from ..providers.ollama import OllamaProvider
from ..tools.registry import ToolRegistry
from . import ui
from .config import save_config
from .session_prefs import (
    clear_connection,
    clear_provider_keys,
    save_connection,
    save_provider_key,
    saved_model,
    saved_provider,
)
from .constants import (
    CLOUD_PROVIDERS,
    CODING_AGENT_PROMPT,
    COMING_SOON_PROVIDERS,
    DEFAULT_MODELS,
    NATIVE_TOOL_PROVIDERS,
    provider_id_from_menu_label,
)


def _probe_ollama_tools(provider: Any, tools_schema: List[Dict[str, Any]]) -> bool:
    """Return True if this Ollama model accepts OpenAI-style tools."""
    if not tools_schema:
        return False
    try:
        provider.complete_turn(
            [{"role": "user", "content": "Say hi in one word."}],
            tools=tools_schema[:1],
            max_tokens=32,
            temperature=0,
        )
        return True
    except Exception:
        return False


class AgentConnector:
    """Create and hold a connected :class:`ReActAgent`."""

    def __init__(
        self,
        *,
        cfg: Dict[str, Any],
        registry: ToolRegistry,
        tools_schema: List[Dict[str, Any]],
        session: ui.AgentSession,
        is_trusted: bool,
        system_prompt: Optional[str] = None,
        workspace_root: Optional[str] = None,
    ) -> None:
        self.cfg = cfg
        self.registry = registry
        self.tools_schema = tools_schema
        self.session = session
        self.is_trusted = is_trusted
        self.system_prompt = system_prompt
        self.workspace_root = workspace_root or os.getcwd()
        self.agent: Optional[ReActAgent] = None
        self.trust_confirmed = False

    def apply_trust(self, is_trusted: bool) -> None:
        """Rebuild tool registry after the user answers the trust prompt."""
        from .tools import build_tool_registry, tools_schema

        self.is_trusted = is_trusted
        self.session.is_trusted = is_trusted
        self.registry = build_tool_registry(
            workspace_root=self.workspace_root,
            is_trusted=is_trusted,
        )
        self.tools_schema = tools_schema(is_trusted=is_trusted)
        self.agent = None

    def connect(
        self,
        prov: Optional[str] = None,
        mod: Optional[str] = None,
        *,
        quiet: bool = False,
        new_key: bool = False,
    ) -> bool:
        p_name = prov or self.session.provider or saved_provider(self.cfg)
        if not p_name and not quiet:
            ui.print_menu(CLOUD_PROVIDERS, "Select AI Provider")
            choice = ui.get_menu_choice(CLOUD_PROVIDERS)
            p_name = provider_id_from_menu_label(CLOUD_PROVIDERS[choice - 1])
        elif not p_name:
            return False

        if p_name in COMING_SOON_PROVIDERS:
            if not quiet:
                ui.info_print(
                    f"{ui.bold('Aqwel AI')} is coming soon — hosted models and billing "
                    f"from Aqwel AI. Use {ui.cyan('/connect openai')}, "
                    f"{ui.cyan('/connect ollama')}, or another provider for now."
                )
            return False

        api_key = None
        if p_name != "ollama":
            if new_key:
                self.disconnect(forget_saved=False)
                clear_provider_keys(self.cfg, p_name)
                ui.info_print(
                    f"Enter a new API key for {ui.bold(p_name)} "
                    f"(saved to {ui.cyan('~/.aion.yaml')})."
                )
                try:
                    api_key = ui.prompt_text("Enter API Key")
                except KeyboardInterrupt:
                    return False
                if not api_key:
                    ui.error_print("API key is required.")
                    return False
                save_provider_key(self.cfg, p_name, api_key)
            else:
                api_key = resolve_api_key(p_name, self.cfg)
                if not api_key:
                    if quiet:
                        return False
                    hint = "GEMINI_API_KEY or GOOGLE_API_KEY" if p_name in (
                        "gemini",
                        "google",
                    ) else f"{p_name.upper()}_API_KEY"
                    ui.info_print(
                        f"No API key found for {ui.bold(p_name)} "
                        f"(set {ui.cyan(hint)} or {ui.cyan('/connect ' + p_name + ' new')})."
                    )
                    try:
                        api_key = ui.prompt_text("Enter API Key")
                    except KeyboardInterrupt:
                        return False
                    if not api_key:
                        ui.error_print("API key is required.")
                        return False
                    save_provider_key(self.cfg, p_name, api_key)

        saved_prov = saved_provider(self.cfg)
        saved_mod = saved_model(self.cfg)
        if mod:
            m_name = mod
        elif self.session.provider == p_name and self.session.model:
            m_name = self.session.model
        elif saved_prov == p_name and saved_mod:
            m_name = saved_mod
        else:
            m_name = None
        # Only show pick-a-model menus on first setup (no saved model, not quiet).
        pick_model = not quiet and mod is None and not (
            saved_prov == p_name and saved_mod
        )

        if p_name == "ollama":
            try:
                ollama_models = OllamaProvider.list_models()
            except ProviderError as e:
                ui.provider_error_print(e)
                return False
            if not ollama_models:
                ui.error_print("No Ollama models found. Install one: ollama pull llama3")
                return False
            if mod:
                if mod not in ollama_models:
                    ui.error_print(
                        f"Model {ui.bold(mod)} not installed. "
                        f"Run: {ui.cyan('ollama pull ' + mod)}"
                    )
                    return False
                m_name = mod
            elif quiet:
                if (
                    saved_prov == "ollama"
                    and saved_mod
                    and saved_mod in ollama_models
                ):
                    m_name = saved_mod
                elif m_name and m_name in ollama_models:
                    pass
                else:
                    m_name = ollama_models[0]
            else:
                ui.print_menu(
                    ollama_models,
                    f"Select Ollama model ({len(ollama_models)} installed)",
                )
                m_name = ollama_models[ui.get_menu_choice(ollama_models) - 1]
        elif p_name in ("gemini", "google"):
            p_name = "gemini"
            if not m_name:
                m_name = DEFAULT_MODELS.get("gemini", "gemini-2.0-flash")
            if pick_model:
                try:
                    available = GeminiProvider.list_models(api_key)
                except ProviderError as e:
                    if e.status == 429:
                        ui.info_print(
                            "Gemini rate limited — using default model "
                            f"({ui.bold(m_name)}) without listing."
                        )
                        available = [m_name]
                    else:
                        ui.provider_error_print(e)
                        return False
                if m_name not in available:
                    ui.info_print(
                        f"Model {ui.bold(m_name)} not available; pick another."
                    )
                    m_name = None
                if not m_name:
                    choices = available[:12]
                    ui.print_menu(choices, "Select Gemini Model")
                    m_name = choices[ui.get_menu_choice(choices) - 1]
        elif not m_name:
            m_name = DEFAULT_MODELS.get(p_name, "default-model")

        try:
            provider = create_provider(p_name, api_key=api_key, model=m_name)
            from ..usage.tracking import wrap_provider_with_usage

            provider = wrap_provider_with_usage(
                provider,
                provider_name=p_name,
                model=m_name,
                source="agent",
            )

            if p_name in ("gemini", "google", "anthropic", "claude"):
                provider.supports_tools = False  # type: ignore[attr-defined]
            elif p_name == "ollama" and not quiet:
                if _probe_ollama_tools(provider, self.tools_schema):
                    provider.supports_tools = True  # type: ignore[attr-defined]
                else:
                    provider.supports_tools = False  # type: ignore[attr-defined]
            elif p_name == "ollama":
                provider.supports_tools = False  # type: ignore[attr-defined]
            elif p_name in NATIVE_TOOL_PROVIDERS:
                provider.supports_tools = True  # type: ignore[attr-defined]

            base_prompt = self.cfg.get("agent", {}).get("system_prompt") or CODING_AGENT_PROMPT
            if self.is_trusted:
                base_prompt += (
                    f"\n\nWorkspace: {self.workspace_root}\n"
                    "Trust: ON — you may edit files, write files, and run shell commands."
                )
            else:
                base_prompt += (
                    f"\n\nWorkspace: {self.workspace_root}\n"
                    "Trust: OFF — read-only; do not attempt write_file, edit_file, or run_command."
                )

            prompt = self.system_prompt or base_prompt
            self.agent = ReActAgent(
                provider=provider,
                registry=self.registry,
                tools=self.tools_schema,
                system_prompt=prompt,
                memory=SlidingWindowMemory(window_size=40, system_prompt=prompt),
                max_steps=20,
                on_step=self._on_tool_step,
            )
            self._apply_session(p_name, m_name, provider)
            save_connection(self.cfg, provider=p_name, model=m_name)
            if not quiet:
                ui.success_print(
                    f"Connected to {ui.bold(p_name)} · {ui.accent_muted(m_name)}. "
                    f"You can start chatting now."
                )
                ui.info_print(
                    f"Saved for next startup. {ui.dim('Use /disconnect to go offline.')}"
                )
            return True
        except ProviderError as e:
            ui.provider_error_print(e)
            return False
        except Exception as e:
            ui.error_print(f"Failed to connect: {e}")
            return False

    def disconnect(
        self,
        *,
        forget_saved: bool = False,
        clear_keys_for: Optional[str] = None,
    ) -> None:
        """End the current AI session; optionally clear saved provider or API keys."""
        self.agent = None
        self.session.connected = False
        self.session.provider = None
        self.session.model = None
        self.session.tools_enabled = False
        self.session.mode = "offline"
        if forget_saved:
            clear_connection(self.cfg)
        if clear_keys_for:
            clear_provider_keys(self.cfg, clear_keys_for)

    def _on_tool_step(self, step: int, action: str, result: str) -> None:
        preview = result.split("\n", 1)[0]
        if len(preview) > 120:
            preview = preview[:117] + "…"
        ui.tool_print(action, preview)

    def _apply_session(self, provider: str, model: str, backend: Any) -> None:
        self.session.connected = True
        self.session.provider = provider
        self.session.model = model
        self.session.mode = "ollama" if provider == "ollama" else "cloud"
        self.session.tools_enabled = bool(self.tools_schema)
