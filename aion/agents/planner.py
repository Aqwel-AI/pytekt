"""Planning agent: decompose a task into resumable sub-steps, then execute each."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PlanStep:
    description: str
    status: str = "pending"  # pending | running | done | failed | blocked
    result: str = ""
    depends_on: List[int] = field(default_factory=list)
    retries: int = 0
    max_retries: int = 1


class PlanningAgent:
    """
    Agent that first generates a plan, then executes each step with retries and resumability.
    """

    def __init__(
        self,
        provider: Any,
        registry: Any,
        tools: List[Dict[str, Any]],
        *,
        system_prompt: str = (
            "You are a planning assistant. When given a task, first output a numbered "
            "plan of steps as a JSON array of strings. Then execute each step using tools."
        ),
        max_steps_per_action: int = 5,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_steps_per_action = max_steps_per_action
        self.plan: List[PlanStep] = []
        self.original_task: str = ""

    def run(self, task: str) -> str:
        """Plan and execute a task. Returns the final answer."""
        self.original_task = task
        self.plan = self._generate_plan(task)
        self.execute_plan()
        return self._finalize(task)

    def _finalize(self, task: str) -> str:
        from ..providers.base import ChatMessage

        results = [
            f"- {step.description}: {step.result or step.status}"
            for step in self.plan
        ]
        summary_prompt = (
            f"Task: {task}\n\nCompleted steps:\n" + "\n".join(results) +
            "\n\nPlease provide a final comprehensive answer."
        )
        return self.provider.complete([
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=summary_prompt),
        ])

    def _generate_plan(self, task: str) -> List[PlanStep]:
        from ..providers.base import ChatMessage

        prompt = (
            "Break this task into 2-6 clear steps. Return ONLY a JSON array of strings.\n\n"
            f"Task: {task}"
        )
        response = self.provider.complete([
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=prompt),
        ])
        try:
            start = response.index("[")
            end = response.rindex("]") + 1
            steps = json.loads(response[start:end])
            plan = [PlanStep(description=s) for s in steps]
        except (ValueError, json.JSONDecodeError):
            plan = [PlanStep(description=task)]
        for index, step in enumerate(plan):
            if index > 0:
                step.depends_on = [index - 1]
        return plan

    def _execute_step(self, step: PlanStep, original_task: str) -> str:
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"Original task: {original_task}\n"
                f"Current step: {step.description}\n"
                "Complete this step using available tools, then respond with the result."
            )},
        ]
        for _ in range(self.max_steps_per_action):
            turn = self.provider.complete_turn(messages, tools=self.tools, temperature=0.2)
            if turn.tool_calls:
                asst: Dict[str, Any] = {"role": "assistant", "content": turn.content or ""}
                from ..tools.loop import tool_calls_to_message_payload
                asst["tool_calls"] = tool_calls_to_message_payload(turn.tool_calls)
                messages.append(asst)
                for tc in turn.tool_calls:
                    result = self.registry.call(tc.name, tc.arguments_json)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
                continue
            return turn.content or ""
        return "Step completed (max iterations reached)."

    def execute_plan(self) -> None:
        """Execute the current plan with dependency checks and retries."""
        for index, step in enumerate(self.plan):
            if any(self.plan[dep].status != "done" for dep in step.depends_on):
                step.status = "blocked"
                step.result = "Blocked by unmet dependency."
                continue
            while step.retries <= step.max_retries:
                step.status = "running"
                result = self._execute_step(step, self.original_task)
                step.result = result
                if result and not result.casefold().startswith("error:"):
                    step.status = "done"
                    break
                step.retries += 1
            else:
                step.status = "failed"
            if step.status not in {"done", "failed"}:
                step.status = "failed"

    def get_plan_summary(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": step.description,
                "status": step.status,
                "depends_on": step.depends_on,
                "retries": step.retries,
                "result": step.result[:200],
            }
            for step in self.plan
        ]

    def save(self, path: str) -> Path:
        """Persist the current plan to a JSON file."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                {"task": self.original_task, "plan": [asdict(step) for step in self.plan]},
                indent=2,
            ),
            encoding="utf-8",
        )
        return target

    def load(self, path: str) -> None:
        """Load a previously saved plan."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.original_task = data.get("task", "")
        self.plan = [PlanStep(**item) for item in data.get("plan", [])]
