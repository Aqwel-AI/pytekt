"""ReAct (Reason + Act) agent loop."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence

from ..providers.base import ChatMessage
from ..tools.loop import tool_calls_to_message_payload
from .action_detect import looks_like_instructions_only, needs_tool_action
from .json_tools import JSON_TOOL_SYSTEM, run_json_tool_loop, tools_catalog_for_prompt
from .memory import Memory, SlidingWindowMemory

_CHAT_ROLES = frozenset({"system", "user", "assistant"})


def _messages_for_chat_completion(messages: Sequence[Dict[str, Any]]) -> List[ChatMessage]:
    """Drop tool messages and non-text roles for plain chat APIs."""
    out: List[ChatMessage] = []
    for m in messages:
        role = m.get("role", "")
        if role not in _CHAT_ROLES:
            continue
        content = m.get("content")
        if content is None:
            continue
        out.append(ChatMessage(role=role, content=str(content)))
    return out


class ReActAgent:
    """
    ReAct agent: observe -> think -> act loop.

    Uses native tool calling when the provider supports it; otherwise falls back
    to a JSON tool protocol (Ollama, Gemini chat, etc.).
    """

    def __init__(
        self,
        provider: Any,
        registry: Any,
        tools: List[Dict[str, Any]],
        *,
        system_prompt: str = (
            "You are a helpful assistant. Use the provided tools when needed "
            "to answer the user's question. Think step by step."
        ),
        memory: Optional[Memory] = None,
        max_steps: int = 20,
        on_step: Optional[Callable[..., None]] = None,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.tools = tools
        self.system_prompt = system_prompt
        self.memory: Memory = memory or SlidingWindowMemory(system_prompt=system_prompt)
        self.max_steps = max_steps
        self.on_step = on_step
        self.steps: List[Dict[str, Any]] = []
        self._tool_names = [
            t["function"]["name"]
            for t in tools
            if isinstance(t, dict) and isinstance(t.get("function"), dict)
        ]
        self._use_native_tools = bool(tools) and getattr(
            self.provider, "supports_tools", True
        )

    def run(self, user_input: str) -> str:
        """Run the agent loop for a single user query."""
        self.steps = []
        self.memory.add({"role": "user", "content": user_input})

        if not self.tools:
            return self._chat_only(user_input)

        if not needs_tool_action(user_input):
            return self._chat_only(user_input)

        if self._use_native_tools:
            return self._run_native_tools(user_input)

        return self._run_json_tools(user_input)

    def _chat_only(self, user_input: str) -> str:
        messages = self.memory.get_messages()
        answer = self.provider.complete(
            _messages_for_chat_completion(messages),
            temperature=0.2,
            max_tokens=4096,
        )
        self.memory.add({"role": "assistant", "content": answer})
        return answer

    def _run_json_tools(self, user_input: str) -> str:
        catalog = tools_catalog_for_prompt(self._tool_names)
        json_system = f"{self.system_prompt}\n\n{JSON_TOOL_SYSTEM}\n{catalog}"
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": json_system},
            {"role": "user", "content": user_input},
        ]
        answer = run_json_tool_loop(
            self.provider.complete,
            self.registry,
            messages=messages,
            tool_names=self._tool_names,
            max_steps=self.max_steps,
            on_step=self.on_step,
        )
        self.memory.add({"role": "assistant", "content": answer})
        return answer

    def _run_native_tools(self, user_input: str) -> str:
        action_task = needs_tool_action(user_input)
        nudges = 0

        for step_num in range(self.max_steps):
            messages = self.memory.get_messages()
            turn = self.provider.complete_turn(
                messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.2,
                max_tokens=4096,
            )

            if turn.tool_calls:
                asst_msg: Dict[str, Any] = {
                    "role": "assistant",
                    "content": turn.content or "",
                    "tool_calls": tool_calls_to_message_payload(turn.tool_calls),
                }
                self.memory.add(asst_msg)

                for tc in turn.tool_calls:
                    result = self.registry.call(tc.name, tc.arguments_json)
                    self.steps.append({
                        "step": step_num,
                        "action": tc.name,
                        "args": tc.arguments_json,
                        "result": result[:500],
                    })
                    if self.on_step:
                        self.on_step(step_num, tc.name, result)
                    self.memory.add({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
                nudges = 0
                continue

            answer = turn.content or ""

            if (
                action_task
                and not self.steps
                and nudges < 2
                and (
                    looks_like_instructions_only(answer)
                    or "```" in answer
                )
            ):
                nudges += 1
                self.memory.add({
                    "role": "assistant",
                    "content": answer,
                })
                self.memory.add({
                    "role": "user",
                    "content": (
                        "STOP giving instructions. Call write_file or edit_file NOW "
                        "using the tool API. Do not output shell or Python for the user."
                    ),
                })
                continue

            self.memory.add({"role": "assistant", "content": answer})
            return answer

        return self._force_finalize()

    def _force_finalize(self) -> str:
        final_messages = self.memory.get_messages()
        final_messages.append({
            "role": "user",
            "content": "Summarize what you accomplished with tools, or admit nothing was changed.",
        })
        final = self.provider.complete(
            _messages_for_chat_completion(final_messages),
            max_tokens=1024,
        )
        self.memory.add({"role": "assistant", "content": final})
        return final

    def chat(self, user_input: str) -> str:
        """Multi-turn chat: memory persists across calls."""
        return self.run(user_input)

    def reset(self) -> None:
        """Clear memory and step history."""
        self.memory.clear()
        self.steps = []
