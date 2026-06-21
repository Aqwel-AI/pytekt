"""Tests for disconnect key clearing."""

from aion.cli_agent.connect import AgentConnector
from aion.cli_agent.ui.status import AgentSession
from aion.tools.registry import ToolRegistry


def test_disconnect_clears_provider_keys():
    cfg = {"keys": {"nvidia_api_key": "secret", "openai_api_key": "other"}}
    session = AgentSession()
    connector = AgentConnector(
        cfg=cfg,
        registry=ToolRegistry(),
        tools_schema=[],
        session=session,
        is_trusted=False,
    )
    session.connected = True
    session.provider = "nvidia"

    cleared = connector.disconnect(clear_keys_for="nvidia", disconnect_session=True)

    assert cleared is True
    assert "nvidia_api_key" not in cfg.get("keys", {})
    assert cfg["keys"]["openai_api_key"] == "other"
    assert session.connected is False


def test_disconnect_keeps_keys_by_default():
    cfg = {"keys": {"nvidia_api_key": "secret"}}
    session = AgentSession()
    connector = AgentConnector(
        cfg=cfg,
        registry=ToolRegistry(),
        tools_schema=[],
        session=session,
        is_trusted=False,
    )

    cleared = connector.disconnect(forget_saved=False, disconnect_session=True)

    assert cleared is False
    assert cfg["keys"]["nvidia_api_key"] == "secret"


def test_keys_only_does_not_disconnect_session():
    cfg = {"keys": {"openai_api_key": "secret"}}
    session = AgentSession()
    connector = AgentConnector(
        cfg=cfg,
        registry=ToolRegistry(),
        tools_schema=[],
        session=session,
        is_trusted=False,
    )
    session.connected = True
    session.provider = "nvidia"

    cleared = connector.disconnect(
        clear_keys_for="openai",
        disconnect_session=False,
    )

    assert cleared is True
    assert session.connected is True
    assert session.provider == "nvidia"
