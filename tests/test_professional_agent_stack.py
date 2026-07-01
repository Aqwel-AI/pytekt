from __future__ import annotations

import json

import aion
from aion.cli_agent.edit_history import EditHistory
from aion.cli_agent.project import discover_project
from aion.cli_agent.runtime_models import ValidationResult
from aion.cli_agent.tool_middleware import ToolMiddleware
from aion.providers.adapter import ProviderAdapter, cached_model_metadata


def test_edit_history_rolls_back_task(tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("one\n", encoding="utf-8")
    history = EditHistory("session", base_dir=str(tmp_path / ".state"))
    history.snapshot_before(str(tmp_path), "a.txt", task_id="task1")
    path.write_text("two\n", encoding="utf-8")
    actions = history.rollback_task(str(tmp_path), "task1")
    assert actions == ["Restored a.txt"]
    assert path.read_text(encoding="utf-8") == "one\n"


def test_tool_middleware_blocks_shell_disabled(tmp_path):
    middleware = ToolMiddleware(
        workspace_root=str(tmp_path),
        session_id="sess",
        safety_mode="shell-disabled",
        edit_history=EditHistory("sess", base_dir=str(tmp_path / ".state")),
    )

    result = middleware.execute("run_command", {"command": "pytest"}, lambda **_: "ok")
    assert "shell-disabled" in result


def test_tool_middleware_validates_and_rolls_back_bad_python(tmp_path):
    source = tmp_path / "bad.py"
    source.write_text("print('ok')\n", encoding="utf-8")
    middleware = ToolMiddleware(
        workspace_root=str(tmp_path),
        session_id="sess",
        edit_history=EditHistory("sess", base_dir=str(tmp_path / ".state")),
        validate_after_edits=False,
    )
    middleware.start_task("break python file")

    def writer(**kwargs):
        source.write_text(kwargs["content"], encoding="utf-8")
        return "Wrote bad.py"

    result = middleware.execute(
        "write_file",
        {"path": "bad.py", "content": "def broken(:\n    pass\n"},
        writer,
    )
    middleware.finalize_task(rollback_on_failure=True)

    assert "Validation failed" in result
    assert source.read_text(encoding="utf-8") == "print('ok')\n"


def test_project_intelligence_detects_framework_and_build(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "app",
                "scripts": {"test": "vitest", "lint": "eslint .", "build": "vite build"},
                "dependencies": {"react": "^18.0.0"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("Contributing\n", encoding="utf-8")
    info = discover_project(str(tmp_path))
    assert info.framework == "react"
    assert info.build_command == "npm run build"
    assert info.dependency_manager == "npm"
    assert any("CONTRIBUTING" in item for item in info.conventions)


def test_provider_adapter_metadata_and_cache():
    class DummyProvider:
        supports_tools = True

        def complete(self, messages, **kwargs):
            return "ok"

    adapter = ProviderAdapter(DummyProvider(), provider_name="nvidia", model="meta/llama-3.1-8b-instruct")
    metadata = adapter.metadata()
    cached = cached_model_metadata("nvidia", "meta/llama-3.1-8b-instruct")
    assert metadata["supports_tools"] is True
    assert cached["family"] == "llama"


def test_planning_agent_save_load_and_status(tmp_path):
    class DummyTurn:
        tool_calls = []
        content = "done"

    class DummyProvider:
        def complete(self, messages, **kwargs):
            return '["inspect", "edit"]'

        def complete_turn(self, messages, **kwargs):
            return DummyTurn()

    planner = aion.agents.PlanningAgent(DummyProvider(), registry=None, tools=[])
    planner.run("fix issue")
    assert planner.plan[0].status == "done"
    path = tmp_path / "plan.json"
    planner.save(str(path))
    restored = aion.agents.PlanningAgent(DummyProvider(), registry=None, tools=[])
    restored.load(str(path))
    assert restored.original_task == "fix issue"
    assert restored.plan[1].description == "edit"
