"""
Step-based pipelines for chaining operations declaratively.

Build composable data-processing or ML pipelines from reusable ``Step``
objects. Supports error handling (retry / fallback), dry-run mode, and
JSON serialization of pipeline definitions.

Examples
--------
>>> from aion.pipeline import Pipeline, Step
>>> class Double(Step):
...     name = "double"
...     def run(self, data, ctx):
...         return [x * 2 for x in data]
>>> pipe = Pipeline([Double()])
>>> pipe.execute([1, 2, 3])
[2, 4, 6]
"""

from .core import Pipeline, Step, PipelineResult
from .steps import FunctionStep, FilterStep, MapStep, BatchStep

__all__ = [
    "BatchStep",
    "FilterStep",
    "FunctionStep",
    "MapStep",
    "Pipeline",
    "PipelineResult",
    "Step",
]
