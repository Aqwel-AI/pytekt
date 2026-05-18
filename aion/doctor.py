"""
Environment diagnostics for Aion research workflows.

Run via CLI: ``python -m aion doctor`` or ``aion doctor`` (after install).
"""

from __future__ import annotations

import os
import sys
from typing import List, Tuple


def _check(name: str, ok: bool, detail: str = "") -> Tuple[str, bool, str]:
    return name, ok, detail


def run_doctor(*, verbose: bool = True) -> bool:
    """
    Print environment checks. Returns True if all required checks pass.
    """
    lines: List[Tuple[str, bool, str]] = []

    py_ok = sys.version_info >= (3, 8)
    lines.append(_check("Python >= 3.8", py_ok, sys.version.split()[0]))

    try:
        import numpy as np

        lines.append(_check("numpy", True, np.__version__))
    except ImportError:
        lines.append(_check("numpy", False, "pip install numpy"))

    try:
        from aion import __version__

        lines.append(_check("aion", True, __version__))
    except ImportError as e:
        lines.append(_check("aion", False, str(e)))

    optional = [
        ("matplotlib", "viz", "aion[viz]"),
        ("pandas", "ai", "aion[ai]"),
        ("fastapi", "serve", "aion[serve]"),
        ("sentence_transformers", "rag", "aion[rag]"),
        ("gradio", "ui", "aion[ui]"),
    ]
    for mod, extra, hint in optional:
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "ok")
            lines.append(_check(f"{mod} [{extra}]", True, str(ver)))
        except ImportError:
            lines.append(_check(f"{mod} [{extra}]", False, f"optional: pip install 'aqwel-aion[{extra}]'"))

    tracker_dir = ".aion_experiments"
    writable = True
    try:
        os.makedirs(tracker_dir, exist_ok=True)
        test = os.path.join(tracker_dir, ".write_test")
        with open(test, "w") as f:
            f.write("ok")
        os.remove(test)
    except OSError as e:
        writable = False
        lines.append(_check("tracker directory writable", False, str(e)))
    else:
        lines.append(_check("tracker directory writable", True, tracker_dir))

    try:
        from aion._core import using_native_extension

        native = using_native_extension()
        lines.append(_check("aion C++ extension", native, "native" if native else "numpy fallback"))
    except Exception:
        lines.append(_check("aion C++ extension", False, "not built"))

    all_required_ok = all(ok for name, ok, _ in lines if "optional" not in _.lower() and name in (
        "Python >= 3.8", "numpy", "aion", "tracker directory writable"
    ))

    if verbose:
        _print_report(lines, all_required_ok)
    return all_required_ok


def _print_report(lines: List[Tuple[str, bool, str]], all_ok: bool) -> None:
    use_color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    print()
    print("  Aion Doctor — research environment")
    print("  " + "─" * 40)
    for name, ok, detail in lines:
        mark = "\033[32m✓\033[0m" if ok and use_color else ("✓" if ok else "✗")
        if not ok and use_color:
            mark = "\033[31m✗\033[0m"
        line = f"  {mark}  {name}"
        if detail:
            line += f"  ({detail})"
        print(line)
    print()
    if all_ok:
        msg = "  Ready for research workflows."
        if use_color:
            msg = "\033[32m" + msg + "\033[0m"
    else:
        msg = "  Fix required checks above before running experiments."
        if use_color:
            msg = "\033[33m" + msg + "\033[0m"
    print(msg)
    print()


def main() -> None:
    ok = run_doctor()
    sys.exit(0 if ok else 1)
