"""Multi-turn tool-calling loop (OpenAI chat/completions shape)."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence, Tuple

from ..providers.structured import AssistantTurn, NormalizedToolCall


class SupportsCompleteTurn(Protocol):
    """Provider with OpenAI-style ``complete_turn``."""

    def complete_turn(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> AssistantTurn:
        ...


def tool_calls_to_message_payload(tool_calls: List[NormalizedToolCall]) -> List[Dict[str, Any]]:
    """Build ``tool_calls`` array for an assistant message in the chat API."""
    out: List[Dict[str, Any]] = []
    for tc in tool_calls:
        out.append(
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.name, "arguments": tc.arguments_json},
            }
        )
    return out


def run_tool_loop(
    provider: SupportsCompleteTurn,
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]],
    registry: Any,
    *,
    max_rounds: int = 8,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    **complete_kw: Any,
) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Run chat completions until the assistant returns text (no tool_calls) or
    ``max_rounds`` is exceeded.

    Parameters
    ----------
    provider
        ``OpenAIProvider`` or ``OpenAICompatibleProvider``.
    messages
        Mutable list of chat API messages (dicts); updated in place.
    tools
        OpenAI ``tools`` array (from ``aion.tools.schemas.function_tool``).
    registry
        ``ToolRegistry`` with registered implementations.

    Returns
    -------
    final_text, messages
        Assistant text (or None if only tools ran and rounds exhausted) and
        the full message list for follow-up turns.

    Raises
    ------
    RuntimeError
        If ``max_rounds`` is hit while the model still requests tools.
    """
    msgs = messages
    for _ in range(max_rounds):
        turn = provider.complete_turn(
            msgs,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            **complete_kw,
        )
        if turn.tool_calls:
            asst: Dict[str, Any] = {"role": "assistant", "content": turn.content}
            asst["tool_calls"] = tool_calls_to_message_payload(turn.tool_calls)
            msgs.append(asst)
            for tc in turn.tool_calls:
                content = registry.call(tc.name, tc.arguments_json)
                msgs.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": content,
                    }
                )
            continue
        if turn.content is not None:
            msgs.append({"role": "assistant", "content": turn.content})
        return turn.content, msgs
    raise RuntimeError(
        f"run_tool_loop exceeded max_rounds={max_rounds} with pending tool calls"
    )
