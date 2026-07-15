"""Tests for specialist subagents and parallel multi."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from unittest.mock import patch

from aion.cli_agent.subagent import (
    _edit_registry,
    _read_only_registry,
    _test_registry,
    run_parallel_specialists,
    run_research_subagent,
    run_specialist_subagent,
)
from aion.providers.structured import AssistantTurn


class DummyProvider:
    supports_tools = True

    def __init__(self, reply: str = "ok") -> None:
        self.reply = reply
        self.calls = 0

    def complete(self, messages: Sequence[Any], **kwargs: Any) -> str:
        self.calls += 1
        return self.reply

    def complete_turn(
        self,
        messages: Sequence[Any],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> AssistantTurn:
        self.calls += 1
        return AssistantTurn(content=self.reply, tool_calls=[])


def test_read_only_registry_has_no_write(tmp_path):
    reg = _read_only_registry(str(tmp_path))
    assert "read_file" in reg._fns
    assert "write_file" not in reg._fns


def test_edit_registry_has_write(tmp_path):
    reg = _edit_registry(str(tmp_path))
    assert "write_file" in reg._fns
    assert "edit_file" in reg._fns


def test_test_registry_has_run_command(tmp_path):
    reg = _test_registry(str(tmp_path))
    assert "run_command" in reg._fns
    assert "write_file" not in reg._fns


def test_run_specialist_explore(tmp_path):
    provider = DummyProvider("explored")
    out = run_specialist_subagent(
        provider,
        "summarize",
        kind="explore",
        workspace_root=str(tmp_path),
    )
    assert "explored" in out
    assert provider.calls >= 1


def test_run_research_alias(tmp_path):
    provider = DummyProvider("research-ok")
    out = run_research_subagent(provider, "look around", workspace_root=str(tmp_path))
    assert "research-ok" in out


def test_run_parallel_specialists(tmp_path):
    provider = DummyProvider("done")

    def fake_run(provider, query, *, kind, workspace_root, max_steps=5, test_command=None):
        return f"{kind}:{query}"

    with patch("aion.cli_agent.subagent.run_specialist_subagent", side_effect=fake_run):
        out = run_parallel_specialists(
            provider,
            "fix bug",
            workspace_root=str(tmp_path),
            kinds=["explore", "test"],
        )
    assert "## explore" in out
    assert "## test" in out
    assert "explore:fix bug" in out
    assert "## synthesis" in out
