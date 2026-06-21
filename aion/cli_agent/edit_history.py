"""Edit snapshots and /undo support."""

from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def _snapshot_dir(session_id: str) -> Path:
    base = Path.home() / ".aion" / "edit_snapshots" / session_id
    base.mkdir(parents=True, exist_ok=True)
    return base


@dataclass
class SnapshotEntry:
    path: str
    snapshot_id: str
    existed: bool


class EditHistory:
    """Stack of file snapshots per session."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self._stack: List[SnapshotEntry] = []

    def snapshot_before(self, workspace_root: str, rel_path: str) -> Optional[str]:
        root = Path(workspace_root)
        target = (root / rel_path).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            return None

        snap_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        snap_path = _snapshot_dir(self.session_id) / f"{snap_id}.bin"
        existed = target.is_file()
        if existed:
            shutil.copy2(target, snap_path)
        else:
            snap_path.write_bytes(b"")
        self._stack.append(SnapshotEntry(path=rel_path, snapshot_id=snap_id, existed=existed))
        return snap_id

    def undo_last(self, workspace_root: str) -> str:
        if not self._stack:
            return "Nothing to undo."
        entry = self._stack.pop()
        snap_path = _snapshot_dir(self.session_id) / f"{entry.snapshot_id}.bin"
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

    @property
    def count(self) -> int:
        return len(self._stack)
