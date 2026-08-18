"""Optional token counting via tiktoken (install pytekt[tools])."""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Sequence

try:
    import tiktoken  # type: ignore[import-not-found]
except ImportError:
    tiktoken = None


def estimate_text_tokens_openai(text: str, model: str = "gpt-4o-mini") -> Optional[int]:
    """
    Return token count for ``text`` using tiktoken, or ``None`` if unavailable.

    Encoding falls back to ``cl100k_base`` when the model name is unknown.
    """
    if tiktoken is None:
        return None
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


MessageLike = Mapping[str, Any]


def estimate_messages_tokens_openai(
    messages: Sequence[MessageLike],
    model: str = "gpt-4o-mini",
) -> Optional[int]:
    """
    Rough token estimate over message contents (concatenated); not a full
    chat-template count. Returns ``None`` if tiktoken is not installed.
    """
    if tiktoken is None:
        return None
    parts: List[str] = []
    for m in messages:
        role = str(m.get("role", ""))
        content = m.get("content")
        if content is None:
            parts.append(role)
        elif isinstance(content, str):
            parts.append(f"{role}\n{content}")
        else:
            parts.append(f"{role}\n{content!s}")
    return estimate_text_tokens_openai("\n\n".join(parts), model=model)
