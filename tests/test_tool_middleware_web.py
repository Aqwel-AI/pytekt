"""Tests for web approval handler on ToolMiddleware."""

from aion.cli_agent.tool_middleware import ToolMiddleware


def test_approval_handler_accept():
    results = []

    def handler(diff: str, path: str, tool: str, approval_id: str):
        results.append(approval_id)
        return True

    mw = ToolMiddleware(
        workspace_root=".",
        session_id="test",
        approval_gate=True,
        approval_handler=handler,
    )
    assert mw._request_approval("diff", "a.py", "write_file") is True
    assert results
