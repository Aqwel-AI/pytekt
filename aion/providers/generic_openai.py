"""OpenAI-compatible HTTP servers (LM Studio, vLLM, Ollama OpenAI bridge, etc.)."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from .base import ChatMessage
from .http_utils import post_json
from .structured import AssistantTurn, parse_chat_completion_response

MessageInput = Union[ChatMessage, Mapping[str, Any]]


class OpenAICompatibleProvider:
    """
    Talk to any API that implements OpenAI-style ``POST .../chat/completions``.

    Parameters
    ----------
    base_url : str
        Base URL including ``/v1`` if the server uses that layout, e.g.
        ``http://localhost:1234/v1``.
    model : str
        Model name accepted by that server.
    api_key : str, optional
        Sent as ``Bearer`` if provided (many local servers ignore it).
    """

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: Optional[str] = None,
    ):
        self._base = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key

    @staticmethod
    def _messages_to_api(messages: Sequence[MessageInput]) -> List[Dict[str, Any]]:
        return [dict(m) for m in messages]

    def complete_turn(
        self,
        messages: Sequence[MessageInput],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> AssistantTurn:
        """OpenAI-compatible chat completion including optional tool calling."""
        url = f"{self._base}/chat/completions"
        payload: dict = {
            "model": self._model,
            "messages": self._messages_to_api(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        for k, v in kwargs.items():
            if k not in payload:
                payload[k] = v
        headers: Dict[str, str] = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        data = post_json(url, payload, headers=headers or None)
        self._last_raw_response = data  # type: ignore[attr-defined]
        return parse_chat_completion_response(data)

    def complete(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        url = f"{self._base}/chat/completions"
        payload: dict = {
            "model": self._model,
            "messages": list(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        payload.update(kwargs)
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        data = post_json(url, payload, headers=headers or None)
        self._last_raw_response = data  # type: ignore[attr-defined]
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Unexpected chat/completions response: {data!r}") from e
