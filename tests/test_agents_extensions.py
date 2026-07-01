import json

import aion


class DummyProvider:
    supports_tools = True

    def complete(self, messages, **kwargs):
        return "ok"

    def complete_turn(self, messages, **kwargs):
        raise AssertionError("complete_turn should not be called in this test")


class DummyRegistry:
    def call(self, name, arguments_json):
        return json.dumps({"name": name, "arguments_json": arguments_json})


def test_agent_state_and_checkpoints(tmp_path):
    state = aion.agents.AgentState()
    state.start("fix bug", ["inspect", "edit", "test"])
    state.record_tool_call("read_file", '{"path":"x.py"}', "done")
    state.add_artifact("x.py")
    path = tmp_path / "checkpoint.json"
    aion.agents.save_checkpoint(state, path)
    loaded = aion.agents.load_checkpoint(path)
    assert loaded.goal == "fix bug"
    assert loaded.tool_history[0]["name"] == "read_file"


def test_tool_policy():
    policy = aion.agents.ToolPolicy.from_lists(
        read_only=True,
        allowlist=["read_file", "write_file"],
    )
    assert policy.validate_tool("read_file") is None
    assert policy.validate_tool("write_file") == "read_only_policy"
    assert policy.validate_tool("shell") == "tool_not_in_allowlist"


def test_retry_call_with_fallback():
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        raise RuntimeError("timeout talking to provider")

    result = aion.agents.retry_call(
        flaky,
        config=aion.agents.RetryConfig(attempts=2),
        fallback=lambda: "fallback",
    )
    assert result == "fallback"
    assert attempts["count"] == 2


def test_validator_helpers(tmp_path):
    path = tmp_path / "artifact.txt"
    path.write_text("hello", encoding="utf-8")
    assert aion.agents.is_valid_json('{"a":1}') is True
    assert aion.agents.file_exists(str(path)) is True
    report = aion.agents.validate_output('{"a":1}', require_json=True)
    assert report["valid_json"] is True


def test_artifact_tracker_and_critic():
    tracker = aion.agents.ArtifactTracker()
    tracker.add("report.md", "document", "Generated report")
    critique = aion.agents.SelfReviewAgent().review(
        "TODO finish this",
        tool_history=[],
        require_tool_use=True,
    )
    assert tracker.list()[0].path == "report.md"
    assert critique.approved is False
    assert "missing_tool_use" in critique.issues


def test_router_and_execution_graph():
    assert aion.agents.route_task("please debug this python error") == "debug"
    graph = aion.agents.ExecutionGraph()
    graph.add_node(aion.agents.ExecutionNode("a", lambda: "A"))
    graph.add_node(aion.agents.ExecutionNode("b", lambda: "B", depends_on=["a"]))
    results = graph.execute()
    assert results == {"a": "A", "b": "B"}


def test_episodic_and_vector_memory(tmp_path):
    memory = aion.agents.EpisodicMemory(tmp_path / "episodic.json")
    memory.add("fact", "Project uses Python and pytest")
    assert memory.search("pytest")[0]["kind"] == "fact"

    vector_memory = aion.agents.VectorMemory()
    vector_memory.add("physics simulations and mechanics", topic="physics")
    vector_memory.add("tokenization and NLP", topic="nlp")
    results = vector_memory.search("mechanics physics", top_k=1)
    assert results[0]["metadata"]["topic"] == "physics"


def test_observer_evals_and_human_loop():
    summary = aion.agents.summarize_observation("a\nb\nc\nd", max_lines=3)
    stats = aion.agents.observation_stats("a\n\nb")
    evaluation = aion.agents.evaluate_run(
        final_answer="Physics result with citation https://example.com",
        tool_calls=[{"name": "physics_simulate"}],
        failures=[],
        expected_keywords=["physics", "citation"],
    )
    approved = aion.agents.require_approval("delete file?", lambda prompt: "delete" in prompt)
    assert "... (1 more lines)" in summary
    assert stats["non_empty_lines"] == 2
    assert evaluation["success"] is True
    assert approved is True


def test_specialist_role_and_agent_factory():
    role = aion.agents.build_specialist_role("physics")
    agent = aion.agents.create_specialist_agent(
        "code",
        provider=DummyProvider(),
        registry=DummyRegistry(),
        tools=[],
    )
    assert role.name == "physics"
    assert "physics" in role.system_prompt.casefold()
    assert agent.system_prompt
