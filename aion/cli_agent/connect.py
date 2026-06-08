"""Connect the ReAct agent to Ollama."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from ..agents.memory import SlidingWindowMemory
from ..agents.react import ReActAgent
from ..providers.errors import ProviderError
from ..providers.factory import create_provider
from ..providers.ollama import OllamaProvider
from ..tools.registry import ToolRegistry
from . import ui
from .connect_args import looks_like_model_name, normalize_company
from .constants import (
    AGENT_PROVIDER,
    CODING_AGENT_PROMPT,
    COMING_SOON_PROVIDERS,
    provider_display_name,
)
from .session_prefs import clear_connection, save_connection, saved_model, saved_provider


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


def _resolve_ollama_target(
    prov: Optional[str],
    mod: Optional[str],
) -> tuple[Optional[str], Optional[str], bool]:
    """
    Normalize connect args to Ollama.

    Returns (provider, model, rejected) where rejected means a non-Ollama provider was requested.
    """
    p_name = (prov or "").lower().strip()
    if not p_name:
        return AGENT_PROVIDER, mod, False
    mapped = normalize_company(p_name) or p_name
    if mapped == AGENT_PROVIDER:
        return AGENT_PROVIDER, mod, False
    if looks_like_model_name(p_name):
        return AGENT_PROVIDER, mod or p_name, False
    if mapped in COMING_SOON_PROVIDERS or mapped != AGENT_PROVIDER:
        return mapped, mod, True
    return mapped, mod, True


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
        new_key: bool = False,  # noqa: ARG002 — kept for slash-command compatibility
    ) -> bool:
        raw = prov or self.session.provider or saved_provider(self.cfg)
        p_name, m_name, rejected = _resolve_ollama_target(raw, mod)
        if rejected:
            if not quiet:
                label = provider_display_name(p_name)
                ui.info_print(
                    f"{ui.bold(label)} is coming soon — not available yet. "
                    f"Use {ui.cyan('/connect')} or {ui.cyan('/connect ollama')} for now."
                )
            return False

        saved_prov = saved_provider(self.cfg)
        saved_mod = saved_model(self.cfg)
        if m_name:
            pass
        elif self.session.provider == AGENT_PROVIDER and self.session.model:
            m_name = self.session.model
        elif saved_prov == AGENT_PROVIDER and saved_mod:
            m_name = saved_mod
        else:
            m_name = None

        pick_model = not quiet and mod is None and not (
            saved_prov == AGENT_PROVIDER and saved_mod
        )

        try:
            ollama_models = OllamaProvider.list_models()
        except ProviderError as e:
            ui.provider_error_print(e)
            return False
        if not ollama_models:
            ui.error_print("No Ollama models found. Install one: ollama pull llama3")
            return False

        if m_name and m_name not in ollama_models:
            if mod or (prov and looks_like_model_name(prov)):
                ui.error_print(
                    f"Model {ui.bold(m_name)} not installed. "
                    f"Run: {ui.cyan('ollama pull ' + m_name)}"
                )
                return False
            m_name = None

        if quiet:
            if m_name and m_name in ollama_models:
                pass
            elif saved_prov == AGENT_PROVIDER and saved_mod and saved_mod in ollama_models:
                m_name = saved_mod
            else:
                m_name = ollama_models[0]
        elif pick_model or not m_name:
            ui.print_menu(
                ollama_models,
                f"Select Ollama model ({len(ollama_models)} installed)",
            )
            m_name = ollama_models[ui.get_menu_choice(ollama_models) - 1]

        try:
            provider = create_provider(AGENT_PROVIDER, model=m_name)
            from ..usage.tracking import wrap_provider_with_usage

            provider = wrap_provider_with_usage(
                provider,
                provider_name=AGENT_PROVIDER,
                model=m_name,
                source="agent",
            )

            if not quiet:
                if _probe_ollama_tools(provider, self.tools_schema):
                    provider.supports_tools = True  # type: ignore[attr-defined]
                else:
                    provider.supports_tools = False  # type: ignore[attr-defined]
            else:
                provider.supports_tools = False  # type: ignore[attr-defined]

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
            self._apply_session(m_name, provider)
            save_connection(self.cfg, provider=AGENT_PROVIDER, model=m_name)
            if not quiet:
                ui.success_print(
                    f"Connected to {ui.bold('Ollama')} · {ui.accent_muted(m_name)}. "
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
        clear_keys_for: Optional[str] = None,  # noqa: ARG002 — legacy slash args
    ) -> None:
        """End the current AI session; optionally clear saved provider."""
        self.agent = None
        self.session.connected = False
        self.session.provider = None
        self.session.model = None
        self.session.tools_enabled = False
        self.session.mode = "offline"
        if forget_saved:
            clear_connection(self.cfg)

    def _on_tool_step(self, step: int, action: str, result: str) -> None:
        preview = result.split("\n", 1)[0]
        if len(preview) > 120:
            preview = preview[:117] + "…"
        ui.tool_print(action, preview)

    def _apply_session(self, model: str, backend: Any) -> None:
        self.session.connected = True
        self.session.provider = AGENT_PROVIDER
        self.session.model = model
        self.session.mode = "ollama"
        self.session.tools_enabled = bool(self.tools_schema)
