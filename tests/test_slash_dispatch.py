"""Tests for headless slash dispatch."""

from aion.cli_agent.slash_dispatch import dispatch_slash
from aion.cli_agent.web.service import WebAgentService


def test_dispatch_slash_mode():
    svc = WebAgentService(".")
    result = dispatch_slash(
        "/mode plan",
        connector=svc.connector,
        workspace=svc.workspace_root,
    )
    assert result["ok"] is True
    assert svc.connector.session.interaction_mode == "plan"


def test_web_dispatch_slash_mode():
    svc = WebAgentService(".")
    result = svc.dispatch_slash("/mode agent")
    assert result["ok"] is True
    assert result.get("mode") == "agent"


def test_dispatch_slash_help():
    svc = WebAgentService(".")
    result = dispatch_slash(
        "/help",
        connector=svc.connector,
        workspace=svc.workspace_root,
    )
    assert result["ok"] is True
    assert "/mode" in result["response"]
