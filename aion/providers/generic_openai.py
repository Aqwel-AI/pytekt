"""OpenAI-compatible HTTP servers (LM Studio, vLLM, Ollama OpenAI bridge, etc.)."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Union

from .base import ChatMessage
from .http_utils import post_json, ssl_context
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
        timeout: float = 120.0,
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
        if tools:
            payload["tools"] = tools
        if tool_choice is not None and tools:
            payload["tool_choice"] = tool_choice
        for k, v in kwargs.items():
            if k not in payload:
                payload[k] = v
        headers: Dict[str, str] = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        data = post_json(url, payload, headers=headers or None, timeout=timeout)
        self._last_raw_response = data  # type: ignore[attr-defined]
        return parse_chat_completion_response(data)

    def complete(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: float = 120.0,
        **kwargs: Any,
    ) -> str:
        url = f"{self._base}/chat/completions"
        payload: dict = {
            "model": self._model,
            "messages": list(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        extra = dict(kwargs)
        extra.pop("timeout", None)
        payload.update(extra)
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        data = post_json(url, payload, headers=headers or None, timeout=timeout)
        self._last_raw_response = data  # type: ignore[attr-defined]
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Unexpected chat/completions response: {data!r}") from e

    def complete_stream(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: float = 120.0,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream chat completion tokens (SSE ``data:`` lines)."""
        import json
        import urllib.request

        url = f"{self._base}/chat/completions"
        payload: dict = {
            "model": self._model,
            "messages": list(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        payload.update(kwargs)
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                chunk = line[5:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                except json.JSONDecodeError:
                    continue
                choices = data.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                text = delta.get("content")
                if text:
                    yield text
