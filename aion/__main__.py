"""
Run the CLI without relying on the ``aion`` shell command (PATH-safe).

    python3 -m aion monitor
    python3 -m aion --help

If ``aion`` is not found after ``pip install``, your Python *scripts* directory
is not on ``PATH`` (common with python.org installs on macOS). Use the command
above or add that ``bin`` directory to ``PATH``.
"""

from aion.cli import main

if __name__ == "__main__":
    main()
