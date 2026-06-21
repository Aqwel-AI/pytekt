"""Tests for agent web event bus."""

from aion.cli_agent.web.events import AgentEvent, EventBus


def test_event_bus_publish():
    bus = EventBus()
    bus.publish("tool_step", action="read_file", preview="ok")
    recent = bus.recent(5)
    assert len(recent) == 1
    assert recent[0]["type"] == "tool_step"


def test_agent_event_sse():
    ev = AgentEvent(type="chat_token", data={"text": "hi"})
    assert ev.to_sse().startswith("data: ")
