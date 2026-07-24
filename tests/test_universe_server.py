"""HTTP smoke tests for Cosmos dashboard server."""

from __future__ import annotations

import json
import socket
import threading
import urllib.request


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_universe_api_info():
    from aion.universe.server import run_server

    port = _free_port()
    thread = threading.Thread(
        target=run_server,
        kwargs={"host": "127.0.0.1", "port": port},
        daemon=True,
    )
    thread.start()

    import time

    for _ in range(40):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/info", timeout=0.5) as resp:
                data = json.loads(resp.read().decode())
            assert data["app"] == "universe"
            break
        except Exception:
            time.sleep(0.05)
    else:
        raise AssertionError("universe server did not start")
