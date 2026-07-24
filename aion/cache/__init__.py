"""
Caching utilities: LLM response cache, disk-backed TTL cache, decorator.

Provides a general-purpose ``Cache`` protocol, an in-memory ``MemoryCache``,
a SQLite-backed ``DiskCache``, an LLM-specific ``LLMCache``, and a ``@cached``
decorator that wraps any callable with transparent caching.

All caches support optional time-to-live (TTL) expiration.

Examples
--------
>>> from aion.cache import DiskCache, cached
>>> cache = DiskCache(".aion_cache.db", default_ttl=3600)
>>> cache.set("key", {"data": 42})
>>> cache.get("key")
{'data': 42}

>>> @cached(ttl=300)
... def expensive(x):
...     return x ** 2
"""

from .core import Cache, MemoryCache, DiskCache
from .decorator import cached
from .llm_cache import LLMCache

__all__ = [
    "Cache",
    "DiskCache",
    "LLMCache",
    "MemoryCache",
    "cached",
]
