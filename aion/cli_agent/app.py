"""Main interactive agent — Aion terminal shell."""

from __future__ import annotations

import os
import time
import uuid
from typing import Any, Optional

from ..providers.errors import ProviderError
from . import ui
from .config import get_config
from .connect import AgentConnector
from .connect_args import parse_connect_args, parse_disconnect_args
from .session_prefs import (
    idle_disconnect_minutes,
    save_idle_disconnect_minutes,
    saved_model,
    saved_provider,
    saved_trust,
)
from .tools import build_tool_registry, tools_schema
from .cosmos_cmds import handle_sky_command
from .db_cmds import handle_db_command
from .trust import ensure_trust_for_coding


def _handle_command(
    text: str,
    *,
    connector: AgentConnector,
    workspace: str,
    db_memory: Optional[Any] = None,
) -> Optional[str]:
    """Returns 'quit' to exit loop, None to continue."""
    if text == "?":
        ui.print_shortcuts()
        return None

    if not text.startswith("/"):
        return "chat"

    parts = text[1:].split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd in ("quit", "exit", "q"):
        return "quit"

    if cmd == "help":
        ui.print_slash_help()
        ui.print_shortcuts()
        return None

    if cmd == "idle":
        mins = idle_disconnect_minutes(connector.cfg)
        if not args or args.lower() in ("off", "0", "none", "never"):
            save_idle_disconnect_minutes(connector.cfg, 0)
            ui.success_print(
                "Idle auto-disconnect is off. "
                "Your connection stays after you restart the agent."
            )
        elif args.lower() in ("status", "?"):
            if mins:
                ui.info_print(f"Auto-disconnect after {ui.bold(str(mins))} minutes idle.")
            else:
                ui.info_print("Auto-disconnect is off (connection persists).")
        else:
            try:
                n = int(args.split()[0])
                save_idle_disconnect_minutes(connector.cfg, n)
                if n:
                    ui.success_print(
                        f"Will disconnect after {ui.bold(str(n))} minutes with no messages."
                    )
                else:
                    ui.success_print("Idle auto-disconnect is off.")
            except ValueError:
                ui.error_print("Usage: /idle 30  |  /idle off")
        return None

    if cmd in ("connect", "reconnect"):
        if not ensure_trust_for_coding(connector):
            return None
        if args:
            prov, mod, new_key = parse_connect_args(args)
        else:
            prov, mod, new_key = None, None, False
        if connector.connect(
            prov=prov,
            mod=mod,
            quiet=False,
            new_key=new_key,
        ):
            ui.print_aion_dashboard(
                cfg=connector.cfg,
                session=connector.session,
                version=_version(),
                workspace=workspace,
            )
            ui.print_input_area(connected=True)
        return None

    if cmd == "models":
        ui.print_aion_dashboard(
            cfg=connector.cfg,
            session=connector.session,
            version=_version(),
            workspace=workspace,
        )
        return None

    if cmd in ("disconnect", "offline", "logout"):
        req = parse_disconnect_args(
            args,
            connected=connector.session.connected,
            active_provider=connector.session.provider,
            active_model=connector.session.model,
        )
        was_prov = connector.session.provider
        was_model = connector.session.model

        if req.keys_only and req.provider:
            connector.disconnect(
                forget_saved=False,
                clear_keys_for=req.provider,
            )
            ui.success_print(
                f"Removed saved key for {ui.bold(req.label)}. "
                f"Still using {ui.bold(was_prov or '')}"
                + (f" · {ui.accent_muted(was_model)}" if was_model else "")
                + "."
            )
            ui.print_aion_dashboard(
                cfg=connector.cfg,
                session=connector.session,
                version=_version(),
                workspace=workspace,
            )
            ui.print_input_area(connected=True)
            return None

        clear_keys = req.clear_keys and bool(req.provider)
        connector.disconnect(
            forget_saved=req.forget_saved,
            clear_keys_for=req.provider if clear_keys else None,
        )

        target = req.label or was_prov or "session"
        if was_prov or req.provider:
            ui.success_print(
                f"Disconnected {ui.bold(target)}."
                + (
                    f" {ui.dim('Saved API key removed.')}"
                    if clear_keys
                    else f" {ui.dim('Use /connect to link again.')}"
                )
            )
        else:
            ui.success_print("Offline.")
        ui.print_aion_dashboard(
            cfg=connector.cfg,
            session=connector.session,
            version=_version(),
            workspace=workspace,
        )
        ui.print_input_area(connected=False)
        return None

    if cmd == "init":
        ui.success_print(ui.write_aion_md(workspace))
        return None

    if cmd == "usage":
        from ..usage.launch import ensure_usage_dashboard

        url, started = ensure_usage_dashboard(open_browser=True)
        if started:
            ui.success_print(f"Usage dashboard started at {ui.cyan(url)}")
        else:
            ui.info_print(f"Opened {ui.cyan(url)} (already running)")
        return None

    if cmd == "db":
        handle_db_command(args, cfg=connector.cfg, memory=db_memory)
        return None

    if cmd == "sky":
        handle_sky_command(args, cfg=connector.cfg)
        return None

    ui.print_slash_help(cmd)
    ui.error_print(f"Unknown command {ui.bold(text)}. See matches above.")
    return None


def _version() -> str:
    try:
        from .. import __version__
        return __version__
    except Exception:
        return "0.2.0"


