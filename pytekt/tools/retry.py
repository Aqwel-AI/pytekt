"""Retry wrapper for provider HTTP calls (429 / transient 5xx)."""

from __future__ import annotations

import random
import time
from typing import Any, Callable, Dict, Optional, TypeVar

from ..providers.errors import ProviderError

T = TypeVar("T")


def post_json_with_retry(
    post_json: Callable[..., T],
    url: str,
    payload: Dict[str, Any],
    *,
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **post_kwargs: Any,
) -> T:
    """
    Call ``post_json`` with exponential backoff on 429 and some 5xx errors.

    Pass ``aion.providers.http_utils.post_json`` as the first argument.
    """
    last: Optional[BaseException] = None
    for attempt in range(max_retries + 1):
        try:
            return post_json(url, payload, headers=headers, **post_kwargs)
        except ProviderError as e:
            last = e
            if e.status is None or e.status not in (429, 502, 503, 504):
                raise
            if attempt >= max_retries:
                raise
            delay = base_delay * (2**attempt) + random.uniform(0, 0.25)
            time.sleep(delay)
    assert last is not None
    raise last
