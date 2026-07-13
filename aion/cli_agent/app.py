"""Main interactive agent — Aion terminal shell."""

from __future__ import annotations

import os
import time
import uuid
from typing import Any, Optional

from ..providers.errors import ProviderError
from ..agents.runtime import AgentRuntime
from . import ui
from .commands_runtime import handle_runtime_command
from .config import get_config
from .connect import AgentConnector
from .connect_args import parse_connect_args, parse_disconnect_args
from .constants import (
    CONNECTABLE_PROVIDERS,
    INTERACTION_MODE_LABELS,
    INTERACTION_MODES,
    normalize_interaction_mode,
    provider_display_name,
)
from .mentions import expand_mentions
from .session_prefs import (
    idle_disconnect_minutes,
    save_idle_disconnect_minutes,
    save_pinned_paths,
    save_safety_mode,
    save_specialist_mode,
    save_workspace_roots,
    saved_safety_mode,
    saved_specialist_mode,
    saved_interaction_mode,
    saved_model,
    saved_provider,
    saved_trust,
    saved_workspace_roots,
)
from .tools import build_tool_registry, tools_schema
from .universe_cmds import handle_sky_command
from .physics_cmds import handle_physics_command
from .db_cmds import handle_db_command
from .trust import ensure_trust_for_coding


def _clear_web_chat_memory() -> None:
    """Clear browser chat when the terminal session ends or disconnects."""
    try:
        from .web.service import clear_web_memory

        clear_web_memory()
    except Exception:
        pass


