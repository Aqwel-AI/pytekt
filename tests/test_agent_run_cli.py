"""Tests for headless agent module."""

from aion.cli_agent.headless import run_headless_agent


def test_headless_invalid_provider(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def fake_connect(*args, **kwargs):
        return False

    import aion.cli_agent.headless as headless

    monkeypatch.setattr(headless.AgentConnector, "connect", fake_connect)
    code = run_headless_agent(task="hi", provider="nvidia", yes=True)
    assert code == 1
