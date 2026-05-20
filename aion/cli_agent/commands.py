"""In-session slash commands for the agent loop."""

from __future__ import annotations

import os
from typing import Literal, Optional

from ..providers.errors import ProviderError
from ..providers.ollama import OllamaProvider
from . import ui
from .connect import AgentConnector
from .connect_args import parse_disconnect_args
from .constants import AGENT_MODES, mode_key
from .session_prefs import saved_provider
from .trust import ensure_trust_for_coding

SlashResult = Literal["continue", "quit"]


def handle_slash(
    cmd: str,
    args: str,
    *,
    connector: AgentConnector,
) -> SlashResult:
    session = connector.session
    agent = connector.agent

    if cmd in ("quit", "exit"):
        print(f"  {ui.ICON_EXIT} {ui.bold('Goodbye!')}")
        return "quit"

    if cmd == "reset":
        if agent:
            agent.reset()
            ui.success_print("Conversation memory cleared.")
        else:
            ui.info_print("Not connected — nothing to reset.")
        return "continue"

    if cmd == "status":
        ui.print_status_bar(session)
        if session.connected:
            ui.info_print(f"Working directory: {ui.cyan(os.getcwd())}")
        return "continue"

    if cmd == "model":
        if session.provider != "ollama":
            ui.info_print("/model is for Ollama. Use /mode to change provider.")
            return "continue"
        if not args:
            try:
                models = OllamaProvider.list_models()
            except ProviderError as e:
                ui.provider_error_print(e)
                return "continue"
            ui.print_menu(models, "Select Ollama Model")
            args = models[ui.get_menu_choice(models) - 1]
        if not ensure_trust_for_coding(connector):
            return "continue"
        connector.connect(prov="ollama", mod=args)
        return "continue"

    if cmd == "mode":
        ui.print_menu(AGENT_MODES, "Change Agent Mode")
        choice = ui.get_menu_choice(AGENT_MODES)
        new_mode = mode_key(choice)
        session.mode = new_mode
        if new_mode == "help":
            ui.print_help_catalog()
            ui.print_agent_commands()
            return "continue"
        if new_mode == "offline":
            connector.disconnect()
            ui.success_print("Offline mode.")
        elif new_mode == "cloud":
            if not ensure_trust_for_coding(connector):
                return "continue"
            prov = saved_provider(connector.cfg) or "openai"
            connector.connect(prov=prov, quiet=bool(saved_provider(connector.cfg)))
        elif new_mode == "ollama":
            if not ensure_trust_for_coding(connector):
                return "continue"
            connector.connect(prov="ollama", quiet=bool(saved_provider(connector.cfg)))
        ui.print_status_bar(session)
        return "continue"

    if cmd in ("disconnect", "offline", "logout"):
        req = parse_disconnect_args(
            args,
            connected=session.connected,
            active_provider=session.provider,
            active_model=session.model,
        )
        was = session.provider
        if req.keys_only and req.provider:
            connector.disconnect(forget_saved=False, clear_keys_for=req.provider)
            ui.success_print(f"Removed saved API key for {ui.bold(req.provider)}.")
        else:
            connector.disconnect(
                forget_saved=req.forget_saved,
                clear_keys_for=req.provider if req.clear_keys else None,
            )
            if was or req.provider:
                label = req.provider or was
                ui.success_print(f"Disconnected from {ui.bold(label)}.")
            else:
                ui.success_print("Offline.")
        ui.print_status_bar(session)
        return "continue"

    if cmd == "help":
        ui.print_agent_commands()
        return "continue"

    ui.error_print(f"Unknown command {ui.bold('/' + cmd)}. Try {ui.cyan('/help')}.")
    return "continue"
