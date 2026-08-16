"""Stdlib HTTP server for the PyTekt usage dashboard."""

from __future__ import annotations

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

from .aggregate import build_summary, build_timeseries, build_week_comparison
from .hardware_api import get_hardware_snapshot, get_system_info, history_for_charts, start_hardware_sampling
from .store import UsageStore

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def _library_info() -> Dict[str, Any]:
    try:
        from .. import __version__, __developer__

        return {
            "version": __version__,
            "developer": __developer__,
            "python": sys.version.split()[0],
        }
    except Exception:
        return {"version": "unknown"}


def _agent_session() -> Dict[str, Any]:
    """Legacy endpoint — coding agent removed from this package version."""
    try:
        from ..user_config import get_config

        cfg = get_config()
        agent = cfg.get("agent") or {}
        return {
            "provider": agent.get("provider"),
            "model": agent.get("model"),
            "trust": bool(agent.get("trust")),
            "idle_disconnect_minutes": agent.get("idle_disconnect_minutes"),
            "config_path": os.path.expanduser("~/.pytekt.yaml"),
            "note": "pytekt agent was moved to archived/pytekt_agent/",
        }
    except Exception as e:
        return {"error": str(e)}


def _connected_providers(cfg: Dict[str, Any]) -> List[str]:
    keys = cfg.get("keys") or {}
    names: List[str] = []
    for k in keys:
        if k.endswith("_api_key") and keys.get(k):
            names.append(k.replace("_api_key", "").replace("_", " "))
    return sorted(set(names))


class UsageHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, store=None, **kwargs):
        self._store = store or UsageStore()
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        range_key = (qs.get("range") or ["today"])[0]

        if path == "/api/summary":
            events = self._store.read_all()
            self._json(build_summary(events, range_key=range_key))
        elif path == "/api/timeseries":
            events = self._store.read_all()
            self._json(build_timeseries(events, range_key=range_key))
        elif path == "/api/week":
            events = self._store.read_all()
            self._json(build_week_comparison(events))
        elif path == "/api/recent":
            limit = int((qs.get("limit") or ["30"])[0])
            events = list(self._store.iter_events())
            self._json({"events": events[-limit:][::-1]})
        elif path == "/api/info":
            self._json(_library_info())
        elif path == "/api/session":
            self._json(_agent_session())
        elif path == "/api/meta":
            from ..user_config import get_config

            cfg = get_config()
            self._json(
                {
                    "store_path": self._store.path,
                    "event_count": len(self._store.read_all()),
                    "providers_with_keys": _connected_providers(cfg),
                }
            )
        elif path == "/api/hardware":
            try:
                snap = get_hardware_snapshot()
                hist = snap.get("history") or []
                snap["charts"] = history_for_charts(hist)
                self._json(snap)
            except Exception as e:
                self._json(
                    {
                        "ok": False,
                        "error": str(e),
                        "system": get_system_info(),
                        "history": [],
                        "latest": None,
                        "processes": [],
                        "charts": history_for_charts([]),
                    },
                    status=200,
                )
        elif path == "/api/system":
            try:
                self._json(get_system_info())
            except Exception as e:
                self._json({"error": str(e)}, status=200)
        elif path == "/api/context":
            self._json({"note": "pytekt agent was moved to archived/pytekt_agent/"})
        elif path.startswith("/api/"):
            self.send_error(404)
        elif path in ("/", "", "/dashboard", "/dashboard/"):
            self.path = "/index.html"
            super().do_GET()
        else:
            # SPA: React client routes + hashed assets
            disk = os.path.join(STATIC_DIR, path.lstrip("/"))
            if os.path.isfile(disk):
                super().do_GET()
            else:
                self.path = "/index.html"
                super().do_GET()

    def _json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def run_server(host: str = "127.0.0.1", port: int = 3847) -> None:
    import errno

    store = UsageStore()

    def handler(*args, **kwargs):
        UsageHandler(*args, store=store, **kwargs)

    try:
        server = HTTPServer((host, port), handler)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            url = f"http://{host}:{port}/"
            print(f"Port {port} in use — dashboard may already be running: {url}")
            return
        raise
    start_hardware_sampling()
    print(f"PyTekt Usage Dashboard: http://{host}:{port}/")
    print(f"Log file: {store.path}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        from .hardware_api import stop_hardware_sampling

        stop_hardware_sampling()
        server.shutdown()
