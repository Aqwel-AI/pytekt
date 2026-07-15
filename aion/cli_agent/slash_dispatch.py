"""Headless slash-command dispatch for web UI."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .command_vocab import SLASH_COMMANDS
from .constants import INTERACTION_MODES, normalize_interaction_mode
from .connect import AgentConnector
from .session_prefs import save_pinned_paths, save_trust


def dispatch_slash(
    line: str,
    *,
    connector: AgentConnector,
    workspace: str,
    on_session_update: Optional[Callable[[], None]] = None,
) -> Dict[str, Any]:
    """Parse and execute a slash command. Returns JSON-serializable result."""
    text = line.strip()
    if not text.startswith("/"):
        return {"ok": False, "error": "Not a slash command"}

    parts = text[1:].split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    def _touch() -> None:
        if on_session_update:
            on_session_update()

    if cmd == "help":
        lines = [f"/{c} {hint} — {desc}".strip() for c, hint, desc in SLASH_COMMANDS]
        return {"ok": True, "response": "\n".join(lines), "message": "Slash commands"}

    if cmd == "mode":
        if not args:
            return {
                "ok": True,
                "response": f"Current mode: {connector.session.interaction_mode}",
                "mode": connector.session.interaction_mode,
            }
        mode = normalize_interaction_mode(args.split()[0])
        if not mode:
            return {"ok": False, "error": f"Unknown mode. Use: {', '.join(INTERACTION_MODES)}"}
        try:
            connector.set_interaction_mode(mode)
            _touch()
            return {"ok": True, "message": f"Mode: {mode}", "mode": mode}
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}

    if cmd == "reset":
        if connector.agent:
            connector.agent.reset()
            return {"ok": True, "message": "Conversation memory cleared."}
        return {"ok": True, "message": "Not connected — nothing to reset."}

    if cmd == "undo":
        msg = connector.edit_history.undo_last(workspace)
        connector.session.activity.log("undo", msg)
        return {"ok": True, "message": msg, "response": msg}

    if cmd == "approve":
        if connector.session.pending_plan:
            result = connector.execute_plan()
            _touch()
            return {"ok": True, "response": result, "message": "Plan executed."}
        return {"ok": False, "error": "No pending plan."}

    if cmd == "pin":
        path = args.strip()
        if not path:
            return {"ok": False, "error": "Usage: /pin <path>"}
        if path not in connector.session.pinned_paths:
            connector.session.pinned_paths.append(path)
            save_pinned_paths(connector.cfg, connector.session.pinned_paths)
            connector.session.activity.log("pin", path)
        _touch()
        return {"ok": True, "message": f"Pinned {path}"}

    if cmd == "unpin":
        path = args.strip()
        if path and path in connector.session.pinned_paths:
            connector.session.pinned_paths.remove(path)
        elif not path:
            connector.session.pinned_paths.clear()
        save_pinned_paths(connector.cfg, connector.session.pinned_paths)
        _touch()
        return {"ok": True, "message": "Unpinned."}

    if cmd == "pins":
        if connector.session.pinned_paths:
            text_out = "Pinned: " + ", ".join(connector.session.pinned_paths)
        else:
            text_out = "No pinned paths."
        return {"ok": True, "response": text_out}

    if cmd == "tools":
        arg = args.lower().strip()
        if arg in ("on", "1", "true"):
            connector.set_force_tools(True)
            _touch()
            return {"ok": True, "message": "Force tools ON"}
        if arg in ("off", "0", "false"):
            connector.set_force_tools(False)
            _touch()
            return {"ok": True, "message": "Force tools OFF"}
        return {"ok": True, "response": f"Force tools: {connector.session.force_tools}"}

    if cmd == "init":
        from . import ui

        msg = ui.write_aion_md(workspace)
        return {"ok": True, "message": msg, "response": msg}

    if cmd == "audit":
        from .audit import format_recent

        return {"ok": True, "response": format_recent(20)}

    if cmd == "research":
        if not connector.agent or not connector._raw_provider:
            return {"ok": False, "error": "Connect first."}
        from .subagent import run_research_subagent

        query = args.strip() or "Explore the codebase"
        summary = run_research_subagent(
            connector._raw_provider,
            query,
            workspace_root=workspace,
        )
        return {"ok": True, "response": summary}

    if cmd == "mcp":
        from .session_prefs import save_mcp_servers, saved_mcp_servers

        parts = args.split()
        sub = parts[0].lower() if parts else "list"
        servers = saved_mcp_servers(connector.cfg)
        if sub in ("list", "ls", "status", ""):
            tools = getattr(connector, "_mcp_tool_names", []) or []
            return {
                "ok": True,
                "response": {
                    "servers": servers,
                    "tools": tools,
                    "errors": getattr(connector, "_mcp_errors", []) or [],
                },
            }
        if sub == "add":
            if len(parts) < 3:
                return {"ok": False, "error": "Usage: /mcp add <name> <command> [args…]"}
            name, command, *cmd_args = parts[1], parts[2], parts[3:]
            servers = [s for s in servers if s.get("name") != name]
            servers.append({"name": name, "command": command, "args": cmd_args})
            save_mcp_servers(connector.cfg, servers)
            result = connector.reload_mcp()
            _touch()
            return {"ok": True, "message": f"Saved MCP server {name}", **result}
        if sub == "remove":
            if len(parts) < 2:
                return {"ok": False, "error": "Usage: /mcp remove <name>"}
            name = parts[1]
            new_servers = [s for s in servers if s.get("name") != name]
            if len(new_servers) == len(servers):
                return {"ok": False, "error": f"No MCP server named {name}."}
            save_mcp_servers(connector.cfg, new_servers)
            result = connector.reload_mcp()
            _touch()
            return {"ok": True, "message": f"Removed {name}", **result}
        if sub == "reload":
            result = connector.reload_mcp()
            _touch()
            return {"ok": True, "message": "Reloaded MCP", **result}
        if sub == "tools":
            names = getattr(connector, "_mcp_tool_names", []) or []
            return {"ok": True, "response": names}
        return {"ok": False, "error": "Usage: /mcp [list|add|remove|reload|tools]"}

    if cmd == "commit":
        from .git_cmds import handle_commit

        handle_commit(args, workspace=workspace, pinned_files=connector.session.pinned_paths or None)
        return {"ok": True, "message": "Commit handled."}

    if cmd == "branch":
        from .git_cmds import handle_branch

        handle_branch(args, workspace=workspace)
        return {"ok": True, "message": "Branch handled."}

    if cmd == "trust":
        arg = args.lower().strip()
        if arg in ("on", "1", "true", "yes"):
            connector.apply_trust(True)
            save_trust(connector.cfg, trusted=True)
            connector.trust_confirmed = True
            _touch()
            return {"ok": True, "message": "Trust ON", "trust": True}
        if arg in ("off", "0", "false", "no"):
            connector.apply_trust(False)
            save_trust(connector.cfg, trusted=False)
            connector.trust_confirmed = False
            _touch()
            return {"ok": True, "message": "Trust OFF", "trust": False}
        return {"ok": True, "response": f"Trust: {connector.session.is_trusted}"}

    if cmd in ("quit", "web"):
        return {"ok": False, "error": f"/{cmd} is only available in the terminal agent."}

    if cmd == "usage":
        return {
            "ok": True,
            "message": "Open usage dashboard",
            "action": "open_url",
            "url": "http://127.0.0.1:3847/",
        }

    return {"ok": False, "error": f"Unknown command /{cmd}. Type /help for commands."}
