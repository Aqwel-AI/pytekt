"""
Agent framework: ReAct, planning, multi-agent orchestration, memory.

Build autonomous agents that use :mod:`aion.providers` for LLM calls and
:mod:`aion.tools` for tool execution. Includes conversation memory
strategies (sliding window, summary, token-budget).

Examples
--------
>>> from aion.agents import ReActAgent
>>> from aion.providers import OpenAIProvider, NvidiaProvider
>>> from aion.tools import ToolRegistry, function_tool
>>> agent = ReActAgent(provider=OpenAIProvider(), registry=registry, tools=tools)
>>> result = agent.run("What is 2 + 2?")
"""

from .memory import SlidingWindowMemory, SummaryMemory, TokenBudgetMemory, Memory
from .react import ReActAgent
from .planner import PlanningAgent
from .multi import MultiAgent, AgentRole

__all__ = [
    "AgentRole",
    "Memory",
    "MultiAgent",
    "PlanningAgent",
    "ReActAgent",
    "SlidingWindowMemory",
    "SummaryMemory",
    "TokenBudgetMemory",
]
