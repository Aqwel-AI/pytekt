"""Anthropic Messages API (REST)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from .base import ChatMessage
from .http_utils import post_json
from .structured import AssistantTurn, NormalizedToolCall

MessageInput = Union[ChatMessage, Mapping[str, Any]]


def _openai_tools_to_anthropic(tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
    if not tools:
        return None
    out: List[Dict[str, Any]] = []
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        fn = tool.get("function") if tool.get("type") == "function" else tool
        if not isinstance(fn, dict):
            continue
        name = fn.get("name")
        if not name:
            continue
        params = fn.get("parameters") or fn.get("input_schema") or {"type": "object", "properties": {}}
        entry: Dict[str, Any] = {
            "name": str(name),
            "input_schema": params if isinstance(params, dict) else {"type": "object", "properties": {}},
        }
        desc = fn.get("description")
        if desc:
            entry["description"] = str(desc)
        out.append(entry)
    return out or None


def _openai_messages_to_anthropic(
    messages: Sequence[MessageInput],
) -> tuple[Optional[str], List[dict]]:
    system_chunks: List[str] = []
    api_messages: List[dict] = []

    for m in messages:
        msg = dict(m)
        role = msg.get("role", "")
        content = msg.get("content")

        if role == "system":
            if content:
                system_chunks.append(str(content))
            continue

        if role == "tool":
            tool_result = {
                "type": "tool_result",
                "tool_use_id": str(msg.get("tool_call_id") or ""),
                "content": str(content or ""),
            }
            if api_messages and api_messages[-1].get("role") == "user" and isinstance(
                api_messages[-1].get("content"), list
            ):
                api_messages[-1]["content"].append(tool_result)
            else:
                api_messages.append({"role": "user", "content": [tool_result]})
            continue

        if role == "assistant":
            blocks: List[dict] = []
            if content:
                blocks.append({"type": "text", "text": str(content)})
            for tc in msg.get("tool_calls") or []:
                if not isinstance(tc, dict):
                    continue
                fn = tc.get("function") or {}
                raw_args = fn.get("arguments") if isinstance(fn, dict) else "{}"
                try:
                    parsed = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                except (json.JSONDecodeError, TypeError):
                    parsed = {}
                if not isinstance(parsed, dict):
                    parsed = {}
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": str(tc.get("id") or ""),
                        "name": str((fn or {}).get("name") or ""),
                        "input": parsed,
                    }
                )
            api_messages.append({"role": "assistant", "content": blocks or [{"type": "text", "text": ""}]})
            continue

        if role == "user":
            api_messages.append({"role": "user", "content": str(content or "")})
            continue

    system = "\n\n".join(system_chunks) if system_chunks else None
    return system, api_messages


def _parse_anthropic_response(data: Dict[str, Any]) -> AssistantTurn:
    blocks = data.get("content") or []
    text_parts: List[str] = []
    tool_calls: List[NormalizedToolCall] = []
    if isinstance(blocks, list):
        for block in blocks:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                text_parts.append(str(block.get("text") or ""))
            elif btype == "tool_use":
                args = block.get("input")
                args_json = json.dumps(args if isinstance(args, dict) else {})
                tool_calls.append(
                    NormalizedToolCall(
                        id=str(block.get("id") or ""),
                        name=str(block.get("name") or ""),
                        arguments_json=args_json,
                    )
                )
    content = "".join(text_parts) if text_parts else None
    return AssistantTurn(content=content, tool_calls=tool_calls, raw=dict(data))


class AnthropicProvider:
    """
    Chat via Anthropic ``/v1/messages``.

    Parameters
    ----------
    api_key : str, optional
        Defaults to ``ANTHROPIC_API_KEY``.
    model : str, optional
        Default ``claude-3-5-sonnet-20241022`` (adjust if your account uses another id).
    """

    supports_tools: bool = True

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
    ):
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("AnthropicProvider requires api_key or ANTHROPIC_API_KEY")
        self._api_key = key
        self._model = model

    def complete_turn(
        self,
        messages: Sequence[MessageInput],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Any = None,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> AssistantTurn:
        system, api_messages = _openai_messages_to_anthropic(messages)
        if not api_messages:
            api_messages = [{"role": "user", "content": "Hello"}]

        url = "https://api.anthropic.com/v1/messages"
        payload: dict = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        if system:
            payload["system"] = system
        anthropic_tools = _openai_tools_to_anthropic(tools if isinstance(tools, list) else None)
        if anthropic_tools:
            payload["tools"] = anthropic_tools
            if tool_choice == "auto" or tool_choice is None:
                payload["tool_choice"] = {"type": "auto"}
            elif tool_choice == "none":
                payload["tool_choice"] = {"type": "none"}
            elif isinstance(tool_choice, dict):
                payload["tool_choice"] = tool_choice
        for k, v in kwargs.items():
            if k not in payload:
                payload[k] = v

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
        }
        data = post_json(url, payload, headers=headers)
        self._last_raw_response = data  # type: ignore[attr-defined]
        return _parse_anthropic_response(data)

    def complete(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        turn = self.complete_turn(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=None,
            **kwargs,
        )
        return turn.content or ""
