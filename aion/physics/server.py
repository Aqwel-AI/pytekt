"""Stdlib HTTP server for the Aion physics dashboard."""

from __future__ import annotations

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Any
from urllib.parse import parse_qs, urlparse

from . import web_api

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def _qs_float(qs: dict, key: str, default: float) -> float:
    raw = (qs.get(key) or [None])[0]
    return float(raw) if raw is not None else default


def _qs_int(qs: dict, key: str, default: int) -> int:
    raw = (qs.get(key) or [None])[0]
    return int(raw) if raw is not None else default


class _ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class PhysicsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        try:
            if path == "/api/info":
                self._json(web_api.library_info())
            elif path == "/api/tasks":
                self._json(web_api.tasks_payload())
            elif path == "/api/query":
                text = (qs.get("q") or qs.get("text") or [""])[0]
                self._json(web_api.query_payload(text))
            elif path == "/api/pendulum":
                self._json(
                    web_api.pendulum_payload(
                        length=_qs_float(qs, "length", 1.0),
                        angle_deg=_qs_float(qs, "angle_deg", 15.0),
                        dt=_qs_float(qs, "dt", 0.01),
                        steps=_qs_int(qs, "steps", 1000),
                    )
                )
            elif path == "/api/projectile":
                self._json(
                    web_api.projectile_payload(
                        v0=_qs_float(qs, "v0", 20.0),
                        angle_deg=_qs_float(qs, "angle_deg", 45.0),
                        dt=_qs_float(qs, "dt", 0.01),
                        steps=_qs_int(qs, "steps", 1000),
                        drag=_qs_float(qs, "drag", 0.0),
                    )
                )
            else:
                super().do_GET()
        except Exception as exc:
            self._json({"error": str(exc)}, status=400)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json({"error": "invalid JSON"}, status=400)
            return

        try:
            if parsed.path == "/api/query":
                self._json(web_api.query_payload(str(data.get("text", ""))))
            else:
                self._json({"error": "not found"}, status=404)
        except Exception as exc:
            self._json({"error": str(exc)}, status=400)

    def _json(self, payload: Any, *, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args) -> None:
        if os.environ.get("AION_PHYSICS_QUIET"):
            return
        super().log_message(fmt, *args)


def run_server(host: str = "127.0.0.1", port: int = 3858) -> None:
    os.makedirs(STATIC_DIR, exist_ok=True)
    if not os.path.isfile(os.path.join(STATIC_DIR, "index.html")):
        _write_fallback_static()
    server = _ThreadingHTTPServer((host, port), PhysicsHandler)
    print(f"Aion Physics dashboard at http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.shutdown()


def _write_fallback_static() -> None:
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Aion Physics</title></head>
<body><h1>Aion Physics</h1><p>Build the UI: cd aion/physics/web && npm install && npm run build</p>
<script>
fetch('/api/info').then(r=>r.json()).then(d=>document.body.innerHTML+='<pre>'+JSON.stringify(d,null,2)+'</pre>');
</script></body></html>"""
    with open(os.path.join(STATIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 3858
    run_server(host=host, port=port)
