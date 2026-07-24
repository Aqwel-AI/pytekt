#!/usr/bin/env python3
"""
Print a single /api/metrics/snapshot-style payload using the in-process app.

No browser or long-running server required; useful for smoke tests.

Run::

    python -m aion.monitor.examples.demo_snapshot
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        from starlette.testclient import TestClient
    except ImportError:
        print("Install monitor extras: pip install 'aqwel-aion[monitor]'", file=sys.stderr)
        return 1
    try:
        from aion.monitor.server import app
    except ImportError as e:
        print(str(e), file=sys.stderr)
        return 1

    with TestClient(app) as client:
        r = client.get("/api/metrics/snapshot")
        if r.status_code != 200:
            print("HTTP", r.status_code, r.text[:500], file=sys.stderr)
            return 1
        data = r.json()

    print(json.dumps({k: data[k] for k in data if k != "history"}, indent=2))
    hist = data.get("history") or []
    print("\nhistory points:", len(hist), " max:", data.get("history_max_points"))
    latest = data.get("latest")
    if latest:
        print(
            "latest: cpu={:.1f}% ram={:.1f}%".format(
                float(latest.get("cpu", 0)),
                float(latest.get("ram_pct", 0)),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
