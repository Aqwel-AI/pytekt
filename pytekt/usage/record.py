"""Record a single LLM call into the usage store."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence

from ..llm_eval.cost import estimate_cost
from .extract import estimate_tokens, extract_usage_from_response
from .store import UsageStore, default_store_path


def record_llm_call(
    *,
    provider: str,
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    source: str = "agent",
    raw_response: Optional[Dict[str, Any]] = None,
    messages: Optional[Sequence[Mapping[str, Any]]] = None,
    completion_text: str = "",
    store: Optional[UsageStore] = None,
) -> Dict[str, Any]:
    """
    Append one usage event. Fills token counts from *raw_response* or estimates.
    """
    if raw_response and (prompt_tokens == 0 and completion_tokens == 0):
        prompt_tokens, completion_tokens = extract_usage_from_response(raw_response)
    if (prompt_tokens == 0 and completion_tokens == 0) and messages is not None:
        prompt_tokens, completion_tokens = estimate_tokens(
            messages, completion_text, model=model
        )

    cost = estimate_cost(
        provider,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )

    event: Dict[str, Any] = {
        "provider": provider.lower(),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost_usd": cost["cost_usd"],
        "source": source,
    }
    (store or UsageStore()).append(event)
    return event
