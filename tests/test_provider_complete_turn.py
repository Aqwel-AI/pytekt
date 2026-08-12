"""Tests for Anthropic + Gemini complete_turn parsing (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import patch

from pytekt.providers.anthropic_provider import (
    AnthropicProvider,
    _openai_messages_to_anthropic,
    _openai_tools_to_anthropic,
    _parse_anthropic_response,
)
from pytekt.providers.gemini_provider import (
    GeminiProvider,
    _openai_messages_to_gemini,
    _openai_tools_to_gemini,
    _parse_gemini_response,
)


def test_openai_tools_to_anthropic():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
            },
        }
    ]
    converted = _openai_tools_to_anthropic(tools)
    assert converted is not None
    assert converted[0]["name"] == "read_file"
    assert "input_schema" in converted[0]


def test_parse_anthropic_tool_use():
    data = {
        "content": [
            {"type": "text", "text": "Reading"},
            {
                "type": "tool_use",
                "id": "toolu_1",
                "name": "read_file",
                "input": {"path": "a.py"},
            },
        ]
    }
    turn = _parse_anthropic_response(data)
    assert turn.content == "Reading"
    assert len(turn.tool_calls) == 1
    assert turn.tool_calls[0].name == "read_file"
    assert '"path": "a.py"' in turn.tool_calls[0].arguments_json or '"path":"a.py"' in turn.tool_calls[0].arguments_json


def test_anthropic_messages_convert_tool_loop():
    system, msgs = _openai_messages_to_anthropic(
        [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "read a.py"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "read_file", "arguments": '{"path":"a.py"}'},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call_1", "content": "print(1)"},
        ]
    )
    assert system == "You are helpful"
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"][0]["type"] == "tool_use"
    assert msgs[2]["role"] == "user"
    assert msgs[2]["content"][0]["type"] == "tool_result"


def test_anthropic_complete_turn_mocked():
    provider = AnthropicProvider(api_key="test-key", model="claude-test")
    fake = {
        "content": [
            {"type": "tool_use", "id": "t1", "name": "grep", "input": {"pattern": "foo"}},
        ]
    }
    with patch("aion.providers.anthropic_provider.post_json", return_value=fake):
        turn = provider.complete_turn(
            [{"role": "user", "content": "find foo"}],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "grep",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ],
        )
    assert turn.tool_calls[0].name == "grep"


def test_openai_tools_to_gemini():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]
    converted = _openai_tools_to_gemini(tools)
    assert converted is not None
    assert converted[0]["functionDeclarations"][0]["name"] == "list_files"


def test_parse_gemini_function_call():
    data = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Calling"},
                        {"functionCall": {"name": "read_file", "args": {"path": "x.py"}}},
                    ]
                },
                "finishReason": "STOP",
            }
        ]
    }
    turn = _parse_gemini_response(data)
    assert turn.content == "Calling"
    assert turn.tool_calls[0].name == "read_file"


def test_gemini_tool_result_name_from_call_id():
    system, contents = _openai_messages_to_gemini(
        [
            {"role": "user", "content": "hi"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_abc",
                        "type": "function",
                        "function": {"name": "read_file", "arguments": "{}"},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call_abc", "content": "ok"},
        ]
    )
    assert system is None
    fr = contents[-1]["parts"][0]["functionResponse"]
    assert fr["name"] == "read_file"


def test_gemini_complete_turn_mocked():
    provider = GeminiProvider(api_key="test-key", model="gemini-2.0-flash")
    fake = {
        "candidates": [
            {
                "content": {"parts": [{"text": "done"}]},
                "finishReason": "STOP",
            }
        ]
    }
    with patch.object(provider, "_generate", return_value=fake):
        turn = provider.complete_turn([{"role": "user", "content": "hi"}])
    assert turn.content == "done"
