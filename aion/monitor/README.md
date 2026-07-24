# aion.monitor — Package documentation

## 1. Title and overview

**`aion.monitor`** is a **local hardware and runtime observability** slice of Aion: **CPU** (overall + per-core), **RAM**, **disk usage and I/O rates**, optional **NVIDIA GPU** metrics (utilization, VRAM, temperature), **top processes by memory**, and a **browser dashboard** with about **1–5 minutes** of rolling history (1 sample per second).

It is meant for **developers on their own machine** (training jobs, local APIs), not for multi-host production monitoring.

---

## 2. Module layout

| Path | Role |
|------|------|
| `__init__.py` | Re-exports `get_cpu`, `get_disk`, `get_ram`, `RuntimeTracker`, `tracker`. |
| `hardware.py` | `psutil`-backed CPU/RAM/disk helpers; lazy import of `psutil` with a clear error if missing. |
| `gpu.py` | NVIDIA metrics via **`pynvml`** (`nvidia-ml-py`) or **`nvidia-smi`** fallback. |
| `processes.py` | `top_memory_processes` — RSS-ranked process list with short command lines. |
| `history.py` | `MetricSampler` / `sampler` — background thread, ~1 Hz samples, deque up to **300** points (~5 min). |
| `runtime.py` | `RuntimeTracker` — simple in-process duration stats (used by `/runtime`). |
| `server.py` | **FastAPI** `app`: `/`, `/dashboard/`, `/api/metrics/snapshot`, `/hardware`, `/runtime`, `/docs`. |
| `launch.py` | `run_monitor_command` — spawns `python -m uvicorn aion.monitor.server:app`, optional browser. |
| `cli.py` | `python -m aion.monitor.cli` entry (argparse); same behavior as `aion monitor`. |
| `static/index.html` | Single-page **dashboard** (Chart.js from CDN); packaged via `package_data` / `MANIFEST.in`. |

---

## 3. How developers use it

### Install optional dependencies

```bash
pip install "aqwel-aion[monitor]"
# editable from repo root:
pip install -e ".[monitor]"
```

Core pieces: **`psutil`**, **`fastapi`**, **`uvicorn[standard]`**, **`nvidia-ml-py`** (GPU; still falls back to `nvidia-smi` when possible).

### CLI (recommended)

If the shell cannot find `aion` (scripts dir not on `PATH`), use **`python3 -m aion`** — same as the `aion` console script.

```bash
python3 -m aion monitor              # dashboard + API; opens browser by default
python3 -m aion dashboard            # alias of monitor
python3 -m aion monitor --no-browser # print URL only
python3 -m aion monitor --docs       # open Swagger UI instead of dashboard
python3 -m aion monitor -p 8765      # custom port
```

Equivalent module entry:

```bash
python3 -m aion.monitor.cli --help
```

### Uvicorn only

```bash
python3 -m uvicorn aion.monitor.server:app --host 127.0.0.1 --port 8000
```

Then open **http://127.0.0.1:8000/dashboard/** (or **/** which redirects there).

### Python API (metrics without HTTP)

```python
from aion.monitor.hardware import get_cpu, get_ram, get_cpu_detailed
from aion.monitor.gpu import get_gpu_metrics
from aion.monitor.processes import top_memory_processes

ram = get_ram()
gpu = get_gpu_metrics()
procs = top_memory_processes(limit=20)
```

For the **full snapshot** (history + processes) as served to the dashboard, start the app so the **sampler** runs, then `GET /api/metrics/snapshot` or use **`aion.monitor.history.sampler.snapshot()`** only after the server lifespan has started the sampler (normally via `server.py`).

### HTTP endpoints (summary)

| Path | Purpose |
|------|---------|
| `/dashboard/` | Static **hardware dashboard** UI. |
| `/api/metrics/snapshot` | JSON: `history`, `latest`, `processes`, intervals. |
| `/hardware` | Legacy snapshot: CPU %, RAM, disk usage (blocking CPU read). |
| `/runtime` | `RuntimeTracker.stats()`. |
| `/docs` | OpenAPI / Swagger. |

---

## 4. Examples

Runnable helper and copy-paste commands: **[examples/](examples/)** — see [examples/README.md](examples/README.md).

```bash
python -m aion.monitor.examples.demo_snapshot
```

---

## 5. Conventions

- **Lazy imports:** `psutil` and **FastAPI** are not required to **import** `aion` itself; they are required when you call hardware helpers or load `server.py`.
- **GPU:** Apple Silicon / AMD / machines without NVIDIA drivers will show **no GPU** in the dashboard; that is expected.
- **Disk I/O:** Rates come from **`psutil.disk_io_counters()`** (aggregate); may be **zero** or **unavailable** on some OS configurations.
- **Security:** The server defaults to **127.0.0.1**; do not expose it to untrusted networks without authentication and TLS.

---

## 6. Dependencies

- Declared under **`[project.optional-dependencies].monitor`** in **`pyproject.toml`** (and mirrored in **`setup.py`**): `psutil`, `fastapi`, `uvicorn[standard]`, `nvidia-ml-py`.

---

## 7. See also

- Root CLI: **`aion.cli`** (`python3 -m aion --help`)
- Root README: [../../README.md](../../README.md)
