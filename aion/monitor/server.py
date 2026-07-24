"""
FastAPI monitor: hardware dashboard, JSON APIs, and optional ``/docs``.

Run locally::

    uvicorn aion.monitor.server:app --reload

Requires ``pip install 'aqwel-aion[monitor]'``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

try:
    from fastapi import FastAPI
    from fastapi.responses import RedirectResponse
    from fastapi.staticfiles import StaticFiles
except ImportError as e:  # pragma: no cover - import guard
    raise ImportError(
        "aion.monitor.server requires fastapi and uvicorn. "
        "Install with: pip install 'aqwel-aion[monitor]'"
    ) from e

from aion.monitor.hardware import get_cpu, get_disk, get_ram
from aion.monitor.history import sampler
from aion.monitor.runtime import tracker

_STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def _lifespan(app: FastAPI):
    sampler.start()
    yield
    sampler.stop()


app = FastAPI(title="Aion monitor", version="0.2.0", lifespan=_lifespan)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard/")


@app.get("/hardware")
def hardware():
    return {
        "cpu": get_cpu(0.1),
        "ram": get_ram(),
        "disk": get_disk(),
    }


@app.get("/runtime")
def runtime():
    return tracker.stats()


@app.get("/api/metrics/snapshot")
def metrics_snapshot():
    """Dashboard payload: rolling history (up to 5 min @ 1 Hz), latest point, top processes."""
    return sampler.snapshot()


def _mount_dashboard() -> None:
    if not _STATIC_DIR.is_dir():
        return
    app.mount(
        "/dashboard",
        StaticFiles(directory=str(_STATIC_DIR), html=True),
        name="dashboard",
    )


_mount_dashboard()
