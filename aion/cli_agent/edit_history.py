"""Edit snapshots, batch rollback, and /undo support."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def _default_state_base() -> Path:
    """Pick a writable state directory without relying on the user's home dir."""
    env = os.environ.get("AION_STATE_DIR")
    if env:
        base = Path(env)
    else:
        base = Path.cwd() / ".aion"
    base.mkdir(parents=True, exist_ok=True)
    return base


@dataclass
class SnapshotEntry:
    path: str
    snapshot_id: str
    existed: bool
    task_id: Optional[str] = None


class EditHistory:
    """Stack of file snapshots per session with task-level rollback."""

    def __init__(self, session_id: str, *, base_dir: Optional[str] = None) -> None:
        self.session_id = session_id
        self.base_dir = Path(base_dir).resolve() if base_dir else _default_state_base() / "edit_snapshots"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._stack: List[SnapshotEntry] = []

    def _snapshot_dir(self) -> Path:
        path = self.base_dir / self.session_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def snapshot_before(self, workspace_root: str, rel_path: str, *, task_id: Optional[str] = None) -> Optional[str]:
        root = Path(workspace_root).resolve()
        target = (root / rel_path).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            return None

        snap_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        snap_path = self._snapshot_dir() / f"{snap_id}.bin"
        existed = target.is_file()
        if existed:
            shutil.copy2(target, snap_path)
        else:
            snap_path.write_bytes(b"")
        self._stack.append(
            SnapshotEntry(path=rel_path, snapshot_id=snap_id, existed=existed, task_id=task_id)
        )
        return snap_id

    def _restore_entry(self, workspace_root: str, entry: SnapshotEntry) -> str:
        snap_path = self._snapshot_dir() / f"{entry.snapshot_id}.bin"
        target = Path(workspace_root) / entry.path
        if entry.existed:
            if not snap_path.is_file():
                return f"Snapshot missing for {entry.path}"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(snap_path, target)
            return f"Restored {entry.path}"
        if target.is_file():
            target.unlink()
            return f"Removed {entry.path} (was created)"
        return f"No change for {entry.path}"

    def undo_last(self, workspace_root: str) -> str:
        if not self._stack:
            return "Nothing to undo."
        entry = self._stack.pop()
        return self._restore_entry(workspace_root, entry)

    def rollback_task(self, workspace_root: str, task_id: str) -> List[str]:
        """Rollback all snapshots recorded for a task, newest first."""
        remaining: List[SnapshotEntry] = []
        to_restore: List[SnapshotEntry] = []
        for entry in self._stack:
            if entry.task_id == task_id:
                to_restore.append(entry)
            else:
                remaining.append(entry)
        self._stack = remaining
        results: List[str] = []
        for entry in reversed(to_restore):
            results.append(self._restore_entry(workspace_root, entry))
        return results

    @property
    def count(self) -> int:
        return len(self._stack)
