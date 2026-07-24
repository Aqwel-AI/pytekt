# aion.monitor — Examples

Requires **`aqwel-aion[monitor]`** (or `pip install -e ".[monitor]"` from the repo root).

## Without keeping a server running

Print **one** JSON snapshot using FastAPI’s test client (starts app **lifespan**, so the background sampler runs briefly):

```bash
python -m aion.monitor.examples.demo_snapshot
```

| Script | What it does |
|--------|----------------|
| **demo_snapshot.py** | `GET /api/metrics/snapshot` and pretty-print keys + latest CPU/RAM if present. |

## With the dashboard running

Terminal A:

```bash
python3 -m aion monitor --no-browser
```

Terminal B:

```bash
curl -s http://127.0.0.1:8000/api/metrics/snapshot | head -c 500
open http://127.0.0.1:8000/dashboard/
```

Full package overview: [`../README.md`](../README.md).
