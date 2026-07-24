"""NVIDIA NIM API (OpenAI-compatible chat/completions)."""

from __future__ import annotations

import os
from typing import Any, List, Optional, Sequence

from .base import ChatMessage
from .errors import ProviderError
from .generic_openai import OpenAICompatibleProvider
from .http_utils import get_json
from .structured import AssistantTurn

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"
DEFAULT_CHAT_TIMEOUT = 45.0

# Shown first in /connect nvidia — verified chat/completions models.
RECOMMENDED_CHAT_MODELS = [
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.3-70b-instruct",
    "nvidia/nemotron-mini-4b-instruct",
    "mistralai/mistral-7b-instruct-v0.3",
    "google/gemma-2-9b-it",
    "deepseek-ai/deepseek-v4-flash",
]

POPULAR_MODELS = list(RECOMMENDED_CHAT_MODELS)

# Models that appear in /v1/models but hang or fail on chat/completions.
_CHAT_BLOCKLIST = frozenset({
    "nvidia/llama-3.1-nemotron-nano-8b-v1",
})

_NON_CHAT_MARKERS = (
    "/embed",
    "embed-",
    "-embed",
    "embedding",
    "rerank",
    "detector",
    "translate",
    "/parse",
    "nvclip",
    "/vila",
    "deplot",
    "/fuyu-",
    "kosmos-2",
    "diffusiongemma",
    "-reward",
    "calibration",
    "synthetic-video",
    "gliner",
    "content-safety",
    "topic-control",
    "safety-guard",
    "nemoguard",
    "arctic-embed",
    "bge-m3",
    "nv-embed",
    "nemoretriever",
    "nemotron-parse",
    "nemotron-4-340b-reward",
)


def is_chat_model(model_id: str) -> bool:
    """Heuristic: keep instruct/chat LLMs, drop embeddings and utilities."""
    mid = model_id.lower()
    if model_id in _CHAT_BLOCKLIST:
        return False
    if any(marker in mid for marker in _NON_CHAT_MARKERS):
        return False
    chat_hints = (
        "instruct",
        "chat",
        "gpt-oss",
        "deepseek-v",
        "kimi-",
        "glm-",
        "qwen",
        "mistral",
        "mixtral",
        "dbrx",
        "codestral",
        "llama",
        "gemma",
        "phi-",
        "granite",
        "solar",
        "yi-large",
        "jamba",
        "seed-oss",
        "starcoder",
        "codellama",
        "dracarys",
        "minimax",
        "step-",
        "palmyra",
        "zamba",
        "stockmark",
        "sarvam",
        "nemotron",
    )
    return any(hint in mid for hint in chat_hints)


def prioritize_chat_models(models: List[str]) -> List[str]:
    """Recommended chat models first, then the rest alphabetically."""
    available = set(models)
    head = [m for m in RECOMMENDED_CHAT_MODELS if m in available]
    tail = sorted(m for m in available if m not in head)
    return head + tail


def filter_chat_models(models: List[str]) -> List[str]:
    """Return chat-capable models, falling back to the raw list only if none match."""
    chat = [m for m in models if is_chat_model(m)]
    if chat:
        return prioritize_chat_models(chat)
    if models:
        return prioritize_chat_models(models)
    return list(POPULAR_MODELS)


class NvidiaProvider(OpenAICompatibleProvider):
    """
    Chat via NVIDIA NIM's OpenAI-compatible API.

    Parameters
    ----------
    api_key : str, optional
        Defaults to ``NVIDIA_API_KEY``.
    model : str, optional
        Default ``meta/llama-3.1-8b-instruct``. Use full ids from ``list_models()``.
    base_url : str, optional
        Default ``https://integrate.api.nvidia.com/v1``.
    """

    supports_tools: bool = True

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = NVIDIA_BASE_URL,
    ):
        key = api_key or os.environ.get("NVIDIA_API_KEY")
        if not key:
            raise ValueError(
                "NvidiaProvider requires api_key or NVIDIA_API_KEY environment variable"
            )
        super().__init__(base_url=base_url.rstrip("/"), model=model, api_key=key)

    def complete(
        self,
        messages: List[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: float = DEFAULT_CHAT_TIMEOUT,
        **kwargs: Any,
    ) -> str:
        return super().complete(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            **kwargs,
        )

    def complete_turn(
        self,
        messages: Sequence[Any],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Optional[List[dict]] = None,
        tool_choice: Any = None,
        timeout: float = DEFAULT_CHAT_TIMEOUT,
        **kwargs: Any,
    ) -> AssistantTurn:
        return super().complete_turn(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            timeout=timeout,
            **kwargs,
        )

    @staticmethod
    def list_models(
        *,
        api_key: Optional[str] = None,
        base_url: str = NVIDIA_BASE_URL,
        timeout: float = 15.0,
    ) -> List[str]:
        """Return chat model ids from ``GET /v1/models``."""
        key = api_key or os.environ.get("NVIDIA_API_KEY")
        if not key:
            raise ValueError(
                "list_models requires api_key or NVIDIA_API_KEY environment variable"
            )
        url = f"{base_url.rstrip('/')}/models"
        headers = {"Authorization": f"Bearer {key}"}
        try:
            data = get_json(url, headers=headers, timeout=timeout)
        except ProviderError as e:
            raise ProviderError(
                f"Cannot reach NVIDIA NIM at {base_url}. ({e})",
                status=e.status,
                body=e.body,
            ) from e

        items = data.get("data") or []
        models = [m["id"] for m in items if isinstance(m, dict) and m.get("id")]
        if models:
            return filter_chat_models(models)
        return list(POPULAR_MODELS)
