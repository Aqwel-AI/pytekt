"""Wrap chat providers to record token usage automatically."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from .record import record_llm_call


class UsageTrackingProvider:
    """
    Transparent wrapper: delegates to an inner provider and logs each call.
    """

    def __init__(
        self,
        inner: Any,
        *,
        provider: str,
        model: str,
        source: str = "agent",
    ) -> None:
        self._inner = inner
        self._provider = provider
        self._model = model
        self._source = source
        for attr in ("supports_tools",):
            if hasattr(inner, attr):
                setattr(self, attr, getattr(inner, attr))

    def complete(
        self,
        messages: List[Any],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        text = self._inner.complete(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        raw = getattr(self._inner, "_last_raw_response", None)
        record_llm_call(
            provider=self._provider,
            model=self._model,
            source=self._source,
            raw_response=raw if isinstance(raw, dict) else None,
            messages=messages,
            completion_text=text,
        )
        return text

    def complete_turn(
        self,
        messages: Sequence[Any],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> Any:
        turn = self._inner.complete_turn(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs,
        )
        raw = getattr(turn, "raw", None) or {}
        content = getattr(turn, "content", None) or ""
        record_llm_call(
            provider=self._provider,
            model=self._model,
            source=self._source,
            raw_response=raw if isinstance(raw, dict) else None,
            messages=messages,
            completion_text=str(content),
        )
        return turn


def wrap_provider_with_usage(
    provider: Any,
    *,
    provider_name: str,
    model: str,
    source: str = "agent",
) -> UsageTrackingProvider:
    """Return a usage-logging wrapper around *provider*."""
    return UsageTrackingProvider(
        provider,
        provider=provider_name,
        model=model,
        source=source,
    )
