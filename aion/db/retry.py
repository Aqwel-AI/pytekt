"""Retry transient database errors."""

from __future__ import annotations

import random
import time
from typing import Callable, Tuple, Type, TypeVar

from .errors import ConnectionError, DbError

T = TypeVar("T")

_TRANSIENT = (ConnectionError,)


def with_retry(
    fn: Callable[[], T],
    *,
    max_retries: int = 3,
    base_delay: float = 0.5,
    retry_on: Tuple[Type[BaseException], ...] = _TRANSIENT,
) -> T:
    last: BaseException | None = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except retry_on as e:
            last = e
            if attempt >= max_retries:
                raise
            time.sleep(base_delay * (2**attempt) + random.uniform(0, 0.1))
        except DbError:
            raise
    assert last is not None
    raise last
