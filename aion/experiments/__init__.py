"""
Research experiment utilities for reproducible DS/ML workflows.

- :class:`Experiment` — tracker + seed + manifest in one context manager
- :func:`export_results_table` — LaTeX / CSV / Markdown tables for papers
- :class:`BenchmarkSuite` — multi-seed benchmarks on built-in datasets

Examples
--------
>>> from aion.experiments import Experiment, BenchmarkSuite, export_results_table
>>> from aion.tracker import Tracker
"""

from .core import Experiment, experiment
from .export import export_results_table, export_results_file
from .benchmark import BenchmarkSuite, BenchmarkResult, BenchmarkTask
from .manifest import build_manifest, load_manifest, save_manifest

__all__ = [
    "Experiment",
    "experiment",
    "export_results_table",
    "export_results_file",
    "BenchmarkSuite",
    "BenchmarkResult",
    "BenchmarkTask",
    "build_manifest",
    "load_manifest",
    "save_manifest",
]
