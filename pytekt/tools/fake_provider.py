"""Scripted provider for offline demos and tests (no HTTP)."""

from __future__ import annotations

import tempfile
from typing import Any, Dict, List, Optional, Sequence

from ..providers.structured import AssistantTurn, NormalizedToolCall


class FakeToolProvider:
    """Returns scripted ``AssistantTurn`` instances in order."""

    def __init__(self, turns: Sequence[AssistantTurn]) -> None:
        self._turns = list(turns)
        self._i = 0

    def complete_turn(
        self,
        messages: Sequence[Dict[str, Any]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> AssistantTurn:
        if self._i >= len(self._turns):
            return AssistantTurn(content="done", tool_calls=[], raw={})
        t = self._turns[self._i]
        self._i += 1
        return t


def temp_dir_context():
    """Return a ``tempfile.TemporaryDirectory`` context manager."""
    return tempfile.TemporaryDirectory()


def make_tool_turn(
    tool_calls: List[NormalizedToolCall],
    content: Optional[str] = None,
) -> AssistantTurn:
    return AssistantTurn(content=content, tool_calls=list(tool_calls), raw={})
