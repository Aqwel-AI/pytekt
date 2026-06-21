"""Minimal MCP JSON-RPC client (optional)."""

from __future__ import annotations

import json
import subprocess
from typing import Any, Callable, Dict, List, Optional

from ...tools.registry import ToolRegistry
from ...tools.schemas import function_tool


class MCPServer:
    """Spawn an MCP server subprocess and call list_tools / call_tool."""

    def __init__(self, name: str, command: str, args: Optional[List[str]] = None) -> None:
        self.name = name
        self.command = command
        self.args = args or []
        self._proc: Optional[subprocess.Popen[str]] = None
        self._req_id = 0

    def start(self) -> None:
        self._proc = subprocess.Popen(
            [self.command, *self.args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self._proc or not self._proc.stdin or not self._proc.stdout:
            raise RuntimeError("MCP server not started")
        self._req_id += 1
        msg = {"jsonrpc": "2.0", "id": self._req_id, "method": method, "params": params or {}}
        self._proc.stdin.write(json.dumps(msg) + "\n")
        self._proc.stdin.flush()
        line = self._proc.stdout.readline()
        if not line:
            raise RuntimeError("MCP server closed stdout")
        data = json.loads(line)
        if "error" in data:
            raise RuntimeError(data["error"])
        return data.get("result")

    def list_tools(self) -> List[Dict[str, Any]]:
        try:
            result = self._request("tools/list")
            return result.get("tools", []) if isinstance(result, dict) else []
        except Exception:
            return []

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        if isinstance(result, dict):
            content = result.get("content")
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, dict) and "text" in first:
                    return str(first["text"])
        return str(result)


def register_mcp_tools(
    registry: ToolRegistry,
    servers: List[Dict[str, Any]],
) -> int:
    """Register MCP tools into registry; returns count registered."""
    count = 0
    for spec in servers:
        name = spec.get("name", "mcp")
        cmd = spec.get("command")
        if not cmd:
            continue
        server = MCPServer(name, cmd, spec.get("args"))
        try:
            server.start()
            for tool in server.list_tools():
                tname = tool.get("name")
                if not tname:
                    continue
                mcp_name = f"mcp_{name}_{tname}"

                def _make_call(s: MCPServer, tn: str) -> Callable[..., str]:
                    def _call(**kwargs: Any) -> str:
                        return s.call_tool(tn, kwargs)

                    return _call

                registry.register(mcp_name, _make_call(server, tname))
                count += 1
        except Exception:
            continue
    return count
