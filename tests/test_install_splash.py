"""Tests for install splash (static mode, no TTY animation)."""

import os

from aion.install_splash import show_install_splash


def test_static_splash(capsys):
    os.environ["AION_NO_SPLASH"] = "1"
    try:
        show_install_splash(animated=False, version="0.2.0-test")
    finally:
        os.environ.pop("AION_NO_SPLASH", None)
    out = capsys.readouterr().out
    assert "Aqwel-Aion" in out
    assert "Aksel Aghajanyan" in out
    assert "Aqwel AI Team" in out
    assert "100%" in out
    assert "Installation complete" in out
    assert "Install Overview" not in out
