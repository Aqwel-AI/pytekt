"""LLM-specific response cache (hash prompt+params, return cached completions)."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .core import Cache, DiskCache, MemoryCache


class LLMCache:
    """
    Cache LLM completions keyed by (messages, model, temperature, max_tokens).

    Supports both in-memory and disk-backed storage. Collects basic hit/miss
    statistics for cost-awareness.

    Parameters
    ----------
    backend : {"memory", "disk"} or a ``Cache`` instance
        Storage backend. ``"disk"`` creates a SQLite DB at *db_path*.
    db_path : str
        Path for disk backend (ignored for memory).
    default_ttl : int, optional
        Default time-to-live in seconds.
    """

    def __init__(
        self,
        backend: Any = "memory",
        *,
        db_path: str = ".aion_llm_cache.db",
        default_ttl: Optional[int] = None,
    ) -> None:
        if isinstance(backend, str):
            if backend == "disk":
                self._cache: Cache = DiskCache(db_path, default_ttl=default_ttl)
            else:
                self._cache = MemoryCache(default_ttl=default_ttl)
        else:
            self._cache = backend
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _make_key(
        messages: Sequence[Mapping[str, Any]],
        model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **extra: Any,
    ) -> str:
        payload = json.dumps(
            {"m": list(messages), "model": model, "t": temperature, "mt": max_tokens, **extra},
            sort_keys=True,
            default=str,
        )
        return f"llm:{hashlib.sha256(payload.encode()).hexdigest()}"

    def get(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **extra: Any,
    ) -> Optional[str]:
        """Return cached response text or ``None``."""
        key = self._make_key(messages, model, temperature, max_tokens, **extra)
        hit = self._cache.get(key)
        if hit is not None:
            self.hits += 1
            return hit.get("response") if isinstance(hit, dict) else hit
        self.misses += 1
        return None

    def put(
        self,
        messages: Sequence[Mapping[str, Any]],
        response: str,
        *,
        model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **extra: Any,
    ) -> None:
        """Store a completion response."""
        key = self._make_key(messages, model, temperature, max_tokens, **extra)
        entry = {
            "response": response,
            "model": model,
            "cached_at": time.time(),
            **(metadata or {}),
        }
        self._cache.set(key, entry, ttl=ttl)

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total else 0.0,
            "total_requests": total,
        }

    def clear(self) -> None:
        self._cache.clear()
        self.hits = 0
        self.misses = 0
