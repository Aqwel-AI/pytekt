"""Ollama local LLM provider (OpenAI-compatible API, no tool calling)."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import List, Optional

from .errors import ProviderError
from .generic_openai import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    """
    Local Ollama server via ``/v1/chat/completions``.

    Most Ollama models do not support OpenAI-style tool calling; this provider
    sets ``supports_tools = False`` so agents use plain chat completion.
    """

    supports_tools: bool = False

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11434/v1",
        model: str,
        api_key: Optional[str] = "ollama",
    ):
        super().__init__(base_url=base_url, model=model, api_key=api_key)
        self._host = base_url.rstrip("/").removesuffix("/v1") or "http://localhost:11434"

    @staticmethod
    def list_models(host: str = "http://localhost:11434", *, timeout: float = 5.0) -> List[str]:
        """Return installed model names from ``GET /api/tags``."""
        url = f"{host.rstrip('/')}/api/tags"
        req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            raise ProviderError(
                f"HTTP {e.code}: {e.reason}",
                status=e.code,
                body=body[:4000],
            ) from e
        except urllib.error.URLError as e:
            raise ProviderError(
                f"Cannot reach Ollama at {host}. Is it running? ({e.reason})"
            ) from e

        models = data.get("models") or []
        return [m["name"] for m in models if m.get("name")]