def _handle_command(
    text: str,
    *,
    connector: AgentConnector,
    workspace: str,
    db_memory: Optional[Any] = None,
    runtime: Optional[AgentRuntime] = None,
    tui: Optional[Any] = None,
) -> Optional[str]:
    """Returns 'quit' to exit loop, None to continue."""
    if text == "?":
        ui.print_shortcuts()
        return None

    if not text.startswith("/"):
        return "chat"

    if runtime is not None and tui is not None:
        runtime_result = handle_runtime_command(text, runtime=runtime, tui=tui)
        if runtime_result is None:
            return None

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
        from ..providers.keys import resolve_api_key

        quiet = False
        new_key = False
        if cmd == "reconnect":
            prov = saved_provider(connector.cfg)
            mod = saved_model(connector.cfg)
            if prov in CONNECTABLE_PROVIDERS and mod:
                key_ok = prov == "ollama" or bool(resolve_api_key(prov, connector.cfg))
                quiet = key_ok
            else:
                prov, mod = None, None
        elif args:
            prov, mod, new_key = parse_connect_args(args)
        else:
            saved = saved_provider(connector.cfg)
            if saved in CONNECTABLE_PROVIDERS:
                prov = saved
                mod = saved_model(connector.cfg)
                key_ok = saved == "ollama" or bool(resolve_api_key(saved, connector.cfg))
                quiet = bool(mod and key_ok)
            else:
                providers = ["ollama", "nvidia"]
                ui.print_menu(
                    [provider_display_name(p) for p in providers],
                    "Select provider",
                )
                choice = ui.get_menu_choice([provider_display_name(p) for p in providers])
                prov = providers[choice - 1]
                mod = None
        if connector.connect(
            prov=prov,
            mod=mod,
            quiet=quiet,
            new_key=new_key,
        ):
            if runtime is not None:
                runtime.connect_state()
            if runtime is not None and tui is not None:
                tui.draw_dashboard(session=connector.session, runtime=runtime)
            else:
                ui.print_aion_dashboard(
                    cfg=connector.cfg,
                    session=connector.session,
                    version=_version(),
                    workspace=workspace,
                )
            ui.print_input_area(connected=True)
        return None

    if cmd == "mode":
        if not args:
            ui.print_menu(
                [INTERACTION_MODE_LABELS[m] for m in INTERACTION_MODES],
                "Select interaction mode",
            )
            choice = ui.get_menu_choice([INTERACTION_MODE_LABELS[m] for m in INTERACTION_MODES])
            mode = INTERACTION_MODES[choice - 1]
        else:
            mode = normalize_interaction_mode(args.split()[0])
            if not mode:
                ui.error_print(
                    f"Unknown mode. Use: {ui.cyan('/mode plain|agent|debug')}"
                )
                return None
        try:
            connector.set_interaction_mode(mode)
        except ValueError as e:
            ui.error_print(str(e))
            return None
        ui.success_print(f"Interaction mode: {ui.bold(mode)}")
        if runtime is not None:
            runtime.connect_state()
        if runtime is not None and tui is not None:
            tui.draw_dashboard(session=connector.session, runtime=runtime)
        else:
            ui.print_aion_dashboard(
                cfg=connector.cfg,
                session=connector.session,
                version=_version(),
                workspace=workspace,
            )
        ui.print_input_area(connected=connector.session.connected)
        return None

    if cmd == "safety":
        from .constants import SAFETY_MODES, normalize_safety_mode

        if not args:
            ui.info_print(f"Safety mode: {ui.bold(connector.session.safety_mode)}")
            return None
        mode = normalize_safety_mode(args.split()[0])
        if not mode:
            ui.error_print("Unknown safety mode. Use: " + ", ".join(SAFETY_MODES))
            return None
        connector.session.safety_mode = mode
        connector.tool_middleware.safety_mode = mode
        save_safety_mode(connector.cfg, mode)
        ui.success_print(f"Safety mode: {ui.bold(mode)}")
        return None

    if cmd == "role":
        from .constants import SPECIALIST_MODES, normalize_specialist_mode

        if not args:
            ui.info_print(f"Specialist mode: {ui.bold(connector.session.specialist_mode)}")
            return None
        mode = normalize_specialist_mode(args.split()[0])
        if not mode:
            ui.error_print("Unknown specialist mode. Use: " + ", ".join(SPECIALIST_MODES))
            return None
        connector.session.specialist_mode = mode
        save_specialist_mode(connector.cfg, mode)
        if connector.session.connected and connector.session.provider and connector.session.model and connector._raw_provider is not None:
            connector.agent = connector._build_agent(connector._raw_provider, connector.session.provider, connector.session.model)
            connector._apply_session(connector.session.provider, connector.session.model)
        ui.success_print(f"Specialist mode: {ui.bold(mode)}")
        return None

    if cmd == "status":
        ui.print_status_bar(connector.session)
        ui.info_print(f"Working directory: {ui.cyan(workspace)}")
        if connector.session.project_info:
            ui.info_print(ui.dim(connector.session.project_info.summary()))
        if connector.session.pinned_paths:
            ui.info_print(f"Pinned: {ui.accent_muted(', '.join(connector.session.pinned_paths))}")
        ui.info_print(ui.dim(connector.session.activity.format_dashboard(5)))
        if connector.session.connected:
            ui.info_print(
                f"Provider: {ui.bold(connector.session.provider or '')}"
                + (
                    f" · {ui.accent_muted(connector.session.model)}"
                    if connector.session.model
                    else ""
                )
            )
        return None

    if cmd == "reset":
        if connector.agent:
            connector.agent.reset()
            ui.success_print("Conversation memory cleared.")
        else:
            ui.info_print("Not connected — nothing to reset.")
        return None

    if cmd == "models":
        if runtime is not None and tui is not None:
            runtime.connect_state()
            tui.draw_dashboard(session=connector.session, runtime=runtime)
        else:
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
            keys_cleared = connector.disconnect(
                forget_saved=False,
                clear_keys_for=req.provider,
                disconnect_session=False,
            )
            if keys_cleared:
                ui.success_print(
                    f"Removed saved key for {ui.bold(req.label)}. "
                    f"Still using {ui.bold(was_prov or '')}"
                    + (f" · {ui.accent_muted(was_model)}" if was_model else "")
                    + "."
                )
            else:
                ui.info_print(f"No saved API key found for {ui.bold(req.label)}.")
            if runtime is not None:
                runtime.connect_state()
            if runtime is not None and tui is not None:
                tui.draw_dashboard(session=connector.session, runtime=runtime)
            else:
                ui.print_aion_dashboard(
                    cfg=connector.cfg,
                    session=connector.session,
                    version=_version(),
                    workspace=workspace,
                )
            ui.print_input_area(connected=connector.session.connected)
            return None

        keys_cleared = connector.disconnect(
            forget_saved=req.forget_saved,
            clear_keys_for=req.provider if req.clear_keys else None,
            disconnect_session=req.disconnect_session,
        )
        if req.disconnect_session:
            _clear_web_chat_memory()

        target = req.label or was_prov or "session"
        if req.disconnect_session and (was_prov or req.provider):
            if keys_cleared:
                extra = ui.dim("Saved API key removed.")
            elif req.forget_saved:
                extra = ui.dim("Saved connection cleared.")
            else:
                extra = ui.dim(
                    "Settings kept — /reconnect or restart restores the session. "
                    "/disconnect forget to clear."
                )
            ui.success_print(f"Disconnected {ui.bold(target)}. {extra}")
        elif keys_cleared:
            ui.success_print(f"Removed saved key for {ui.bold(target)}.")
        elif not req.disconnect_session:
            ui.info_print(f"No changes for {ui.bold(target)}.")
        else:
            ui.success_print("Offline.")
        if runtime is not None:
            runtime.connect_state()
        if runtime is not None and tui is not None:
            tui.draw_dashboard(session=connector.session, runtime=runtime)
        else:
            ui.print_aion_dashboard(
                cfg=connector.cfg,
                session=connector.session,
                version=_version(),
                workspace=workspace,
            )
        ui.print_input_area(connected=connector.session.connected)
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

    if cmd == "web":
        from .web.launch import ensure_agent_web

        url, started = ensure_agent_web(open_browser=True)
        if started:
            ui.success_print(f"Agent web UI started at {ui.cyan(url)}")
        else:
            ui.info_print(f"Opened {ui.cyan(url)} (already running)")
        return None

    if cmd == "db":
        handle_db_command(args, cfg=connector.cfg, memory=db_memory)
        return None

    if cmd == "sky":
        handle_sky_command(args, cfg=connector.cfg)
        return None

    if cmd == "physics":
        handle_physics_command(args, cfg=connector.cfg)
        return None

    if cmd == "pin":
        path = args.strip()
        if not path:
            ui.error_print("Usage: /pin <path>")
            return None
        if path not in connector.session.pinned_paths:
            connector.session.pinned_paths.append(path)
            save_pinned_paths(connector.cfg, connector.session.pinned_paths)
            connector.session.activity.log("pin", path)
        ui.success_print(f"Pinned {ui.bold(path)}")
        return None

    if cmd == "unpin":
        path = args.strip()
        if path and path in connector.session.pinned_paths:
            connector.session.pinned_paths.remove(path)
            save_pinned_paths(connector.cfg, connector.session.pinned_paths)
        elif not path:
            connector.session.pinned_paths.clear()
            save_pinned_paths(connector.cfg, [])
        ui.success_print("Unpinned.")
        return None

    if cmd == "pins":
        if connector.session.pinned_paths:
            ui.info_print("Pinned paths: " + ", ".join(connector.session.pinned_paths))
        else:
            ui.info_print("No pinned paths.")
        return None

    if cmd == "undo":
        msg = connector.edit_history.undo_last(workspace)
        connector.session.activity.log("undo", msg)
        ui.success_print(msg)
        return None

    if cmd == "revert":
        actions = connector.tool_middleware.rollback_current_batch()
        ui.info_print("\n".join(actions))
        return None

    if cmd == "diff":
        print()
        ui.info_print(connector.tool_middleware.latest_diff_preview())
        print()
        return None

    if cmd == "validate":
        result = connector.tool_middleware.validate_current_batch()
        if result.ok:
            ui.success_print(result.summary)
        else:
            ui.error_print(result.summary + "\n" + "\n".join(result.errors[:10]))
        return None

    if cmd == "audit":
        from .audit import format_recent

        ui.info_print(format_recent(20))
        return None

    if cmd == "tools":
        if args.lower() in ("on", "1", "true"):
            connector.set_force_tools(True)
            ui.success_print("Force tools ON")
        elif args.lower() in ("off", "0", "false"):
            connector.set_force_tools(False)
            ui.success_print("Force tools OFF")
        else:
            ui.info_print(f"Force tools: {connector.session.force_tools}")
        return None

    if cmd == "root":
        from .multi_workspace import MultiWorkspace

        sub = args.split()
        if sub and sub[0].lower() == "add" and len(sub) > 1:
            mw = MultiWorkspace(workspace, extra_roots=saved_workspace_roots(connector.cfg))
            added = mw.add_root(sub[1])
            save_workspace_roots(connector.cfg, mw.list_roots()[1:])
            ui.success_print(f"Added workspace root: {ui.bold(added)}")
        else:
            roots = [workspace] + saved_workspace_roots(connector.cfg)
            ui.info_print("Workspace roots:\n" + "\n".join(f"  • {r}" for r in roots))
        return None

    if cmd == "approve":
        if connector.session.interaction_mode == "plan":
            response = connector.execute_plan()
            ui.agent_print(response, name="Aion")
            print()
        else:
            ui.info_print("No pending plan.")
        return None

    if cmd == "research":
        if not connector.agent or not connector._raw_provider:
            ui.error_print("Connect first.")
            return None
        from .subagent import run_research_subagent

        query = args.strip() or "Explore the codebase"
        summary = run_research_subagent(
            connector._raw_provider,
            query,
            workspace_root=workspace,
        )
        ui.agent_print(summary, name="Research")
        print()
        return None

    if cmd == "commit":
        from .git_cmds import handle_commit

        handle_commit(args, workspace=workspace, pinned_files=connector.session.pinned_paths or None)
        return None

    if cmd == "branch":
        from .git_cmds import handle_branch

        handle_branch(args, workspace=workspace)
        return None

    if cmd == "pr-summary":
        from .git_cmds import handle_pr_summary

        handle_pr_summary(args, workspace=workspace, connector=connector)
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


