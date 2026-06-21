"""Stdlib HTTP server for the Aion agent web UI."""

from __future__ import annotations

import json
import os
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from .service import WebAgentService, get_service

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
DEFAULT_PORT = 3860


def _library_info(workspace: str) -> Dict[str, Any]:
    try:
        from ... import __version__

        return {
            "app": "aion-agent-web",
            "version": __version__,
            "workspace": workspace,
            "python": sys.version.split()[0],
        }
    except Exception:
        return {"app": "aion-agent-web", "version": "unknown", "workspace": workspace}


class AgentWebHandler(SimpleHTTPRequestHandler):
    service: Optional[WebAgentService] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        svc = self.service or get_service()

        if path == "/api/info":
            self._json(_library_info(svc.workspace_root))
        elif path == "/api/session":
            self._json(svc.session_dict())
        elif path == "/api/providers":
            self._json({"providers": svc.list_providers()})
        elif path.startswith("/api/providers/") and path.endswith("/models"):
            pid = path.split("/")[3]
            self._json(svc.list_models(pid))
        elif path == "/api/activity":
            n = int((qs.get("limit") or ["20"])[0])
            self._json({"events": svc.activity(n)})
        elif path == "/api/files":
            p = (qs.get("path") or ["."])[0]
            rec = (qs.get("recursive") or ["false"])[0].lower() in ("1", "true", "yes")
            self._json(svc.list_files(p, recursive=rec))
        elif path == "/api/file":
            p = (qs.get("path") or [""])[0]
            if not p:
                self._json({"error": "path required"}, status=400)
            else:
                self._json(svc.read_file(p))
        elif path == "/api/pending":
            self._json({"pending": svc.pending_approvals()})
        elif path == "/api/events/stream":
            self._sse_events(svc)
        elif path == "/api/chat/stream":
            message = (qs.get("message") or [""])[0]
            if not message:
                self._json({"error": "message required"}, status=400)
            else:
                self._sse_chat(svc, message)
        elif path.startswith("/api/"):
            self.send_error(404)
        elif path in ("/", ""):
            self.path = "/index.html"
            super().do_GET()
        else:
            disk = os.path.join(STATIC_DIR, path.lstrip("/"))
            if os.path.isfile(disk):
                super().do_GET()
            else:
                self.path = "/index.html"
                super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        svc = self.service or get_service()
        body = self._read_json()

        if path == "/api/connect":
            self._json(
                svc.connect(
                    body.get("provider", ""),
                    model=body.get("model"),
                    api_key=body.get("api_key"),
                )
            )
        elif path == "/api/disconnect":
            self._json(svc.disconnect())
        elif path == "/api/mode":
            self._json(svc.set_mode(body.get("mode", "")))
        elif path == "/api/trust":
            self._json(svc.set_trust(bool(body.get("trusted"))))
        elif path == "/api/chat":
            self._json(svc.chat(body.get("message", "")))
        elif path == "/api/pin":
            self._json(svc.pin(body.get("path", "")))
        elif path == "/api/unpin":
            self._json(svc.unpin(body.get("path")))
        elif path == "/api/undo":
            self._json(svc.undo())
        elif path == "/api/reset":
            self._json(svc.reset())
        elif path == "/api/approve":
            self._json(
                svc.approve_diff(
                    body.get("id", ""),
                    body.get("action", "reject"),
                )
            )
        elif path == "/api/open-files":
            paths = body.get("paths") or []
            svc.write_open_files(paths)
            self._json({"ok": True})
        elif path == "/api/command":
            self._json(svc.run_command(body.get("cmd", ""), body.get("args", "")))
        else:
            self.send_error(404)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(payload)

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    def _sse_chat(self, svc: WebAgentService, message: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self._cors_headers()
        self.end_headers()
        for chunk in svc.chat_stream(message):
            self.wfile.write(chunk.encode("utf-8"))
            self.wfile.flush()

    def _sse_events(self, svc: WebAgentService) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self._cors_headers()
        self.end_headers()
        q = svc.events.subscribe()
        try:
            for recent in svc.events.recent(10):
                line = f"data: {json.dumps({'type': 'replay', **recent}, default=str)}\n\n"
                self.wfile.write(line.encode("utf-8"))
            for chunk in svc.events.iter_sse(q, timeout=25.0):
                self.wfile.write(chunk.encode("utf-8"))
                self.wfile.flush()
        finally:
            svc.events.unsubscribe(q)

    def log_message(self, fmt, *args):
        pass


def run_server(
    host: str = "127.0.0.1",
    port: int = DEFAULT_PORT,
    workspace_root: Optional[str] = None,
) -> None:
    import errno

    svc = get_service(workspace_root)
    AgentWebHandler.service = svc

    def handler(*args, **kwargs):
        AgentWebHandler(*args, **kwargs)

    try:
        server = HTTPServer((host, port), handler)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print(f"Port {port} in use — agent web UI may already be running: http://{host}:{port}/")
            return
        raise
    print(f"Aion Agent Web UI: http://{host}:{port}/")
    print(f"Workspace: {svc.workspace_root}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()


def is_agent_web_server(host: str, port: int) -> bool:
    import urllib.error
    import urllib.request

    url = f"http://{host}:{port}/api/info"
    try:
        with urllib.request.urlopen(url, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return isinstance(data, dict) and data.get("app") == "aion-agent-web"
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
        return False
