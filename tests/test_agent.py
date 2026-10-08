"""
Unit and integration tests for PyTekt Agent.
Tests UndoManager, context expansion, ML tools, Bot scaffolding, Review auditor, and AgentSession.
"""

import os
from pathlib import Path
import pytest

from pytekt.agent.undo import UndoManager
from pytekt.agent.context import expand_prompt_context
from pytekt.agent.ml_tools import profile_dataset, fit_baseline_classifier
from pytekt.agent.bot_tools import scaffold_bot_project
from pytekt.agent.review import audit_git_diff
from pytekt.agent.core import AgentSession
from pytekt.tools.fake_provider import FakeToolProvider, make_tool_turn
from pytekt.providers.structured import AssistantTurn, NormalizedToolCall


def test_undo_manager_new_file(tmp_path):
    undo = UndoManager()
    fpath = tmp_path / "created.txt"
    fpath.write_text("initial text", encoding="utf-8")
    
    # Record creation (content_before=None)
    undo.record_write("created.txt", str(fpath), content_before=None)
    assert undo.can_undo()
    assert undo.history_count == 1

    msg = undo.undo_last()
    assert "Reverted creation" in msg
    assert not fpath.exists()
    assert not undo.can_undo()


def test_undo_manager_edit_file(tmp_path):
    undo = UndoManager()
    fpath = tmp_path / "edited.py"
    original = "x = 10\n"
    fpath.write_text(original, encoding="utf-8")

    # Simulate edit
    fpath.write_text("x = 20\n", encoding="utf-8")
    undo.record_edit("edited.py", str(fpath), original)

    msg = undo.undo_last()
    assert "Reverted edited.py" in msg
    assert fpath.read_text(encoding="utf-8") == original


def test_context_expansion_file(tmp_path):
    sample_file = tmp_path / "sample.py"
    sample_file.write_text("print('hello world')", encoding="utf-8")

    raw_prompt = "Explain @sample.py please"
    expanded, mentions = expand_prompt_context(raw_prompt, str(tmp_path))

    assert "@sample.py" in mentions
    assert "print('hello world')" in expanded


def test_context_expansion_git(tmp_path):
    raw_prompt = "Check current changes with @git"
    expanded, mentions = expand_prompt_context(raw_prompt, str(tmp_path))
    assert "@git" in mentions
    assert "### Git Status" in expanded


def test_ml_tools_profile_and_train(tmp_path):
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(
        "feature1,feature2,target\n"
        "1.0,2.0,0\n"
        "1.5,2.5,0\n"
        "5.0,6.0,1\n"
        "5.5,6.5,1\n"
        "1.2,2.1,0\n"
        "5.2,6.1,1\n",
        encoding="utf-8"
    )

    profile = profile_dataset(str(csv_file))
    assert profile["rows"] == 6
    assert "feature1" in profile["columns"]
    assert profile["columns"]["feature1"]["type"] == "numeric"

    train_res = fit_baseline_classifier(str(csv_file), target_column="target", model_type="gaussian_nb")
    assert train_res["status"] == "success"
    assert "accuracy" in train_res["metrics"]
    assert train_res["metrics"]["accuracy"] >= 0.0


def test_bot_tools_scaffold(tmp_path):
    res = scaffold_bot_project("my_test_bot", platform="telegram", output_dir=str(tmp_path))
    assert res["status"] == "success"
    bot_dir = tmp_path / "my_test_bot"
    assert bot_dir.is_dir()
    assert (bot_dir / "bot" / "main.py").exists() or (bot_dir / "requirements.txt").exists()


def test_review_tool_audit(tmp_path):
    res = audit_git_diff(str(tmp_path))
    assert "findings" in res
    assert "stat" in res


def test_agent_session_modes(tmp_path):
    session = AgentSession(workspace_root=str(tmp_path), provider_name="openai", model="gpt-4o")
    assert session.mode == "code"

    session.set_mode("ml")
    assert session.mode == "ml"
    tools = session._get_tools_for_mode()
    tool_names = [t["function"]["name"] for t in tools]
    assert "profile_dataset" in tool_names

    session.set_mode("bot")
    assert session.mode == "bot"
    tools = session._get_tools_for_mode()
    tool_names = [t["function"]["name"] for t in tools]
    assert "scaffold_bot_project" in tool_names

    session.set_mode("review")
    assert session.mode == "review"
    tools = session._get_tools_for_mode()
    tool_names = [t["function"]["name"] for t in tools]
    assert "audit_git_diff" in tool_names

    session.set_mode("talk")
    assert session.mode == "talk"
    assert session._get_tools_for_mode() is None


def test_agent_session_send_with_fake_provider(tmp_path):
    # Setup session with scripted FakeToolProvider
    turn = AssistantTurn(
        content="Here is the answer.",
        tool_calls=[],
        raw={},
    )
    provider = FakeToolProvider([turn])

    session = AgentSession(workspace_root=str(tmp_path), provider_name="openai")
    session.provider = provider

    reply = session.send("Hello agent")
    assert reply == "Here is the answer."
    assert len(session.messages) >= 2


def test_agent_session_send_without_key_raises_provider_error(tmp_path):
    from pytekt.providers.errors import ProviderError
    # Session initialized with no key for cloud provider
    session = AgentSession(workspace_root=str(tmp_path), provider_name="openai", api_key=None)
    with pytest.raises(ProviderError) as exc_info:
        session.send("source /venv/bin/activate")
    
    assert "/connect" in str(exc_info.value)
    assert "OPENAI_API_KEY" in str(exc_info.value)


def test_render_error_card(capsys):
    from pytekt.agent.tui import _render_error_card
    _render_error_card("OpenAI Error", "Your API key was rejected.", hint="• Type /connect to set up your key")
    captured = capsys.readouterr().out
    assert "OpenAI Error" in captured
    assert "rejected" in captured
    assert "/connect" in captured


def test_agent_session_send_with_hooks_without_key_raises_provider_error(tmp_path):
    from pytekt.providers.errors import ProviderError
    session = AgentSession(workspace_root=str(tmp_path), provider_name="openai", api_key=None)
    with pytest.raises(ProviderError) as exc_info:
        session.send_with_hooks("echo test")
    assert "/connect" in str(exc_info.value)
