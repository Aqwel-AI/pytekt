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
    tools: Optional[List[Dict[str, Any]]],
    registry: Any,
    *,
    max_rounds: int = 8,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    on_tool_call: Optional[Any] = None,
    on_tool_result: Optional[Any] = None,
    **complete_kw: Any,
) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Run chat completions until the assistant returns text (no tool_calls) or
    ``max_rounds`` is exceeded.
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
                parsed_args: Dict[str, Any] = {}
                try:
                    import json
                    if isinstance(tc.arguments_json, str):
                        parsed_args = json.loads(tc.arguments_json)
                    elif isinstance(tc.arguments_json, dict):
                        parsed_args = tc.arguments_json
                except Exception:
                    pass

                if on_tool_call is not None:
                    try:
                        on_tool_call(tc.name, parsed_args)
                    except Exception:
                        pass

                content = registry.call(tc.name, tc.arguments_json)

                if on_tool_result is not None:
                    try:
                        on_tool_result(tc.name, content, parsed_args)
                    except Exception:
                        try:
                            on_tool_result(tc.name, content)
                        except Exception:
                            pass

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
