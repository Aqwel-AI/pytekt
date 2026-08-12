"""Launch the Aion Hub dashboard in the browser."""

from __future__ import annotations

import sys
import threading
import time
import webbrowser


def run_hub(
    host: str = "127.0.0.1",
    port: int = 3000,
    open_browser: bool = True,
) -> None:
    from .server import run_server

    url = f"http://{host}:{port}"

    if open_browser:
        def _open():
            time.sleep(0.8)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    print(f"Aion Hub: {url}")
    print("Press Ctrl+C to stop.")
    try:
        run_server(host=host, port=port)
    except KeyboardInterrupt:
        pass
