"""Launch browser UIs shipped with PyTekt."""

from __future__ import annotations

import threading
import time
import webbrowser
from typing import Any, Dict, List, Optional


def open_in_browser(url: str, *, delay: float = 0.8) -> None:
    """Open *url* in the default browser after a short delay."""
    def _open() -> None:
        time.sleep(delay)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()


def launch_hub(
    host: str = "127.0.0.1",
    port: int = 3000,
    *,
    open_browser: bool = True,
) -> None:
    """Start PyTekt Hub (module explorer + playground). Same as ``pytekt start``."""
    from ..hub.launch import run_hub

    run_hub(host=host, port=port, open_browser=open_browser)


def launch_monitor(
    host: str = "127.0.0.1",
    port: int = 8000,
    *,
    open_browser: bool = True,
    open_docs: bool = False,
) -> None:
    """Start the hardware monitor dashboard (requires ``[monitor]`` extra)."""
    from ..monitor.launch import run_monitor_command

    run_monitor_command(
        host=host,
        port=port,
        open_browser=open_browser,
        open_docs=open_docs,
    )


def list_ui_interfaces() -> List[Dict[str, Any]]:
    """Describe available UIs and how to launch them."""
    return [
        {
            "id": "hub",
            "name": "PyTekt Hub",
            "command": "pytekt start",
            "api": "launch_hub()",
            "url": "http://127.0.0.1:3000",
            "deps": "stdlib only",
            "description": "Module catalog, dependency checker, Python playground.",
        },
        {
            "id": "monitor",
            "name": "Hardware dashboard",
            "command": "pytekt monitor",
            "api": "launch_monitor()",
            "url": "http://127.0.0.1:8000/dashboard/",
            "deps": "[monitor]",
            "description": "Live CPU, RAM, disk, GPU, and process metrics.",
        },
        {
            "id": "universe",
            "name": "Universe dashboard",
            "command": "pytekt universe web",
            "api": "ensure_universe_dashboard()",
            "url": "http://127.0.0.1:3857",
            "deps": "stdlib; C++ optional; [viz] for matplotlib sky PNG",
            "description": "Sky map, moon, coordinates, cosmology, observation log.",
        },
        {
            "id": "usage",
            "name": "Usage dashboard",
            "command": "pytekt usage",
            "api": "ensure_usage_dashboard()",
            "url": "http://127.0.0.1:3847",
            "deps": "stdlib only",
            "description": "LLM token usage, cost, and hardware charts.",
        },
        {
            "id": "serve",
            "name": "API server",
            "command": "pytekt serve (via Python)",
            "api": "pytekt.serve.create_app()",
            "url": "http://127.0.0.1:8080/docs",
            "deps": "[serve]",
            "description": "FastAPI /chat, /rag, /health for LLM apps.",
        },
        {
            "id": "report",
            "name": "HTML reports",
            "command": "pytekt.ui.build_experiment_dashboard(...)",
            "api": "PageBuilder.save()",
            "url": "file:// (static HTML)",
            "deps": "stdlib; matplotlib for figures",
            "description": "Experiment and dataset HTML reports.",
        },
    ]
