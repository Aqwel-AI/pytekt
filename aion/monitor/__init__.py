"""
Host metrics, optional HTTP API, and a browser dashboard.

Requires optional dependencies for full functionality::

    pip install "aqwel-aion[monitor]"

Developer documentation: see ``README.md`` in this package (module layout, CLI, API).

- **hardware** — CPU/RAM/disk via ``psutil`` (lazy-imported per call).
- **runtime** — simple request-duration tracker.
- **server** — FastAPI app (``app``) for ``uvicorn aion.monitor.server:app``.
"""

from __future__ import annotations

from .hardware import get_cpu, get_disk, get_ram
from .runtime import RuntimeTracker, tracker

__all__ = [
    "get_cpu",
    "get_disk",
    "get_ram",
    "RuntimeTracker",
    "tracker",
]
