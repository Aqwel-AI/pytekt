"""Tool execution middleware: snapshots, diff, secrets, approval, audit."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .audit import log_action
from .diff_preview import preview_edit, preview_write
from .edit_history import EditHistory
from .secret_scan import scan_command, scan_text


MUTATING_TOOLS = frozenset({"write_file", "edit_file", "run_command"})

ApprovalHandler = Callable[[str, str, str, str], Optional[bool]]
"""Callable(diff, path, tool_name, approval_id) -> True accept, False reject, None wait."""


@dataclass
class PendingApproval:
    id: str
    path: str
    tool: str
    diff: str
    event: threading.Event = field(default_factory=threading.Event)
    result: Optional[bool] = None


class ToolMiddleware:
    """Gate mutating tool calls with safety checks."""

    def __init__(
        self,
        *,
        workspace_root: str,
        session_id: str,
        provider: Optional[str] = None,
        approval_gate: bool = False,
        allowed_commands: Optional[List[str]] = None,
        edit_history: Optional[EditHistory] = None,
        auto_approve: bool = False,
        approval_handler: Optional[ApprovalHandler] = None,
    ) -> None:
        self.workspace_root = workspace_root
        self.session_id = session_id
        self.provider = provider
        self.approval_gate = approval_gate
        self.allowed_commands = allowed_commands or []
        self.edit_history = edit_history or EditHistory(session_id)
        self.auto_approve = auto_approve
        self.approval_handler = approval_handler
        self._approve_all = False
        self._pending: Dict[str, PendingApproval] = {}
        self._lock = threading.Lock()

    @property
    def pending_approvals(self) -> List[PendingApproval]:
        with self._lock:
            return list(self._pending.values())

    def resolve_approval(self, approval_id: str, action: str) -> bool:
        """Resolve a pending approval: accept, reject, or accept_all."""
        with self._lock:
            item = self._pending.get(approval_id)
            if not item:
                return False
            if action == "accept_all":
                self._approve_all = True
                item.result = True
            elif action == "accept":
                item.result = True
            else:
                item.result = False
            item.event.set()
            self._pending.pop(approval_id, None)
            return True

    def _cli_approval(self, diff: str, path: str, tool: str) -> bool:
        print("\n--- Proposed change ---")
        print(diff[:4000])
        choice = input("Apply? [y/N/a=all]: ").strip().lower()
        if choice == "a":
            self._approve_all = True
            return True
        return choice == "y"

    def _request_approval(self, diff: str, path: str, tool: str) -> bool:
        if self.auto_approve or self._approve_all:
            return True
        if not self.approval_gate:
            return True

        if self.approval_handler is None:
            return self._cli_approval(diff, path, tool)

        approval_id = uuid.uuid4().hex[:12]
        item = PendingApproval(id=approval_id, path=path, tool=tool, diff=diff[:8000])
        result = self.approval_handler(diff, path, tool, approval_id)
        if result is not None:
            return result

        with self._lock:
            self._pending[approval_id] = item
        item.event.wait(timeout=600)
        with self._lock:
            self._pending.pop(approval_id, None)
        return bool(item.result)

    def execute(
        self,
        name: str,
        kwargs: Dict[str, Any],
        fn: Callable[..., str],
    ) -> str:
        if name == "run_command":
            cmd = str(kwargs.get("command", ""))
            if self.allowed_commands:
                base = cmd.strip().split()[0] if cmd.strip() else ""
                allowed = {c.split()[0] for c in self.allowed_commands}
                if base and base not in allowed:
                    return f"Error: command {base!r} not in allowlist"
            warnings = scan_command(cmd)
            if warnings:
                return f"Error: possible secret in command — blocked. {warnings[0]}"

        if name in ("write_file", "edit_file"):
            path = str(kwargs.get("path", ""))
            if name == "write_file":
                content = str(kwargs.get("content", ""))
                warnings = scan_text(content)
                diff = preview_write(self.workspace_root, path, content)
            else:
                old_s = str(kwargs.get("old_string", ""))
                new_s = str(kwargs.get("new_string", ""))
                warnings = scan_text(old_s + new_s)
                diff = preview_edit(self.workspace_root, path, old_s, new_s)

            if warnings:
                return f"Error: possible secret detected — blocked. {warnings[0]}"

            if self.approval_gate and not self.auto_approve and not self._approve_all:
                if not self._request_approval(diff, path, name):
                    return "Error: change rejected by user"

            self.edit_history.snapshot_before(self.workspace_root, path)

        result = fn(**kwargs)

        if name in MUTATING_TOOLS:
            log_action(
                action=name,
                path=kwargs.get("path"),
                command=kwargs.get("command"),
                provider=self.provider,
                session_id=self.session_id,
            )
        return result
