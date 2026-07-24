"""Start uvicorn for the monitor FastAPI app (optional ``[monitor]`` dependencies)."""

from __future__ import annotations

import subprocess
import sys
import threading
import time
import webbrowser


def run_monitor_command(
    host: str = "127.0.0.1",
    port: int = 8000,
    open_browser: bool = True,
    open_docs: bool = False,
) -> None:
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print(
            "The monitor server needs uvicorn (and fastapi, psutil). "
            "Install with: pip install 'aqwel-aion[monitor]'",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        import aion.monitor.server  # noqa: F401 — validates fastapi + app
    except ImportError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    path = "/docs" if open_docs else "/dashboard/"
    url = f"http://{host}:{port}{path}"
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "aion.monitor.server:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if open_browser:

        def _open():
            time.sleep(1.5)
            webbrowser.open(url)

        threading.Thread(target=_open, daemon=True).start()

    print(f"Monitor: {url}")
    if not open_docs:
        print(f"API docs: http://{host}:{port}/docs")
    print("Press Ctrl+C to stop.")
    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        pass
