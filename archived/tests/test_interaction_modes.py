"""Tests for interaction modes."""

from pytekt.cli_agent.connect import AgentConnector
from pytekt.cli_agent.constants import normalize_interaction_mode
from pytekt.cli_agent.session_prefs import save_interaction_mode, saved_interaction_mode
from pytekt.cli_agent.ui.status import AgentSession
from pytekt.tools.registry import ToolRegistry


def test_normalize_interaction_mode():
    assert normalize_interaction_mode("plain") == "plain"
    assert normalize_interaction_mode("DEBUG") == "debug"
    assert normalize_interaction_mode("unknown") is None


def test_save_interaction_mode():
    cfg: dict = {}
    save_interaction_mode(cfg, "debug")
    assert saved_interaction_mode(cfg) == "debug"


def test_plain_mode_disables_tools():
    session = AgentSession(interaction_mode="plain")
    connector = AgentConnector(
        cfg={},
        registry=ToolRegistry(),
        tools_schema=[{"type": "function", "function": {"name": "read_file"}}],
        session=session,
        is_trusted=True,
    )
    assert connector._tools_for_session() == []


def test_agent_mode_keeps_tools():
    session = AgentSession(interaction_mode="agent")
    connector = AgentConnector(
        cfg={},
        registry=ToolRegistry(),
        tools_schema=[],
        session=session,
        is_trusted=True,
        workspace_root=".",
    )
    tools = connector._tools_for_session()
    names = [t["function"]["name"] for t in tools]
    assert "read_file" in names
