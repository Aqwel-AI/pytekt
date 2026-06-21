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
