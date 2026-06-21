"""Thread-safe web wrapper around AgentConnector."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from ..config import get_config
from ..mentions import expand_mentions
from ..session_prefs import (
    save_pinned_paths,
    save_trust,
    saved_workspace_roots,
)
from ..tools import build_tool_registry, tools_schema
from .. import ui
from ..connect import AgentConnector
from .events import EventBus


class WebAgentService:
    """Single shared agent session for the web server."""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = os.path.abspath(workspace_root)
        self.cfg = get_config()
        self.events = EventBus()
        self._lock = threading.RLock()
        self._chat_lock = threading.Lock()
        session = ui.AgentSession(
            mode="offline",
            is_trusted=False,
            interaction_mode=__import__(
                "aion.cli_agent.session_prefs", fromlist=["saved_interaction_mode"]
            ).saved_interaction_mode(self.cfg),
        )
        self.connector = AgentConnector(
            cfg=self.cfg,
            registry=build_tool_registry(workspace_root=self.workspace_root, is_trusted=False),
            tools_schema=tools_schema(is_trusted=False),
            session=session,
            is_trusted=False,
            workspace_root=self.workspace_root,
        )
        self.connector.set_event_callback(self._on_connector_event)
        self._wire_approval_handler()

    def _on_connector_event(self, event_type: str, data: Dict[str, Any]) -> None:
        self.events.publish(event_type, **data)

    def _wire_approval_handler(self) -> None:
        bus = self.events
        middleware = self.connector.tool_middleware

        def handler(diff: str, path: str, tool: str, approval_id: str) -> Optional[bool]:
            bus.publish(
                "approval_required",
                id=approval_id,
                path=path,
                tool=tool,
                diff=diff[:8000],
            )
            return None

        middleware.approval_handler = handler

    def _publish_session(self) -> None:
        self.events.publish("session_updated", session=self.session_dict())

    def session_dict(self) -> Dict[str, Any]:
        return self.connector.session_dict()

    def list_providers(self) -> List[Dict[str, Any]]:
        from ..constants import CONNECTABLE_PROVIDERS, PROVIDER_ENV_VARS, provider_display_name
        from ...providers.keys import resolve_api_key

        out = []
        for pid in sorted(CONNECTABLE_PROVIDERS):
            has_key = pid == "ollama" or bool(resolve_api_key(pid, self.cfg))
            out.append(
                {
                    "id": pid,
                    "label": provider_display_name(pid),
                    "env_var": PROVIDER_ENV_VARS.get(pid),
                    "ready": has_key,
                }
            )
        return out

    def list_models(self, provider_id: str) -> Dict[str, Any]:
        with self._lock:
            return self.connector.list_models_api(provider_id)

    def connect(
        self,
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self._lock:
            result = self.connector.connect_api(prov=provider, mod=model, api_key=api_key)
            self._publish_session()
            return result

    def disconnect(self) -> Dict[str, Any]:
        with self._lock:
            self.connector.disconnect(forget_saved=False)
            self._publish_session()
            return {"ok": True}

    def set_mode(self, mode: str) -> Dict[str, Any]:
        with self._lock:
            try:
                self.connector.set_interaction_mode(mode)
                self._publish_session()
                return {"ok": True, "mode": mode}
            except ValueError as e:
                return {"ok": False, "error": str(e)}

    def set_trust(self, trusted: bool) -> Dict[str, Any]:
        with self._lock:
            self.connector.apply_trust(trusted)
            save_trust(self.cfg, trusted=trusted)
            self.connector.trust_confirmed = trusted
            self._publish_session()
            return {"ok": True, "trust": trusted}

    def pin(self, path: str) -> Dict[str, Any]:
        with self._lock:
            if path not in self.connector.session.pinned_paths:
                self.connector.session.pinned_paths.append(path)
                save_pinned_paths(self.cfg, self.connector.session.pinned_paths)
            self._publish_session()
            return {"ok": True, "pinned_paths": self.connector.session.pinned_paths}

    def unpin(self, path: Optional[str] = None) -> Dict[str, Any]:
        with self._lock:
            if path:
                if path in self.connector.session.pinned_paths:
                    self.connector.session.pinned_paths.remove(path)
            else:
                self.connector.session.pinned_paths.clear()
            save_pinned_paths(self.cfg, self.connector.session.pinned_paths)
            self._publish_session()
            return {"ok": True, "pinned_paths": self.connector.session.pinned_paths}

    def undo(self) -> Dict[str, Any]:
        with self._lock:
            msg = self.connector.edit_history.undo_last(self.workspace_root)
            self.events.publish("undo", message=msg)
            return {"ok": True, "message": msg}

    def reset(self) -> Dict[str, Any]:
        with self._lock:
            if self.connector.agent:
                self.connector.agent.reset()
            return {"ok": True}

    def approve_diff(self, approval_id: str, action: str) -> Dict[str, Any]:
        with self._lock:
            ok = self.connector.tool_middleware.resolve_approval(approval_id, action)
            return {"ok": ok}

    def pending_approvals(self) -> List[Dict[str, Any]]:
        items = self.connector.tool_middleware.pending_approvals
        return [
            {"id": p.id, "path": p.path, "tool": p.tool, "diff": p.diff}
            for p in items
        ]

    def activity(self, n: int = 20) -> List[Dict[str, str]]:
        events = self.connector.session.activity.recent(n)
        return [{"kind": e.kind, "detail": e.detail, "ts": e.ts} for e in events]

    def list_files(self, path: str = ".", recursive: bool = False) -> Dict[str, Any]:
        from ...tools.code_agent import list_files
        from ...tools.workspace import Workspace

        ws = Workspace(self.workspace_root)
        listing = list_files(ws, path, recursive=recursive)
        entries = []
        if not listing.startswith("Error"):
            for line in listing.splitlines():
                if line.startswith("…"):
                    continue
                entries.append(line)
        return {"path": path, "entries": entries, "raw": listing}

    def read_file(self, path: str, limit: int = 400) -> Dict[str, Any]:
        from ...tools.code_agent import read_file
        from ...tools.workspace import Workspace

        ws = Workspace(self.workspace_root)
        content = read_file(ws, path, limit=limit)
        return {"path": path, "content": content}

    def write_open_files(self, paths: List[str]) -> None:
        sidecar = Path(self.workspace_root) / ".aion" / "open_files.json"
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "updated_at": time.time(),
            "files": [{"path": p} for p in paths],
        }
        sidecar.write_text(json.dumps(data), encoding="utf-8")

    def _enrich(self, message: str) -> str:
        enriched, _ = expand_mentions(
            message,
            self.workspace_root,
            pinned_paths=self.connector.session.pinned_paths,
            extra_roots=saved_workspace_roots(self.cfg),
        )
        return enriched

    def chat(self, message: str) -> Dict[str, Any]:
        with self._chat_lock:
            if not self.connector.agent:
                return {"ok": False, "error": "Not connected"}
            try:
                enriched = self._enrich(message)
                self.events.publish("chat_start", message=message)
                response = self.connector.chat(enriched)
                self.events.publish("chat_done", response=response)
                self._publish_session()
                return {"ok": True, "response": response}
            except Exception as e:
                self.events.publish("error", message=str(e))
                return {"ok": False, "error": str(e)}

    def chat_stream(self, message: str) -> Iterator[str]:
        """Yield SSE lines for a chat turn."""
        from .events import AgentEvent

        with self._chat_lock:
            if not self.connector.agent:
                yield AgentEvent(type="error", data={"message": "Not connected"}).to_sse()
                return

            enriched = self._enrich(message)
            self.events.publish("chat_start", message=message)

            if self.connector.session.interaction_mode != "plain":
                try:
                    response = self.connector.chat(enriched)
                    yield AgentEvent(type="chat_done", data={"response": response}).to_sse()
                    self._publish_session()
                except Exception as e:
                    yield AgentEvent(type="error", data={"message": str(e)}).to_sse()
                return

            inner = getattr(self.connector._raw_provider, "_inner", self.connector._raw_provider)
            if hasattr(inner, "complete_stream"):
                from ...providers.base import ChatMessage

                parts: List[str] = []
                try:
                    for token in inner.complete_stream(
                        [ChatMessage(role="user", content=enriched)],
                        max_tokens=4096,
                    ):
                        parts.append(token)
                        yield AgentEvent(type="chat_token", data={"text": token}).to_sse()
                    text = "".join(parts)
                    if self.connector.agent:
                        self.connector.agent.memory.add({"role": "user", "content": enriched})
                        self.connector.agent.memory.add({"role": "assistant", "content": text})
                    yield AgentEvent(type="chat_done", data={"response": text}).to_sse()
                except Exception:
                    response = self.connector.chat(enriched)
                    yield AgentEvent(type="chat_done", data={"response": response}).to_sse()
            else:
                try:
                    response = self.connector.chat(enriched)
                    yield AgentEvent(type="chat_done", data={"response": response}).to_sse()
                except Exception as e:
                    yield AgentEvent(type="error", data={"message": str(e)}).to_sse()
            self._publish_session()

    def run_command(self, cmd: str, args: str = "") -> Dict[str, Any]:
        with self._lock:
            if cmd == "approve":
                result = self.connector.execute_plan()
                self._publish_session()
                return {"ok": True, "response": result}
            if cmd == "research":
                if not self.connector.agent:
                    return {"ok": False, "error": "Not connected"}
                from ..subagent import run_research_subagent

                summary = run_research_subagent(
                    self.connector._raw_provider or self.connector.agent.provider,
                    args or "Explore codebase",
                    workspace_root=self.workspace_root,
                )
                return {"ok": True, "response": summary}
            if cmd == "commit":
                from ..git_cmds import handle_commit

                handle_commit(args, workspace=self.workspace_root, pinned_files=self.connector.session.pinned_paths or None)
                return {"ok": True}
            if cmd == "branch":
                from ..git_cmds import handle_branch

                handle_branch(args, workspace=self.workspace_root)
                return {"ok": True}
            return {"ok": False, "error": f"Unknown command: {cmd}"}


_SERVICE: Optional[WebAgentService] = None
_SERVICE_LOCK = threading.Lock()


def get_service(workspace_root: Optional[str] = None) -> WebAgentService:
    global _SERVICE
    with _SERVICE_LOCK:
        if _SERVICE is None:
            root = workspace_root or os.getcwd()
            _SERVICE = WebAgentService(root)
        return _SERVICE
