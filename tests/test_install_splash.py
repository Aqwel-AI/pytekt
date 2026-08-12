"""Tests for install splash (static mode, no TTY animation)."""

import os
from pathlib import Path

from pytekt.install_splash import (
    maybe_show_install_splash,
    should_show_install_splash,
    show_install_splash,
)


def test_static_splash(capsys):
    os.environ["PYTEKT_NO_SPLASH"] = "1"
    try:
        show_install_splash(animated=False, version="0.2.0-test")
    finally:
        os.environ.pop("PYTEKT_NO_SPLASH", None)
    out = capsys.readouterr().out
    assert "PyTekt" in out
    assert "Aksel Aghajanyan" in out
    assert "Aqwel AI Team" in out
    assert "100%" in out
    assert "Installation complete" in out
    assert "Install Overview" not in out
    assert "█████╗" in out or "PyTekt" in out or "PyTekt" in out


def test_maybe_show_respects_no_splash(capsys):
    os.environ["PYTEKT_NO_SPLASH"] = "1"
    try:
        assert should_show_install_splash() is False
        maybe_show_install_splash()
    finally:
        os.environ.pop("PYTEKT_NO_SPLASH", None)
    assert capsys.readouterr().out == ""


def test_marker_suppresses_repeat(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTEKT_NO_SPLASH", "1")
    assert should_show_install_splash() is False
    monkeypatch.delenv("PYTEKT_NO_SPLASH", raising=False)
    monkeypatch.setattr(
        "pytekt.install_splash._state_dir",
        lambda: Path(tmp_path),
    )
    monkeypatch.setattr("pytekt.install_splash._package_version", lambda: "9.9.9-test")
    # Non-TTY → still false
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)
    assert should_show_install_splash() is False