def _chat_response(
    connector: AgentConnector,
    enriched: str,
    raw_input: str,
    *,
    runtime: Optional[AgentRuntime] = None,
) -> str:
    """Chat with optional streaming for plain mode."""
    if runtime is not None and connector.session.interaction_mode == "plain" and connector._raw_provider:
        print()
        parts: list[str] = []
        try:
            for token in runtime.run_plain_stream(enriched):
                print(token, end="", flush=True)
                parts.append(token)
            print()
            return "".join(parts)
        except Exception:
            pass
    if runtime is not None:
        return runtime.run_prompt(enriched)
    return connector.chat(enriched)


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
    session = ui.AgentSession(
        mode="offline",
        is_trusted=False,
        interaction_mode=saved_interaction_mode(cfg),
        safety_mode=saved_safety_mode(cfg),
        specialist_mode=saved_specialist_mode(cfg),
    )
    ui.configure_input(workspace_root)

    from .constants import CONNECTABLE_PROVIDERS, COMING_SOON_PROVIDERS, provider_display_name

    if provider_name:
        if provider_name in COMING_SOON_PROVIDERS:
            ui.info_print(
                f"{provider_display_name(provider_name)} is coming soon — not available yet. "
                f"Use {ui.cyan('/connect ollama')} or {ui.cyan('/connect nvidia')}."
            )
        elif provider_name not in CONNECTABLE_PROVIDERS:
            ui.info_print(
                f"Use {ui.cyan('/connect ollama')} or {ui.cyan('/connect nvidia')}."
            )
        else:
            session.provider = provider_name
            session.mode = provider_name

    connector = AgentConnector(
        cfg=cfg,
        registry=build_tool_registry(workspace_root=workspace_root, is_trusted=False),
        tools_schema=tools_schema(is_trusted=False),
        session=session,
        is_trusted=False,
        system_prompt=system_prompt,
        workspace_root=workspace_root,
    )
    runtime = AgentRuntime(workspace_root=workspace_root, connector=connector)
    tui = ui.ModernTerminalUI(version=version, workspace=workspace_root)

    if saved_trust(cfg):
        connector.apply_trust(True)
        connector.trust_confirmed = True

    saved = saved_provider(cfg)
    if provider_name in CONNECTABLE_PROVIDERS:
        auto_provider = provider_name
    elif provider_name is None and saved in CONNECTABLE_PROVIDERS:
        auto_provider = saved
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
            from ..providers.keys import resolve_api_key

            if auto_provider == "nvidia" and not resolve_api_key("nvidia", cfg):
                ui.info_print(
                    f"Could not restore {ui.bold('nvidia')}. "
                    f"Run {ui.cyan('aion api add nvidia YOUR_KEY')} then restart or "
                    f"{ui.cyan('/connect nvidia')}."
                )
            else:
                ui.info_print(
                    f"Could not restore {ui.bold(auto_provider)}. "
                    f"Use {ui.cyan('/connect ' + auto_provider)} when ready."
                )
    elif provider_name in CONNECTABLE_PROVIDERS and ensure_trust_for_coding(connector):
        connector.connect(prov=provider_name, mod=model)

    runtime.connect_state()
    tui.draw_dashboard(session=session, runtime=runtime)
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

    try:
        while True:
            idle_mins = idle_disconnect_minutes(cfg)
            if (
                idle_mins > 0
                and connector.session.connected
                and time.time() - last_activity >= idle_mins * 60
            ):
                connector.disconnect(forget_saved=False)
                _clear_web_chat_memory()
                ui.info_print(
                    f"Disconnected after {ui.bold(str(idle_mins))} min idle. "
                    f"{ui.dim('/connect to continue (settings are still saved).')}"
                )
                runtime.connect_state()
                tui.draw_dashboard(session=session, runtime=runtime)
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
                    runtime=runtime,
                    tui=tui,
                )
            except KeyboardInterrupt:
                print(f"\n  {ui.dim('Cancelled.')}\n")
                continue
            if action == "quit":
                break
            if action != "chat":
                last_activity = time.time()
                continue

            if connector.session.interaction_mode != "plain":
                if not ensure_trust_for_coding(connector):
                    continue

            if not connector.agent:
                ui.error_print(
                    f"Connect first: {ui.cyan('/connect')} · "
                    f"{ui.cyan('/connect ollama')} · {ui.cyan('/connect nvidia')}"
                )
                continue

            try:
                enriched, attachments = expand_mentions(
                    user_input,
                    workspace_root,
                    pinned_paths=connector.session.pinned_paths,
                    extra_roots=saved_workspace_roots(connector.cfg),
                )
                if attachments:
                    ui.info_print(f"Attached: {ui.accent_muted(', '.join(attachments))}")
                print(f"  {ui.dim(ui.spinner_label(session))}", flush=True)
                response = _chat_response(connector, enriched, user_input, runtime=runtime)
                connector.print_edit_batch_summary()
                last_activity = time.time()
                runtime.connect_state()
                if db_memory is not None:
                    try:
                        db_memory.append("user", user_input)
                        db_memory.append("assistant", response)
                    except Exception:
                        pass
                tui.draw_dashboard(session=session, runtime=runtime)
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
    finally:
        _clear_web_chat_memory()
