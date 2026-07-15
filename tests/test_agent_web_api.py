"""Tests for agent web API."""

import json
import threading
import urllib.request

from aion.cli_agent.web.server import is_agent_web_server, run_server
from aion.cli_agent.web.service import WebAgentService


def test_web_agent_service_session():
    svc = WebAgentService(".")
    data = svc.session_dict()
    assert "connected" in data
    assert "workspace" in data


def test_list_providers():
    svc = WebAgentService(".")
    providers = svc.list_providers()
    assert any(p["id"] == "ollama" for p in providers)


def test_list_files(tmp_path):
    (tmp_path / "hello.py").write_text("x=1\n", encoding="utf-8")
    svc = WebAgentService(str(tmp_path))
    result = svc.list_files(".")
    assert any("hello.py" in e for e in result["entries"])


def test_is_agent_web_server_free():
    assert not is_agent_web_server("127.0.0.1", 3869)


def test_chat_stream_emits_start_before_done():
    svc = WebAgentService(".")
    svc.connector.agent = object()
    svc.connector.session.interaction_mode = "agent"
    svc.connector.chat = lambda _msg: "Hello from agent"

    types: list[str] = []
    for line in svc.chat_stream("hi"):
        if line.startswith("data: "):
            payload = json.loads(line[6:].strip())
            types.append(payload["type"])

    assert types[0] == "chat_start"
    assert "chat_done" in types
    assert types.index("chat_start") < types.index("chat_done")


def test_chat_stream_forwards_tool_step_before_done():
    svc = WebAgentService(".")
    svc.connector.agent = object()
    svc.connector.session.interaction_mode = "agent"

    def fake_chat(_msg: str) -> str:
        svc.connector._emit(
            "tool_step",
            step=1,
            action="read_file",
            preview="hello.py",
            result="ok",
        )
        return "Hello from agent"

    svc.connector.chat = fake_chat

    types: list[str] = []
    for line in svc.chat_stream("hi"):
        if line.startswith("data: "):
            payload = json.loads(line[6:].strip())
            types.append(payload["type"])

    assert "tool_step" in types
    assert "chat_done" in types
    assert types.index("tool_step") < types.index("chat_done")


def test_threading_server_serves_api_while_sse_open(tmp_path):
    import socket
    import time

    from aion.cli_agent.web.server import AgentWebHandler, _ThreadingHTTPServer

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    svc = WebAgentService(str(tmp_path))
    AgentWebHandler.service = svc
    server = _ThreadingHTTPServer(("127.0.0.1", port), AgentWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)

    sse_holder: list[object] = []

    def hold_sse() -> None:
        sse_holder.append(
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/events/stream", timeout=5)
        )

    sse_thread = threading.Thread(target=hold_sse, daemon=True)
    sse_thread.start()
    time.sleep(0.3)

    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/session", timeout=2) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    assert "connected" in data

    server.shutdown()
