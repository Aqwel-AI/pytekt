"""Write a temp file atomically, stream lines, print SHA-256."""
from __future__ import annotations

import tempfile
from pathlib import Path

from pytekt.io import atomic_write, file_sha256, iter_lines, verify_sha256


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "sample.txt"
        atomic_write(path, "alpha\nbeta\n")
        lines = list(iter_lines(path))
        assert lines == ["alpha", "beta"]
        h = file_sha256(path)
        assert verify_sha256(path, h)
        print("demo_atomic_checksum ok — lines =", lines, "sha256 =", h[:16] + "…")


if __name__ == "__main__":
    main()
