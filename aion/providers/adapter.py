"""Unified provider abstraction for streaming, tool support, and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, Iterator, List, Optional

from .base import ChatMessage


@dataclass
class ProviderCapabilities:
    supports_tools: bool = False
    supports_streaming: bool = False
    provider_name: str = ""
    model: str = ""


class ProviderAdapter:
    """Normalize provider capabilities across Nvidia, Ollama, and compatible backends."""

    def __init__(self, provider: Any, *, provider_name: str, model: str) -> None:
        self.provider = provider
        self.provider_name = provider_name
        self.model = model
        inner = getattr(provider, "_inner", provider)
        self.capabilities = ProviderCapabilities(
            supports_tools=bool(getattr(provider, "supports_tools", getattr(inner, "supports_tools", False))),
            supports_streaming=hasattr(inner, "complete_stream"),
            provider_name=provider_name,
            model=model,
        )

    def stream(self, messages: List[ChatMessage], *, max_tokens: int = 4096) -> Iterator[str]:
        """Yield streamed tokens when the provider supports it."""
        inner = getattr(self.provider, "_inner", self.provider)
        if hasattr(inner, "complete_stream"):
            yield from inner.complete_stream(messages, max_tokens=max_tokens)
            return
        text = self.provider.complete(messages, max_tokens=max_tokens)
        yield text

    def metadata(self) -> Dict[str, Any]:
        """Return provider metadata for the runtime/UI."""
        return {
            "provider": self.provider_name,
            "model": self.model,
            "supports_tools": self.capabilities.supports_tools,
            "supports_streaming": self.capabilities.supports_streaming,
        }

    def healthcheck(self) -> bool:
        """Best-effort provider health check."""
        try:
            self.provider.complete([ChatMessage(role="user", content="Say ok.")], max_tokens=8, temperature=0)
            return True
        except Exception:
            return False


@lru_cache(maxsize=128)
def cached_model_metadata(provider_name: str, model: str) -> Dict[str, str]:
    """Small metadata cache keyed by provider and model."""
    lower = model.casefold()
    family = "general"
    if "llama" in lower:
        family = "llama"
    elif "gemma" in lower:
        family = "gemma"
    elif "mistral" in lower:
        family = "mistral"
    elif "qwen" in lower:
        family = "qwen"
    return {"provider": provider_name, "model": model, "family": family}
