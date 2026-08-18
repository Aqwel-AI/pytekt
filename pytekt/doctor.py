"""
Environment diagnostics for PyTekt research workflows.

Run via CLI: ``python -m pytekt doctor`` or ``pytekt doctor`` (after install).
"""

from __future__ import annotations

import os
import shutil
import sys
from typing import List, Tuple

from .native import native_backends


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
        from pytekt import __version__

        lines.append(_check("pytekt", True, __version__))
    except ImportError as e:
        lines.append(_check("pytekt", False, str(e)))

    optional = [
        ("matplotlib", "viz", "pytekt[viz]"),
        ("pandas", "ai", "pytekt[ai]"),
        ("fastapi", "serve", "pytekt[serve]"),
        ("sentence_transformers", "rag", "pytekt[rag]"),
        ("gradio", "ui", "pytekt[ui]"),
        ("PIL", "vision", "pytekt[vision]"),
        ("cv2", "vision", "pytekt[vision]"),
    ]
    for mod, extra, hint in optional:
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "ok")
            lines.append(_check(f"{mod} [{extra}]", True, str(ver)))
        except ImportError:
            lines.append(_check(f"{mod} [{extra}]", False, f"optional: pip install 'pytekt[{extra}]'"))

    tracker_dir = ".pytekt_experiments"
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

    for status in native_backends().values():
        detail = "native" if status.available else f"{status.fallback.lower()} fallback"
        lines.append(_check(f"{status.name} (C++)", status.available, detail))

    compiler = shutil.which("c++") or shutil.which("clang++") or shutil.which("g++")
    if compiler:
        lines.append(_check("C++ compiler", True, compiler))
    else:
        lines.append(_check("C++ compiler", False, "optional: install clang++ or g++ for native builds"))

    cmake = shutil.which("cmake")
    if cmake:
        lines.append(_check("cmake", True, cmake))
    else:
        lines.append(_check("cmake", False, "optional: install cmake for C++ workspaces"))

    all_required_ok = all(ok for name, ok, _ in lines if "optional" not in _.lower() and name in (
        "Python >= 3.8", "numpy", "pytekt", "tracker directory writable"
    ))

    if verbose:
        _print_report(lines, all_required_ok)
    return all_required_ok


def _print_report(lines: List[Tuple[str, bool, str]], all_ok: bool) -> None:
    use_color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    print()
    print("  PyTekt Doctor — research environment")
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
