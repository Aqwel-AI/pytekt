"""
Undo manager for PyTekt Agent file modifications.
Tracks file mutations made by the agent and supports step-by-step rollback.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FileSnapshot:
    rel_path: str
    abs_path: str
    content_before: Optional[str]  # None if file did not exist before
    action: str  # "edit" or "write"


class UndoManager:
    """Tracks file mutations made by the agent and supports step-by-step rollback."""

    def __init__(self) -> None:
        self._stack: List[FileSnapshot] = []

    def record_edit(self, rel_path: str, abs_path: str, content_before: str) -> None:
        """Record a file modification snapshot."""
        self._stack.append(
            FileSnapshot(
                rel_path=rel_path,
                abs_path=abs_path,
                content_before=content_before,
                action="edit",
            )
        )

    def record_write(
        self, rel_path: str, abs_path: str, content_before: Optional[str]
    ) -> None:
        """Record a file creation or overwrite snapshot."""
        self._stack.append(
            FileSnapshot(
                rel_path=rel_path,
                abs_path=abs_path,
                content_before=content_before,
                action="write",
            )
        )

    @property
    def history_count(self) -> int:
        """Number of recoverable actions in the stack."""
        return len(self._stack)

    def can_undo(self) -> bool:
        """Return True if an undoable snapshot exists."""
        return len(self._stack) > 0

    def undo_last(self) -> str:
        """Revert the most recent file modification."""
        if not self._stack:
            return "Nothing to undo."
        snap = self._stack.pop()
        try:
            if snap.content_before is None:
                # File was created new by agent; undo removes it
                if os.path.exists(snap.abs_path):
                    os.remove(snap.abs_path)
                    return f"Reverted creation of {snap.rel_path} (file removed)."
                return f"File {snap.rel_path} was already deleted."
            else:
                # Revert to previous content
                with open(snap.abs_path, "w", encoding="utf-8") as f:
                    f.write(snap.content_before)
                return f"Reverted {snap.rel_path} to previous version."
        except Exception as e:
            return f"Failed to undo {snap.rel_path}: {e}"

    def clear(self) -> None:
        """Clear the undo history."""
        self._stack.clear()


# Global or session-level singleton
undo_manager = UndoManager()
