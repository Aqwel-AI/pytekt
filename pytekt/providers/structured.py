"""Structured chat completion parsing (OpenAI-style /chat/completions)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class NormalizedToolCall:
    """One tool invocation returned by the assistant."""

    id: str
    name: str
    arguments_json: str


@dataclass
class AssistantTurn:
    """Parsed assistant message from a chat completion response."""

    content: Optional[str]
    tool_calls: List[NormalizedToolCall] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


def parse_chat_completion_response(data: Dict[str, Any]) -> AssistantTurn:
    """
    Parse OpenAI-style ``chat/completions`` JSON into AssistantTurn.

    Handles ``content`` being null when the model returns only ``tool_calls``.
    """
    raw = dict(data)
    try:
        choice = data["choices"][0]
        msg = choice["message"]
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Unexpected chat completion shape: {data!r}") from e

    content = msg.get("content")
    if content is not None and not isinstance(content, str):
        content = str(content)

    tool_calls: List[NormalizedToolCall] = []
    raw_tool_calls = msg.get("tool_calls")
    if isinstance(raw_tool_calls, list):
        for tc in raw_tool_calls:
            if not isinstance(tc, dict):
                continue
            tc_id = str(tc.get("id", ""))
            fn = tc.get("function")
            if not isinstance(fn, dict):
                continue
            name = str(fn.get("name", ""))
            args = fn.get("arguments")
            args_str = args if isinstance(args, str) else (
                "" if args is None else str(args)
            )
            tool_calls.append(
                NormalizedToolCall(id=tc_id, name=name, arguments_json=args_str)
            )

    return AssistantTurn(content=content, tool_calls=tool_calls, raw=raw)
