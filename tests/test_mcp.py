"""Tests for MCP registration, schemas, and prefs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import patch

from aion.cli_agent.mcp import (
    MCPRegisterResult,
    MCPServer,
    _schema_from_mcp_tool,
    register_mcp_tools,
)
from aion.cli_agent.session_prefs import save_mcp_servers, saved_mcp_servers
from aion.tools.registry import ToolRegistry


def test_schema_from_mcp_tool():
    schema = _schema_from_mcp_tool(
        "mcp_fs_read",
        {
            "name": "read",
            "description": "Read a path",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    )
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "mcp_fs_read"
    assert "path" in schema["function"]["parameters"]["properties"]


def test_save_mcp_servers(tmp_path, monkeypatch):
    cfg_path = tmp_path / "aion.yaml"
    monkeypatch.setenv("AION_CONFIG_PATH", str(cfg_path))
    from aion.cli_agent import config as cfg_mod

    monkeypatch.setattr(cfg_mod, "CONFIG_PATH", str(cfg_path))
    cfg: Dict[str, Any] = {}
    save_mcp_servers(cfg, [{"name": "demo", "command": "echo", "args": ["hi"]}])
    assert saved_mcp_servers(cfg)[0]["name"] == "demo"


def test_register_mcp_tools_merges_schemas():
    registry = ToolRegistry()

    class FakeServer(MCPServer):
        def __init__(self, name: str, command: str, args: Optional[List[str]] = None) -> None:
            super().__init__(name, command, args)
            self.started = False
            self.stopped = False

        def start(self) -> None:
            self.started = True
            self._initialized = True

        def stop(self) -> None:
            self.stopped = True

        def list_tools(self) -> List[Dict[str, Any]]:
            return [
                {
                    "name": "ping",
                    "description": "Ping",
                    "inputSchema": {"type": "object", "properties": {}},
                }
            ]

        def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
            return "pong"

    with patch("aion.cli_agent.mcp.MCPServer", FakeServer):
        result = register_mcp_tools(
            registry,
            [{"name": "demo", "command": "fake", "args": []}],
        )
    assert isinstance(result, MCPRegisterResult)
    assert result.count == 1
    assert result.schemas[0]["function"]["name"] == "mcp_demo_ping"
    assert registry.call("mcp_demo_ping", "{}") == "pong"
    assert result.errors == []
    result.servers[0].stop()
    assert result.servers[0].stopped is True


def test_register_mcp_reports_errors():
    registry = ToolRegistry()

    class BoomServer(MCPServer):
        def start(self) -> None:
            raise RuntimeError("boom")

    with patch("aion.cli_agent.mcp.MCPServer", BoomServer):
        result = register_mcp_tools(
            registry,
            [{"name": "bad", "command": "nope"}],
        )
    assert result.count == 0
    assert result.errors
    assert "boom" in result.errors[0]
