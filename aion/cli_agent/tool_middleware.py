"""Tool execution middleware: snapshots, diff, validation, approval, audit."""

from __future__ import annotations

import ast
import json
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .audit import log_action
from .diff_preview import preview_edit, preview_write
from .edit_history import EditHistory
from .project import ProjectInfo
from .runtime_models import ArtifactRecord, CommandRecord, EditIntent, ValidationResult
from .secret_scan import scan_command, scan_text
from ..tools.code_agent import run_command
from ..tools.workspace import Workspace


MUTATING_TOOLS = frozenset({"write_file", "edit_file", "run_command"})
DESTRUCTIVE_COMMAND_MARKERS = ("rm ", "git reset", "git clean", "mv ", "rmdir ", "del ")
GIT_COMMAND_PREFIXES = ("git ",)
ApprovalHandler = Callable[[str, str, str, str], Optional[bool]]

SAFETY_MODES = frozenset(
    {"read-only", "workspace-write", "full-trusted", "shell-disabled", "network-disabled"}
)


@dataclass
class PendingApproval:
    id: str
    path: str
    tool: str
    diff: str
    event: threading.Event = field(default_factory=threading.Event)
    result: Optional[bool] = None


class ToolMiddleware:
    """Gate mutating tool calls with safety checks and edit validation."""

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
        project_info: Optional[ProjectInfo] = None,
        safety_mode: str = "workspace-write",
        validate_after_edits: bool = True,
    ) -> None:
        self.workspace_root = workspace_root
        self.session_id = session_id
        self.provider = provider
        self.approval_gate = approval_gate
        self.allowed_commands = allowed_commands or []
        self.edit_history = edit_history or EditHistory(session_id)
        self.auto_approve = auto_approve
        self.approval_handler = approval_handler
        self.project_info = project_info
        self.safety_mode = safety_mode if safety_mode in SAFETY_MODES else "workspace-write"
        self.validate_after_edits = validate_after_edits
        self._approve_all = False
        self._pending: Dict[str, PendingApproval] = {}
        self._lock = threading.Lock()
        self._current_task_id: Optional[str] = None
        self._current_intent: Optional[EditIntent] = None
        self._last_intent: Optional[EditIntent] = None
        self._artifacts: List[ArtifactRecord] = []
        self._commands: List[CommandRecord] = []

    @property
    def pending_approvals(self) -> List[PendingApproval]:
        with self._lock:
            return list(self._pending.values())

    @property
    def last_intent(self) -> Optional[EditIntent]:
        return self._last_intent

    @property
    def artifacts(self) -> List[ArtifactRecord]:
        return list(self._artifacts)

    @property
    def commands(self) -> List[CommandRecord]:
        return list(self._commands)

    def start_task(self, user_request: str) -> str:
        """Open an edit-intent batch for one user task."""
        task_id = uuid.uuid4().hex[:10]
        self._current_task_id = task_id
        self._current_intent = EditIntent(task_id=task_id, user_request=user_request, status="running")
        self._artifacts = []
        self._commands = []
        return task_id

    def finalize_task(self, *, rollback_on_failure: bool = False) -> Optional[EditIntent]:
        """Finalize the current edit intent and optionally rollback on validation failure."""
        intent = self._current_intent
        if intent is None:
            return None
        if intent.validation is None:
            intent.validation = ValidationResult(ok=True, summary="No file edits performed.")
        if rollback_on_failure and intent.validation and not intent.validation.ok:
            intent.rollback_actions = self.edit_history.rollback_task(self.workspace_root, intent.task_id)
            intent.status = "rolled_back"
        elif intent.validation and intent.validation.ok:
            intent.status = "completed"
        else:
            intent.status = "failed"
        self._last_intent = intent
        self._current_task_id = None
        self._current_intent = None
        return intent

    def diff_summary(self) -> str:
        """Return a staged summary of the current or last edit batch."""
        intent = self._current_intent or self._last_intent
        if intent is None or not intent.file_summaries:
            return "No staged edits."
        return "\n".join(intent.file_summaries)

    def touched_files(self) -> List[str]:
        """Return touched files from the current or last intent."""
        intent = self._current_intent or self._last_intent
        if intent is None:
            return []
        return list(intent.paths)

    def latest_diff_preview(self, *, limit: int = 12000) -> str:
        """Return concatenated diff previews for the current or last edit intent."""
        intent = self._current_intent or self._last_intent
        if intent is None or not intent.diffs:
            return "No diff preview available."
        chunks = []
        for path in intent.paths:
            diff = intent.diffs.get(path)
            if diff:
                chunks.append(diff)
        text = "\n\n".join(chunks)
        return text[:limit]

    def resolve_approval(self, approval_id: str, action: str) -> bool:
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

    def _require_approval_for_command(self, cmd: str) -> bool:
        lowered = cmd.strip().casefold()
        if any(marker in lowered for marker in DESTRUCTIVE_COMMAND_MARKERS):
            return True
        if any(lowered.startswith(prefix) for prefix in GIT_COMMAND_PREFIXES):
            return True
        return False

    def _check_safety_mode(self, name: str, kwargs: Dict[str, Any]) -> Optional[str]:
        if self.safety_mode == "read-only" and name in MUTATING_TOOLS:
            return "Error: read-only safety mode blocks mutating tools."
        if self.safety_mode == "shell-disabled" and name == "run_command":
            return "Error: shell-disabled safety mode blocks run_command."
        if name == "run_command":
            cmd = str(kwargs.get("command", "")).casefold()
            if self.safety_mode == "network-disabled":
                network_markers = ("curl ", "wget ", "pip install", "npm install", "uv pip", "git clone")
                if any(marker in cmd for marker in network_markers):
                    return "Error: network-disabled safety mode blocks network commands."
        return None

    def _track_edit_preview(self, path: str, diff: str) -> None:
        intent = self._current_intent
        if intent is None:
            return
        if path not in intent.paths:
            intent.paths.append(path)
        intent.diffs[path] = diff
        summary_line = f"{path}: {len(diff.splitlines())} diff lines"
        if summary_line not in intent.file_summaries:
            intent.file_summaries.append(summary_line)

    def _python_syntax_check(self, path: Path) -> Optional[str]:
        if path.suffix != ".py":
            return None
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            return f"Python syntax error in {path.name}: {exc}"
        return None

    def _json_syntax_check(self, path: Path) -> Optional[str]:
        if path.suffix != ".json":
            return None
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return f"JSON syntax error in {path.name}: {exc}"
        return None

    def _run_validation_command(self, command: str) -> CommandRecord:
        workspace = Workspace(self.workspace_root)
        output = run_command(workspace, command, timeout=120)
        returncode = 0
        lowered = output.casefold()
        if lowered.startswith("error:") or "returned " in lowered and "stdout" in lowered:
            returncode = 1
        record = CommandRecord(command=command, returncode=returncode, output_preview=output[:500])
        self._commands.append(record)
        self._artifacts.append(
            ArtifactRecord(kind="command", command=command, description="validation command", metadata={"returncode": returncode})
        )
        return record

    def validate_current_batch(self) -> ValidationResult:
        """Run syntax and project-level validation for the current edit batch."""
        intent = self._current_intent
        if intent is None or not intent.paths:
            result = ValidationResult(ok=True, summary="No file edits to validate.")
            if intent is not None:
                intent.validation = result
            return result

        checks: List[str] = []
        errors: List[str] = []
        warnings: List[str] = []

        for rel_path in intent.paths:
            abs_path = Path(self.workspace_root) / rel_path
            checks.append(f"file exists: {rel_path}")
            if not abs_path.exists():
                errors.append(f"Missing expected file: {rel_path}")
                continue
            syntax_error = self._python_syntax_check(abs_path) or self._json_syntax_check(abs_path)
            if syntax_error:
                errors.append(syntax_error)

        info = self.project_info
        if self.validate_after_edits and info:
            if info.lint_command:
                lint = self._run_validation_command(info.lint_command)
                checks.append(f"lint: {info.lint_command}")
                if lint.returncode != 0:
                    errors.append(f"Lint failed: {info.lint_command}")
            if info.test_command:
                test = self._run_validation_command(info.test_command)
                checks.append(f"test: {info.test_command}")
                if test.returncode != 0:
                    errors.append(f"Tests failed: {info.test_command}")

        ok = not errors
        summary = "Validation passed." if ok else "Validation failed."
        result = ValidationResult(ok=ok, checks=checks, errors=errors, warnings=warnings, summary=summary)
        intent.validation = result
        return result

    def rollback_current_batch(self) -> List[str]:
        """Rollback the current edit batch."""
        intent = self._current_intent or self._last_intent
        if intent is None:
            return ["No active edit batch."]
        task_id = intent.task_id
        actions = self.edit_history.rollback_task(self.workspace_root, task_id)
        intent.rollback_actions = actions
        intent.status = "rolled_back"
        return actions

    def execute(self, name: str, kwargs: Dict[str, Any], fn: Callable[..., str]) -> str:
        block_reason = self._check_safety_mode(name, kwargs)
        if block_reason:
            return block_reason

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
            if self._require_approval_for_command(cmd):
                if not self._request_approval(f"Command: {cmd}", "<shell>", name):
                    return "Error: command rejected by user"

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

            self._track_edit_preview(path, diff)
            large_change = len((self._current_intent.paths if self._current_intent else [])) > 3 or len(diff) > 6000
            if self.approval_gate and not self.auto_approve and not self._approve_all:
                if large_change or self.safety_mode in {"workspace-write", "full-trusted"}:
                    if not self._request_approval(diff, path, name):
                        return "Error: change rejected by user"

            self.edit_history.snapshot_before(
                self.workspace_root,
                path,
                task_id=self._current_task_id,
            )

        result = fn(**kwargs)

        if name in ("write_file", "edit_file"):
            path = str(kwargs.get("path", ""))
            self._artifacts.append(
                ArtifactRecord(kind="file", path=path, description=name, metadata={"result": result[:240]})
            )
            validation = self.validate_current_batch()
            if not validation.ok:
                rollback = self.rollback_current_batch()
                return (
                    f"{result}\nValidation failed.\n"
                    + "\n".join(validation.errors[:10])
                    + "\nRollback:\n"
                    + "\n".join(rollback[:10])
                )

        if name == "run_command":
            cmd = str(kwargs.get("command", ""))
            self._commands.append(CommandRecord(command=cmd, returncode=0, output_preview=result[:500]))
            self._artifacts.append(
                ArtifactRecord(kind="command", command=cmd, description="user command", metadata={"output_preview": result[:240]})
            )

        if name in MUTATING_TOOLS:
            log_action(
                action=name,
                path=kwargs.get("path"),
                command=kwargs.get("command"),
                provider=self.provider,
                session_id=self.session_id,
            )
        return result
