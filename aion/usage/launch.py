"""Launch usage dashboard in the browser (singleton server)."""

from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from typing import Optional, Tuple

_SERVER_THREAD: Optional[threading.Thread] = None
_SERVER_PORT: Optional[int] = None
_SERVER_LOCK = threading.Lock()
_DEFAULT_HOST = "127.0.0.1"
# Not 3333 — often taken by other local apps (e.g. PHP). Aion-only default:
_DEFAULT_PORT = 3847
_PORT_SCAN_RANGE = 15


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.35):
            return True
    except OSError:
        return False


def is_aion_usage_server(host: str, port: int) -> bool:
    """True if this port serves the Aion usage API (not another app)."""
    url = f"http://{host}:{port}/api/info"
    try:
        with urllib.request.urlopen(url, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return isinstance(data, dict) and "version" in data
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
        return False


def resolve_usage_port(host: str, preferred: int = _DEFAULT_PORT) -> Tuple[int, bool]:
    """
    Pick a port for the Aion React dashboard.

    Returns ``(port, already_running)``.
    """
    if is_aion_usage_server(host, preferred):
        return preferred, True

    if not _port_open(host, preferred):
        return preferred, False

    for offset in range(1, _PORT_SCAN_RANGE):
        candidate = preferred + offset
        if is_aion_usage_server(host, candidate):
            return candidate, True
        if not _port_open(host, candidate):
            return candidate, False

    return preferred + _PORT_SCAN_RANGE, False


def _start_server_thread(host: str, port: int) -> None:
    global _SERVER_THREAD, _SERVER_PORT

    def _run():
        from .server import run_server

        run_server(host=host, port=port)

    _SERVER_PORT = port
    _SERVER_THREAD = threading.Thread(target=_run, name="aion-usage-server", daemon=True)
    _SERVER_THREAD.start()


def dashboard_url(host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT) -> str:
    return f"http://{host}:{port}/"


def ensure_usage_dashboard(
    host: str = _DEFAULT_HOST,
    port: int = _DEFAULT_PORT,
    *,
    open_browser: bool = True,
    wait_ready: float = 2.0,
) -> Tuple[str, bool]:
    """
    Ensure the Aion React dashboard server is running; open the browser.

    Returns ``(url, started_new_server)``.
    Never opens a random app on a busy port — verifies ``/api/info`` first.
    """
    use_port, already = resolve_usage_port(host, port)
    url = dashboard_url(host, use_port)
    started_new = False

    if already:
        if open_browser:
            webbrowser.open(url)
        return url, False

    with _SERVER_LOCK:
        if _SERVER_THREAD is not None and _SERVER_THREAD.is_alive() and _SERVER_PORT:
            if is_aion_usage_server(host, _SERVER_PORT):
                url = dashboard_url(host, _SERVER_PORT)
                if open_browser:
                    webbrowser.open(url)
                return url, False

        if use_port != port and _port_open(host, port):
            print(
                f"Note: port {port} is used by another app (not Aion). "
                f"Using port {use_port} for the usage dashboard."
            )

        _start_server_thread(host, use_port)
        started_new = True
        url = dashboard_url(host, use_port)

    if started_new and wait_ready > 0:
        deadline = time.time() + wait_ready
        while time.time() < deadline:
            if is_aion_usage_server(host, use_port):
                break
            time.sleep(0.08)

    if open_browser:
        webbrowser.open(url)

    return url, started_new


def run_usage_dashboard(
    host: str = _DEFAULT_HOST,
    port: int = _DEFAULT_PORT,
    open_browser: bool = True,
) -> None:
    """Blocking entry for ``aion usage`` — runs Aion server in foreground."""
    use_port, already = resolve_usage_port(host, port)
    url = dashboard_url(host, use_port)

    if already:
        print(f"Aion usage dashboard already running at {url}")
        if open_browser:
            webbrowser.open(url)
        return

    if use_port != port and _port_open(host, port):
        print(
            f"Port {port} is in use by another program — starting Aion on {use_port} instead."
        )

    if open_browser:

        def _open():
            time.sleep(0.6)
            webbrowser.open(url)

        threading.Thread(target=_open, daemon=True).start()

    from .server import run_server

    run_server(host=host, port=use_port)
