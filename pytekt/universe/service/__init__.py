"""
Universe Service: Pipelines, Visualizer, CLI & Web API
======================================================

Provides astronomy pipelines, visualization, CLI commands, and dashboard server:
- Universe pipeline execution steps (CatalogStep, PlotStep)
- Sky map and orbit plots
- HTTP dashboard server and launcher
- CLI entry point
"""

from __future__ import annotations

from .cli import universe_main
from .launch import run_universe_dashboard
from .pipeline import UniverseCatalogStep, UniversePlotStep
from .server import CosmosHandler, STATIC_DIR, run_server
from .viz import plot_orbit, plot_skymap
from . import web_api

main = universe_main

__all__ = [
    "UniverseCatalogStep",
    "UniversePlotStep",
    "plot_skymap",
    "plot_orbit",
    "CosmosHandler",
    "STATIC_DIR",
    "run_server",
    "run_universe_dashboard",
    "universe_main",
    "main",
    "web_api",
]
