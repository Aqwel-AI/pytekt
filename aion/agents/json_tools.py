"""JSON tool-calling protocol for models without native function calling."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, List, Optional

JSON_TOOL_SYSTEM = """
You are a coding agent with REAL filesystem tools. The runtime executes tools for you.

CONVERSATION (greetings, small talk, general questions, explanations):
- Do NOT call tools.
- Reply with ONLY: {"done":true,"message":"Your helpful answer here"}

CODING TASKS (create/edit files, search the repo, run commands):
- Use tools only when the user asks to change or inspect the project.
- Output ONLY one JSON object (no markdown, no extra text).

Call a tool:
{"tool":"read_file","arguments":{"path":"aion/cli.py"}}

Paths MUST be relative to the workspace (e.g. "README.md", "aion/agents/react.py").
NEVER use absolute paths or guess paths like project.py unless the user named them.

Other tools: read_file, edit_file, list_files, grep, glob, run_command (same JSON shape).

When finished:
{"done":true,"message":"Short summary of what you did"}

If you need a tool result before continuing, wait — you will receive tool output in the next message.
"""


def tools_catalog_for_prompt(tool_names: List[str]) -> str:
    return "Available tool names: " + ", ".join(sorted(tool_names))


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    if not text:
        return None
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1))
        except json.JSONDecodeError:
            pass
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def run_json_tool_loop(
    complete_fn: Callable[..., str],
    registry: Any,
    *,
    messages: List[Dict[str, str]],
    tool_names: List[str],
    max_steps: int = 20,
    on_step: Optional[Callable[..., None]] = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
) -> str:
    """
    Run agent loop using JSON tool calls in model text (for Ollama / chat-only APIs).
    """
    from ..providers.base import ChatMessage

    working = list(messages)
    for step in range(max_steps):
        reply = complete_fn(
            [ChatMessage(role=m["role"], content=m["content"]) for m in working],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        parsed = extract_json_object(reply)
        if not parsed:
            plain = reply.strip()
            if plain and '"tool"' not in plain.lower():
                return plain
            working.append({"role": "assistant", "content": reply})
            working.append({
                "role": "user",
                "content": (
                    "Invalid response. Output ONLY JSON: "
                    '{"done":true,"message":"..."} for chat, or '
                    '{"tool":"read_file","arguments":{"path":"relative/path.py"}} for tools. '
                    "Use workspace-relative paths only."
                ),
            })
            continue

        if parsed.get("done"):
            msg = parsed.get("message") or parsed.get("answer") or "Done."
            return str(msg)

        tool = parsed.get("tool")
        if not tool:
            working.append({"role": "assistant", "content": reply})
            working.append({
                "role": "user",
                "content": 'Output JSON with "tool" and "arguments", or {"done":true,"message":"..."}.',
            })
            continue

        name = str(tool)
        if name not in tool_names:
            working.append({"role": "assistant", "content": reply})
            working.append({
                "role": "user",
                "content": f"Unknown tool {name!r}. Use one of: {', '.join(tool_names)}",
            })
            continue

        args = parsed.get("arguments") or {}
        if not isinstance(args, dict):
            args = {}
        result = registry.call(name, json.dumps(args))
        if on_step:
            on_step(step, name, result)
        working.append({"role": "assistant", "content": reply})
        working.append({
            "role": "user",
            "content": f"Tool {name} result:\n{result}\n\nContinue (more JSON) or finish with {{\"done\":true,\"message\":\"...\"}}.",
        })

    return "Stopped after max steps. Try again or use OpenAI (gpt-4o) for native tool calling."
