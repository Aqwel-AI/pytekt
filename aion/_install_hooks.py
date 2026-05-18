"""Setuptools install hooks — show animated splash after ``pip install``."""

from __future__ import annotations

from setuptools.command.develop import develop
from setuptools.command.install import install


def _run_splash() -> None:
    try:
        from aion.install_splash import show_install_splash

        show_install_splash(animated=True)
    except Exception:
        # Never break installation
        pass


class InstallCommand(install):
    """Custom install that prints the Aion install animation."""

    def run(self) -> None:
        super().run()
        _run_splash()


class DevelopCommand(develop):
    """Custom editable install — same celebration screen."""

    def run(self) -> None:
        super().run()
        _run_splash()
