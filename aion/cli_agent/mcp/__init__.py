"""MCP JSON-RPC client (stdio) for optional external tools."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from ...tools.registry import ToolRegistry
from ...tools.schemas import function_tool


@dataclass
class MCPRegisterResult:
    """Outcome of registering MCP servers into a tool registry."""

    count: int = 0
    schemas: List[Dict[str, Any]] = field(default_factory=list)
    servers: List["MCPServer"] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    tool_names: List[str] = field(default_factory=list)


class MCPServer:
    """Spawn an MCP server subprocess and call list_tools / call_tool."""

    def __init__(self, name: str, command: str, args: Optional[List[str]] = None) -> None:
        self.name = name
        self.command = command
        self.args = args or []
        self._proc: Optional[subprocess.Popen[str]] = None
        self._req_id = 0
        self._initialized = False
        self._tool_defs: List[Dict[str, Any]] = []

    def start(self) -> None:
        self._proc = subprocess.Popen(
            [self.command, *self.args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._initialize()

    def stop(self) -> None:
        proc = self._proc
        self._proc = None
        self._initialized = False
        if proc is None:
            return
        try:
            if proc.stdin:
                try:
                    proc.stdin.close()
                except Exception:
                    pass
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        except Exception:
            pass

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
            err = data["error"]
            raise RuntimeError(err if isinstance(err, str) else json.dumps(err))
        return data.get("result")

    def _notify(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        if not self._proc or not self._proc.stdin:
            raise RuntimeError("MCP server not started")
        msg = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        self._proc.stdin.write(json.dumps(msg) + "\n")
        self._proc.stdin.flush()

    def _initialize(self) -> None:
        self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "aion-agent", "version": "0.2.0"},
            },
        )
        try:
            self._notify("notifications/initialized")
        except Exception:
            pass
        self._initialized = True

    def list_tools(self) -> List[Dict[str, Any]]:
        result = self._request("tools/list")
        tools = result.get("tools", []) if isinstance(result, dict) else []
        self._tool_defs = list(tools) if isinstance(tools, list) else []
        return self._tool_defs

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        if isinstance(result, dict):
            content = result.get("content")
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, dict) and "text" in first:
                    return str(first["text"])
        return str(result)


def _schema_from_mcp_tool(registered_name: str, tool: Dict[str, Any]) -> Dict[str, Any]:
    desc = str(tool.get("description") or f"MCP tool {tool.get('name', registered_name)}")
    schema = tool.get("inputSchema") or tool.get("input_schema") or {}
    if not isinstance(schema, dict):
        schema = {}
    properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    required = schema.get("required") if isinstance(schema.get("required"), list) else []
    return function_tool(
        registered_name,
        desc,
        properties=dict(properties),
        required=[str(r) for r in required],
    )


def register_mcp_tools(
    registry: ToolRegistry,
    servers: List[Dict[str, Any]],
) -> MCPRegisterResult:
    """Register MCP tools into registry and return schemas + live server handles."""
    result = MCPRegisterResult()
    for spec in servers:
        name = str(spec.get("name") or "mcp")
        cmd = spec.get("command")
        if not cmd:
            result.errors.append(f"{name}: missing command")
            continue
        args = spec.get("args") or []
        if not isinstance(args, list):
            args = [str(args)]
        server = MCPServer(name, str(cmd), [str(a) for a in args])
        try:
            server.start()
            for tool in server.list_tools():
                if not isinstance(tool, dict):
                    continue
                tname = tool.get("name")
                if not tname:
                    continue
                mcp_name = f"mcp_{name}_{tname}"

                def _make_call(s: MCPServer, tn: str) -> Callable[..., str]:
                    def _call(**kwargs: Any) -> str:
                        return s.call_tool(tn, kwargs)

                    return _call

                registry.register(mcp_name, _make_call(server, str(tname)))
                result.schemas.append(_schema_from_mcp_tool(mcp_name, tool))
                result.tool_names.append(mcp_name)
                result.count += 1
            result.servers.append(server)
        except Exception as e:
            server.stop()
            result.errors.append(f"{name}: {e}")
            continue
    return result


def stop_mcp_servers(servers: List[MCPServer]) -> None:
    for server in servers:
        try:
            server.stop()
        except Exception:
            pass
