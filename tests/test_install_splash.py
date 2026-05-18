"""Tests for install splash (static mode, no TTY animation)."""

import os

from aion.install_splash import show_install_splash, INSTALL_SECTIONS


def test_install_sections_nonempty():
    assert len(INSTALL_SECTIONS) >= 4
    names = [m[1] for _s, mods in INSTALL_SECTIONS for m in mods]
    assert "models" in names
    assert "ui" in names


def test_static_splash(capsys):
    os.environ["AION_NO_SPLASH"] = "1"
    try:
        show_install_splash(animated=False, version="0.2.0-test")
    finally:
        os.environ.pop("AION_NO_SPLASH", None)
    out = capsys.readouterr().out
    assert "Aqwel-Aion" in out
    assert "PREPROCESSING" in out or "preprocessing" in out
    assert "Installation complete" in out
