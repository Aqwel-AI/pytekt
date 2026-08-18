"""Simple token-bucket rate limiter for serializing API calls."""

from __future__ import annotations

import time


class TokenBucket:
    """
    Token bucket: at most ``capacity`` bursts, refilled at ``rate_per_sec``.
    ``acquire`` blocks until ``n`` tokens are available.
    """

    def __init__(self, rate_per_sec: float, capacity: float) -> None:
        if rate_per_sec <= 0:
            raise ValueError("rate_per_sec must be positive")
        self._rate = rate_per_sec
        self._capacity = capacity
        self._tokens = float(capacity)
        self._last = time.monotonic()

    def acquire(self, n: float = 1.0) -> None:
        """Block until ``n`` tokens can be consumed."""
        if n <= 0:
            return
        while True:
            now = time.monotonic()
            elapsed = now - self._last
            self._last = now
            self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
            if self._tokens >= n:
                self._tokens -= n
                return
            need = n - self._tokens
            wait = need / self._rate
            time.sleep(max(wait, 0.01))
