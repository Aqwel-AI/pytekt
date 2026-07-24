"""
Run the monitor HTTP server from the command line::

    python -m aion.monitor.cli

Same dependencies as ``aion monitor`` (``aqwel-aion[monitor]``).
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> None:
    from .launch import run_monitor_command

    p = argparse.ArgumentParser(description="Aion monitor — hardware/runtime HTTP API")
    p.add_argument("--host", default="127.0.0.1", help="Bind address")
    p.add_argument("--port", "-p", type=int, default=8000, help="Port (default 8000)")
    p.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the dashboard in a browser",
    )
    p.add_argument(
        "--docs",
        action="store_true",
        help="Open /docs (Swagger) instead of the hardware dashboard",
    )
    ns = p.parse_args(argv)
    run_monitor_command(
        host=ns.host,
        port=ns.port,
        open_browser=not ns.no_browser,
        open_docs=ns.docs,
    )


if __name__ == "__main__":
    main()
