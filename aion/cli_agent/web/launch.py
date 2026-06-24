"""Launch agent web UI in the browser."""

from __future__ import annotations

import socket
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from typing import Optional, Tuple

from .server import DEFAULT_PORT, is_agent_web_server, run_server
from .service import clear_web_memory

_DEFAULT_HOST = "127.0.0.1"
_SERVER_THREAD: Optional[threading.Thread] = None
_SERVER_LOCK = threading.Lock()


def ensure_agent_web(
    host: str = _DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    *,
    workspace_root: Optional[str] = None,
    open_browser: bool = True,
    wait_ready: float = 2.0,
) -> Tuple[str, bool]:
    """Start or reuse agent web server. Returns (url, started)."""
    global _SERVER_THREAD
    url = f"http://{host}:{port}/"

    if is_agent_web_server(host, port):
        if open_browser:
            webbrowser.open(url)
        return url, False

    with _SERVER_LOCK:
        if _SERVER_THREAD is not None and _SERVER_THREAD.is_alive():
            if open_browser:
                webbrowser.open(url)
            return url, False

        def _run():
            run_server(host=host, port=port, workspace_root=workspace_root)

        _SERVER_THREAD = threading.Thread(target=_run, daemon=True, name="aion-agent-web")
        _SERVER_THREAD.start()

    deadline = time.time() + wait_ready
    while time.time() < deadline:
        if is_agent_web_server(host, port):
            break
        time.sleep(0.15)

    if open_browser:
        webbrowser.open(url)
    return url, True


def run_agent_web(
    host: str = _DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    *,
    workspace_root: Optional[str] = None,
    open_browser: bool = True,
) -> None:
    """Blocking entry for ``aion agent web``."""
    url, already = (f"http://{host}:{port}/", False)
    if is_agent_web_server(host, port):
        already = True
    if already:
        print(f"Aion agent web UI already running at {url}")
        if open_browser:
            webbrowser.open(url)
        return
    if open_browser:

        def _open():
            time.sleep(0.6)
            webbrowser.open(url)

        threading.Thread(target=_open, daemon=True).start()
    run_server(host=host, port=port, workspace_root=workspace_root)
