"""Run ``run_tool_loop`` with ``FakeToolProvider`` (no HTTP)."""
from __future__ import annotations

from pytekt.providers.structured import AssistantTurn, NormalizedToolCall
from pytekt.tools import FakeToolProvider, ToolRegistry, function_tool, make_tool_turn, run_tool_loop


def add(a: float, b: float) -> float:
    return float(a) + float(b)


def main() -> None:
    reg = ToolRegistry()
    reg.register("add", add, required_arg_keys=["a", "b"])
    tools = [
        function_tool(
            "add",
            "Add two numbers.",
            properties={
                "a": {"type": "number", "description": "First summand"},
                "b": {"type": "number", "description": "Second summand"},
            },
            required=["a", "b"],
        )
    ]
    tc = NormalizedToolCall(
        id="call_demo_1",
        name="add",
        arguments_json='{"a": 2, "b": 3}',
    )
    turns: list[AssistantTurn] = [
        make_tool_turn([tc], content=None),
        AssistantTurn(content="The sum is 5.", tool_calls=[], raw={}),
    ]
    provider = FakeToolProvider(turns)
    messages: list[dict] = [{"role": "user", "content": "What is 2 + 3? Use add."}]
    final, _ = run_tool_loop(provider, messages, tools, reg, max_rounds=4)
    assert final == "The sum is 5."
    print("demo_tool_loop ok — final:", final)


if __name__ == "__main__":
    main()
