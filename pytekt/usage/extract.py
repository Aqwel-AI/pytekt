"""Extract token counts from provider API responses or estimate from text."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


def extract_usage_from_response(data: Dict[str, Any]) -> Tuple[int, int]:
    """
    Return ``(prompt_tokens, completion_tokens)`` from a vendor JSON body.

    Supports OpenAI-style ``usage``, Gemini ``usageMetadata``, and Ollama eval counts.
    """
    if not isinstance(data, dict):
        return 0, 0

    usage = data.get("usage")
    if isinstance(usage, dict):
        return (
            int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0),
            int(usage.get("completion_tokens") or usage.get("output_tokens") or 0),
        )

    meta = data.get("usageMetadata")
    if isinstance(meta, dict):
        return (
            int(meta.get("promptTokenCount") or 0),
            int(meta.get("candidatesTokenCount") or meta.get("totalTokenCount") or 0),
        )

    prompt_eval = data.get("prompt_eval_count")
    eval_count = data.get("eval_count")
    if prompt_eval is not None or eval_count is not None:
        return int(prompt_eval or 0), int(eval_count or 0)

    return 0, 0


def _text_from_messages(messages: Sequence[Mapping[str, Any]]) -> str:
    parts: List[str] = []
    for m in messages:
        role = str(m.get("role", ""))
        content = m.get("content")
        if content is None:
            continue
        if isinstance(content, str):
            parts.append(f"{role}\n{content}")
        else:
            parts.append(f"{role}\n{content!s}")
    return "\n\n".join(parts)


def estimate_tokens(
    messages: Sequence[Mapping[str, Any]],
    completion_text: str,
    *,
    model: str = "gpt-4o-mini",
) -> Tuple[int, int]:
    """Estimate prompt and completion tokens when the API omits usage."""
    prompt_text = _text_from_messages(messages)
    try:
        from ..tools.tokens import estimate_text_tokens_openai

        p = estimate_text_tokens_openai(prompt_text, model=model)
        c = estimate_text_tokens_openai(completion_text or "", model=model)
        if p is not None and c is not None:
            return p, c
    except Exception:
        pass
    return max(1, len(prompt_text) // 4), max(0, len(completion_text or "") // 4)
