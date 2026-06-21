"""Tests for plan mode connector hooks."""

from aion.cli_agent.connect import AgentConnector
from aion.cli_agent.tools import build_tool_registry, tools_schema
from aion.cli_agent import ui


def test_plan_mode_pending():
    session = ui.AgentSession(interaction_mode="plan")
    cfg = {"agent": {}}
    connector = AgentConnector(
        cfg=cfg,
        registry=build_tool_registry(workspace_root=".", is_trusted=False),
        tools_schema=tools_schema(is_trusted=False),
        session=session,
        is_trusted=False,
        workspace_root=".",
    )
    assert session.interaction_mode == "plan"
