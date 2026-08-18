"""Pipeline engine: step protocol, execution, and serialization."""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class Step(ABC):
    """
    Base class for a pipeline step.

    Subclasses must set ``name`` and implement ``run``.
    """

    name: str = "unnamed"
    retries: int = 0
    fallback: Optional[Callable[..., Any]] = None

    @abstractmethod
    def run(self, data: Any, ctx: Dict[str, Any]) -> Any:
        """Transform *data* and return the result. *ctx* is shared state."""
        ...

    def on_error(self, error: Exception, data: Any, ctx: Dict[str, Any]) -> Any:
        """Called when ``run`` raises. Override to provide custom recovery."""
        raise error


@dataclass
class StepResult:
    name: str
    success: bool
    elapsed_ms: float
    error: Optional[str] = None


@dataclass
class PipelineResult:
    """Outcome of a full pipeline execution."""

    success: bool
    data: Any = None
    steps: List[StepResult] = field(default_factory=list)
    total_ms: float = 0.0

    @property
    def failed_steps(self) -> List[StepResult]:
        return [s for s in self.steps if not s.success]


class Pipeline:
    """
    Sequential chain of :class:`Step` objects.

    Parameters
    ----------
    steps : list[Step]
        Ordered list of processing steps.
    """

    def __init__(self, steps: Optional[List[Step]] = None) -> None:
        self.steps: List[Step] = list(steps or [])

    def add(self, step: Step) -> "Pipeline":
        self.steps.append(step)
        return self

    def execute(self, data: Any, *, ctx: Optional[Dict[str, Any]] = None) -> Any:
        """Run all steps sequentially. Returns the final transformed data."""
        result = self.execute_detailed(data, ctx=ctx)
        if not result.success:
            failed = result.failed_steps
            msg = "; ".join(f"{s.name}: {s.error}" for s in failed)
            raise RuntimeError(f"Pipeline failed at: {msg}")
        return result.data

    def execute_detailed(
        self, data: Any, *, ctx: Optional[Dict[str, Any]] = None
    ) -> PipelineResult:
        """Run all steps and return a :class:`PipelineResult` with per-step timing."""
        context = ctx or {}
        step_results: List[StepResult] = []
        t0 = time.perf_counter()

        for step in self.steps:
            s_start = time.perf_counter()
            try:
                data = self._run_with_retry(step, data, context)
                step_results.append(
                    StepResult(step.name, True, (time.perf_counter() - s_start) * 1000)
                )
            except Exception as exc:
                step_results.append(
                    StepResult(
                        step.name,
                        False,
                        (time.perf_counter() - s_start) * 1000,
                        str(exc),
                    )
                )
                return PipelineResult(
                    False, data, step_results, (time.perf_counter() - t0) * 1000
                )

        return PipelineResult(
            True, data, step_results, (time.perf_counter() - t0) * 1000
        )

    def dry_run(self, data: Any) -> List[str]:
        """Return the list of step names that *would* execute (no side effects)."""
        return [s.name for s in self.steps]

    def to_json(self) -> str:
        return json.dumps(
            {"steps": [{"name": s.name, "retries": s.retries} for s in self.steps]},
            indent=2,
        )

    def __len__(self) -> int:
        return len(self.steps)

    def __repr__(self) -> str:
        names = " -> ".join(s.name for s in self.steps)
        return f"Pipeline({names})"

    @staticmethod
    def _run_with_retry(step: Step, data: Any, ctx: Dict[str, Any]) -> Any:
        last_err: Optional[Exception] = None
        for attempt in range(1 + step.retries):
            try:
                return step.run(data, ctx)
            except Exception as exc:
                last_err = exc
                if attempt == step.retries:
                    if step.fallback is not None:
                        return step.fallback(data, ctx)
                    return step.on_error(exc, data, ctx)
        raise last_err  # type: ignore[misc]
