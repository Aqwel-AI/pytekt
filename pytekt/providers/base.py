"""Shared types and protocol for chat providers."""

from __future__ import annotations

from typing import Any, Dict, List, Protocol, TypedDict, runtime_checkable


class ChatMessage(TypedDict):
    """One message in a chat history."""

    role: str  # "system" | "user" | "assistant"
    content: str


@runtime_checkable
class ChatProvider(Protocol):
    """
    Minimal interface: send messages, get assistant text back.

    Implementations call vendor HTTP APIs (OpenAI, Gemini, Anthropic, …).
    """

    def complete(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> str:
        """Return the model's reply as plain text."""
        ...
