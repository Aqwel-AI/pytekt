"""Setuptools install hooks — show animated PyTekt splash after install/upgrade."""

from __future__ import annotations

import os
import subprocess
import sys

from setuptools.command.develop import develop
from setuptools.command.install import install

try:
    from setuptools.command.editable_wheel import editable_wheel as _editable_wheel
except ImportError:  # pragma: no cover
    _editable_wheel = None


def _run_splash() -> None:
    """Show the PyTekt install animation without breaking installation."""
    if os.environ.get("PYTEKT_NO_SPLASH"):
        return
    try:
        # Subprocess keeps the animation on a real TTY after pip finishes writing.
        subprocess.run(
            [
                sys.executable,
                "-c",
                "from pytekt.install_splash import maybe_show_install_splash; "
                "maybe_show_install_splash()",
            ],
            check=False,
        )
    except Exception:
        try:
            from pytekt.install_splash import maybe_show_install_splash

            maybe_show_install_splash()
        except Exception:
            pass


class InstallCommand(install):
    """Custom install that prints the PyTekt install animation."""

    def run(self) -> None:
        super().run()
        _run_splash()


class DevelopCommand(develop):
    """Custom editable install — same celebration screen."""

    def run(self) -> None:
        super().run()
        _run_splash()


if _editable_wheel is not None:

    class EditableWheelCommand(_editable_wheel):
        """Editable wheel install (``pip install -e .`` on modern setuptools)."""

        def run(self) -> None:
            super().run()
            _run_splash()

else:  # pragma: no cover

    class EditableWheelCommand(develop):  # type: ignore[no-redef]
        """Fallback when setuptools has no editable_wheel command."""

        pass
