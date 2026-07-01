"""Retry helpers for provider or tool execution."""

from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Callable, Iterable, Optional, TypeVar


T = TypeVar("T")


@dataclass
class RetryConfig:
    """Retry policy for fragile operations."""

    attempts: int = 3
    backoff_seconds: float = 0.0
    retry_on_substrings: tuple[str, ...] = ("timeout", "temporarily", "rate limit")


def retry_call(
    fn: Callable[[], T],
    *,
    config: Optional[RetryConfig] = None,
    fallback: Optional[Callable[[], T]] = None,
) -> T:
    """Retry a callable with simple substring-based transient-error detection."""
    cfg = config or RetryConfig()
    last_exc: Optional[Exception] = None
    for attempt in range(cfg.attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            message = str(exc).casefold()
            transient = any(token in message for token in cfg.retry_on_substrings)
            if not transient or attempt == cfg.attempts - 1:
                break
            if cfg.backoff_seconds > 0:
                sleep(cfg.backoff_seconds * (attempt + 1))
    if fallback is not None:
        return fallback()
    assert last_exc is not None
    raise last_exc
