"""Tests for installer preflight, logging, themes, and recovery flow."""

from pathlib import Path

from aion import installer


def test_preflight_local_skips_network():
    checks = installer._preflight_checks(local=True)

    assert any(label == "Network" and status == "SKIP" for label, status, _, _ in checks)
    assert installer._preflight_ok(checks)


def test_install_log_is_written(tmp_path, monkeypatch):
    log_path = tmp_path / "logs" / "install.log"
    monkeypatch.setattr(installer, "INSTALL_LOG_PATH", log_path)

    installer._append_install_log("test event")

    assert log_path.read_text(encoding="utf-8").endswith("test event\n")


def test_first_run_welcome_is_shown_once(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(installer, "FIRST_RUN_MARKER", Path(tmp_path) / ".first_run_complete")

    installer._print_first_run_welcome(color=False)
    first_output = capsys.readouterr().out
    installer._print_first_run_welcome(color=False)
    second_output = capsys.readouterr().out

    assert "AION ONLINE" in first_output
    assert second_output == ""


def test_failed_install_can_retry(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("CI", "1")
    monkeypatch.setattr(installer.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(installer, "choose_profile", lambda **_: "core")
    monkeypatch.setattr(installer, "choose_full_install", lambda **_: False)
    monkeypatch.setattr(installer, "_choose_failure_action", lambda **_: "retry")
    monkeypatch.setattr(installer, "FIRST_RUN_MARKER", Path(tmp_path) / ".first_run_complete")
    monkeypatch.setattr(installer, "INSTALL_LOG_PATH", Path(tmp_path) / "install.log")

    attempts = []

    def fake_install(command, *, color):
        attempts.append(command)
        return 1 if len(attempts) == 1 else 0

    monkeypatch.setattr(installer, "_run_install", fake_install)

    assert installer.main(["--yes"]) == 0
    assert len(attempts) == 2
    assert "AION ONLINE" in capsys.readouterr().out
