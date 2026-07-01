"""Checkpoint persistence for agent state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .state import AgentState


PathLike = Union[str, Path]


def save_checkpoint(state: AgentState, path: PathLike) -> Path:
    """Write one agent-state checkpoint to disk as JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
    return target


def load_checkpoint(path: PathLike) -> AgentState:
    """Load an agent-state checkpoint from disk."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return AgentState.from_dict(data)
