"""LLM cost estimation and tracking."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

# Local / self-hosted — no cloud API billing.
_FREE_LOCAL_PROVIDERS = frozenset({"ollama", "local", "localhost"})

# Approximate per-1K-token cloud pricing (USD) — not your real invoice.
_PRICING: Dict[str, Dict[str, float]] = {
    "ollama": {"prompt": 0.0, "completion": 0.0},
    "local": {"prompt": 0.0, "completion": 0.0},
    "openai": {"prompt": 0.0005, "completion": 0.0015},
    "openai-gpt4": {"prompt": 0.03, "completion": 0.06},
    "openai-gpt4o": {"prompt": 0.005, "completion": 0.015},
    "anthropic": {"prompt": 0.008, "completion": 0.024},
    "anthropic-haiku": {"prompt": 0.00025, "completion": 0.00125},
    "gemini": {"prompt": 0.00025, "completion": 0.0005},
    "gemini-pro": {"prompt": 0.00125, "completion": 0.005},
    "deepseek": {"prompt": 0.00014, "completion": 0.00028},
    "deepseek-chat": {"prompt": 0.00014, "completion": 0.00028},
}


def estimate_cost(
    provider: str,
    *,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
) -> Dict[str, Any]:
    """
    Estimate the cost of an LLM call in USD.

    Parameters
    ----------
    provider : str
        Provider key (e.g. ``"openai"``, ``"anthropic"``, ``"gemini"``).
    prompt_tokens, completion_tokens : int
        Token counts.

    Returns
    -------
    dict
        ``cost_usd``, ``prompt_cost``, ``completion_cost``, breakdown.
    """
    key = provider.lower().strip()
    if key in _FREE_LOCAL_PROVIDERS or key.startswith("ollama"):
        pricing = {"prompt": 0.0, "completion": 0.0}
    elif key in ("google", "gemini"):
        pricing = _PRICING.get("gemini", {"prompt": 0.00025, "completion": 0.0005})
    elif key in ("claude", "anthropic"):
        pricing = _PRICING.get("anthropic", {"prompt": 0.008, "completion": 0.024})
    else:
        pricing = _PRICING.get(key, {"prompt": 0.001, "completion": 0.002})
    p_cost = (prompt_tokens / 1000) * pricing["prompt"]
    c_cost = (completion_tokens / 1000) * pricing["completion"]
    return {
        "provider": provider,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "prompt_cost_usd": round(p_cost, 6),
        "completion_cost_usd": round(c_cost, 6),
        "cost_usd": round(p_cost + c_cost, 6),
    }


class CostTracker:
    """
    Accumulate LLM usage and cost across multiple calls.

    >>> tracker = CostTracker()
    >>> tracker.record("openai", prompt_tokens=1000, completion_tokens=500)
    >>> tracker.total_cost_usd
    0.00125
    """

    def __init__(self) -> None:
        self._records: List[Dict[str, Any]] = []

    def record(
        self,
        provider: str,
        *,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record a single LLM call."""
        est = estimate_cost(provider, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
        entry = {**est, "timestamp": time.time(), **(metadata or {})}
        self._records.append(entry)
        return entry

    @property
    def total_cost_usd(self) -> float:
        return sum(r.get("cost_usd", 0) for r in self._records)

    @property
    def total_tokens(self) -> int:
        return sum(
            r.get("prompt_tokens", 0) + r.get("completion_tokens", 0)
            for r in self._records
        )

    @property
    def call_count(self) -> int:
        return len(self._records)

    def summary(self) -> Dict[str, Any]:
        by_provider: Dict[str, float] = {}
        for r in self._records:
            prov = r.get("provider", "unknown")
            by_provider[prov] = by_provider.get(prov, 0) + r.get("cost_usd", 0)
        return {
            "total_cost_usd": round(self.total_cost_usd, 6),
            "total_tokens": self.total_tokens,
            "call_count": self.call_count,
            "by_provider": {k: round(v, 6) for k, v in by_provider.items()},
        }

    def reset(self) -> None:
        self._records.clear()
