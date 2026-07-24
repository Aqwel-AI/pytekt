"""Ready-made pipeline step implementations."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence

from .core import Step


class FunctionStep(Step):
    """
    Wrap a plain function as a pipeline step.

    >>> step = FunctionStep("upper", lambda data, ctx: data.upper())
    """

    def __init__(
        self,
        name: str,
        fn: Callable[[Any, Dict[str, Any]], Any],
        *,
        retries: int = 0,
    ) -> None:
        self.name = name
        self.retries = retries
        self._fn = fn

    def run(self, data: Any, ctx: Dict[str, Any]) -> Any:
        return self._fn(data, ctx)


class MapStep(Step):
    """Apply a function to each element of an iterable."""

    def __init__(
        self,
        name: str,
        fn: Callable[[Any], Any],
        *,
        retries: int = 0,
    ) -> None:
        self.name = name
        self.retries = retries
        self._fn = fn

    def run(self, data: Any, ctx: Dict[str, Any]) -> List[Any]:
        return [self._fn(item) for item in data]


class FilterStep(Step):
    """Keep only elements that satisfy a predicate."""

    def __init__(
        self,
        name: str,
        predicate: Callable[[Any], bool],
        *,
        retries: int = 0,
    ) -> None:
        self.name = name
        self.retries = retries
        self._pred = predicate

    def run(self, data: Any, ctx: Dict[str, Any]) -> List[Any]:
        return [item for item in data if self._pred(item)]


class BatchStep(Step):
    """Process data in fixed-size batches, collecting results."""

    def __init__(
        self,
        name: str,
        fn: Callable[[List[Any], Dict[str, Any]], List[Any]],
        batch_size: int = 32,
        *,
        retries: int = 0,
    ) -> None:
        self.name = name
        self.retries = retries
        self._fn = fn
        self._batch_size = batch_size

    def run(self, data: Any, ctx: Dict[str, Any]) -> List[Any]:
        items = list(data)
        results: List[Any] = []
        for i in range(0, len(items), self._batch_size):
            batch = items[i : i + self._batch_size]
            results.extend(self._fn(batch, ctx))
        return results