def run_agent_command(
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> None:
    """Aion UI: animation → dashboard → prompt."""
    version = _version()
    ui.run_agent_intro(version=version)

    try:
        from .context_info import get_agent_context

        ctx = get_agent_context()
        ui.info_print(ui.dim(ctx["line"]))
    except Exception:
        pass

    workspace_root = os.getcwd()
    cfg = get_config()
    session = ui.AgentSession(mode="offline", is_trusted=False)

    from .constants import AGENT_PROVIDER, COMING_SOON_PROVIDERS, provider_display_name

    if provider_name:
        if provider_name in COMING_SOON_PROVIDERS:
            ui.info_print(
                f"{provider_display_name(provider_name)} is coming soon — not available yet. "
                f"Use {ui.cyan('/connect ollama')} for now."
            )
        elif provider_name != AGENT_PROVIDER:
            ui.info_print(
                f"Only Ollama is available now. Use {ui.cyan('/connect ollama')}."
            )
        else:
            session.provider = AGENT_PROVIDER
            session.mode = "ollama"

    connector = AgentConnector(
        cfg=cfg,
        registry=build_tool_registry(workspace_root=workspace_root, is_trusted=False),
        tools_schema=tools_schema(is_trusted=False),
        session=session,
        is_trusted=False,
        system_prompt=system_prompt,
        workspace_root=workspace_root,
    )

    if saved_trust(cfg):
        connector.apply_trust(True)
        connector.trust_confirmed = True

    saved = saved_provider(cfg)
    if provider_name == AGENT_PROVIDER or (provider_name is None and saved == AGENT_PROVIDER):
        auto_provider = AGENT_PROVIDER
    else:
        auto_provider = None
    auto_model = model or saved_model(cfg)
    if auto_provider:
        if not connector.trust_confirmed and saved_trust(cfg):
            connector.apply_trust(True)
            connector.trust_confirmed = True
        if connector.connect(prov=auto_provider, mod=auto_model, quiet=True):
            ui.info_print(
                f"Restored {ui.bold(auto_provider)}"
                + (
                    f" · {ui.accent_muted(auto_model)}"
                    if auto_model
                    else ""
                )
                + f". {ui.dim('Still connected from last time.')}"
            )
        elif not provider_name:
            ui.info_print(
                f"Could not restore {ui.bold(auto_provider)}. "
                f"Use {ui.cyan('/connect ' + auto_provider)} when ready."
            )
    elif provider_name == AGENT_PROVIDER and ensure_trust_for_coding(connector):
        connector.connect(prov=AGENT_PROVIDER, mod=model)

    ui.print_aion_dashboard(
        cfg=cfg,
        session=session,
        version=version,
        workspace=workspace_root,
    )
    ui.print_input_area(connected=session.connected)
    last_activity = time.time()

    db_memory = None
    try:
        from ..db import agent_memory
        from ..db.settings import get_db_connection
        from ..config.core import get_nested, set_nested

        thread_id = get_nested(cfg, "agent.thread_id") or uuid.uuid4().hex[:12]
        if not get_nested(cfg, "agent.thread_id"):
            set_nested(cfg, "agent.thread_id", thread_id)
            from .config import save_config

            save_config(cfg)
        db_conn = get_db_connection(cfg)
        db_memory = agent_memory(db_conn, thread_id=thread_id)
        ui.info_print(
            f"Agent memory → {ui.dim('~/.aion/agent.db')} "
            f"· thread {ui.accent_muted(thread_id)}"
        )
    except Exception:
        pass

    while True:
        idle_mins = idle_disconnect_minutes(cfg)
        if (
            idle_mins > 0
            and connector.session.connected
            and time.time() - last_activity >= idle_mins * 60
        ):
            connector.disconnect(forget_saved=False)
            ui.info_print(
                f"Disconnected after {ui.bold(str(idle_mins))} min idle. "
                f"{ui.dim('/connect to continue (settings are still saved).')}"
            )
            ui.print_aion_dashboard(
                cfg=cfg,
                session=session,
                version=version,
                workspace=workspace_root,
            )
            ui.print_input_area(connected=False)

        try:
            user_input = ui.aion_input_prompt()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {ui.dim('Goodbye!')}\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            break

        if user_input.startswith("/"):
            rest = user_input[1:]
            if not rest or " " not in rest:
                ui.print_slash_help(rest.lower())
                if not rest:
                    continue

        try:
            action = _handle_command(
                user_input,
                connector=connector,
                workspace=workspace_root,
                db_memory=db_memory,
            )
        except KeyboardInterrupt:
            print(f"\n  {ui.dim('Cancelled.')}\n")
            continue
        if action == "quit":
            break
        if action != "chat":
            last_activity = time.time()
            continue

        if not ensure_trust_for_coding(connector):
            continue

        if not connector.agent:
            ui.error_print(f"Connect first: {ui.cyan('/connect')} or {ui.cyan('/connect ollama')}")
            continue

        try:
            response = connector.agent.chat(user_input)
            last_activity = time.time()
            if db_memory is not None:
                try:
                    db_memory.append("user", user_input)
                    db_memory.append("assistant", response)
                except Exception:
                    pass
            print()
            ui.agent_print(response, name="Aion")
            print()
            ui.print_input_area(connected=session.connected)
        except KeyboardInterrupt:
            print(f"\n  {ui.dim('Cancelled.')}\n")
            ui.print_input_area(connected=session.connected)
        except ProviderError as e:
            ui.provider_error_print(e)
        except Exception as e:
            ui.error_print(str(e))
