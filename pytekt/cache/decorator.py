"""@cached decorator for transparent function-level caching."""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional, TypeVar, cast

from .core import Cache, MemoryCache, make_cache_key

F = TypeVar("F", bound=Callable[..., Any])

_DEFAULT_CACHE: Optional[Cache] = None


def _get_default_cache() -> Cache:
    global _DEFAULT_CACHE
    if _DEFAULT_CACHE is None:
        _DEFAULT_CACHE = MemoryCache()
    return _DEFAULT_CACHE


def cached(
    fn: Optional[F] = None,
    *,
    cache: Optional[Cache] = None,
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
) -> Any:
    """
    Decorator that caches function return values.

    Can be used bare (``@cached``) or with arguments (``@cached(ttl=60)``).

    Parameters
    ----------
    cache : Cache, optional
        Cache backend. Defaults to a global ``MemoryCache``.
    ttl : int, optional
        Time-to-live in seconds for cached results.
    key_prefix : str, optional
        Prefix for cache keys (defaults to the function's qualified name).
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            c = cache or _get_default_cache()
            prefix = key_prefix or f"{func.__module__}.{func.__qualname__}"
            key = f"{prefix}:{make_cache_key(*args, **kwargs)}"
            hit = c.get(key)
            if hit is not None:
                return hit
            result = func(*args, **kwargs)
            c.set(key, result, ttl=ttl)
            return result

        wrapper.cache_clear = lambda: (cache or _get_default_cache()).clear()  # type: ignore[attr-defined]
        return cast(F, wrapper)

    if fn is not None:
        return decorator(fn)
    return decorator
