"""Query result caching decorator."""

from __future__ import annotations

import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def cached(
    fn: Optional[F] = None,
    *,
    ttl: int = 300,
    cache_path: str = ".aion_db_cache.db",
) -> Any:
    """
    Cache function results using :mod:`pytekt.cache` disk cache.

    Cache key is derived from function name + arguments.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from ..cache import DiskCache

            cache = DiskCache(cache_path, default_ttl=ttl)
            key_src = json.dumps(
                {"fn": func.__name__, "args": args, "kwargs": kwargs},
                default=str,
                sort_keys=True,
            )
            key = hashlib.sha256(key_src.encode()).hexdigest()[:32]
            hit = cache.get(key)
            if hit is not None:
                return hit
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        return wrapper  # type: ignore[return-value]

    if fn is not None:
        return decorator(fn)
    return decorator
