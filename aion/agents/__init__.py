"""
Agent framework: ReAct, planning, orchestration, state, memory, and utilities.

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

from .artifacts import Artifact, ArtifactTracker
from .checkpoints import load_checkpoint, save_checkpoint
from .critic import CritiqueResult, SelfReviewAgent
from .episodic_memory import EpisodicMemory
from .events import AgentEvent, AgentEventBus
from .evals import evaluate_run
from .execution_graph import ExecutionGraph, ExecutionNode
from .human_loop import require_approval
from .jobs import BackgroundJob, BackgroundJobQueue
from .memory import SlidingWindowMemory, SummaryMemory, TokenBudgetMemory, Memory
from .react import ReActAgent
from .planner import PlanningAgent
from .multi import MultiAgent, AgentRole
from .observer import observation_stats, summarize_observation
from .policies import ToolPolicy
from .retry import RetryConfig, retry_call
from .router import route_task
from .skills import build_specialist_role, create_specialist_agent
from .state import AgentState
from .session import RuntimeSession
from .runtime import AgentRuntime
from .validator import contains_citations, file_exists, is_valid_json, validate_output, validate_with
from .vector_memory import VectorMemory

__all__ = [
    "AgentRole",
    "AgentEvent",
    "AgentEventBus",
    "AgentRuntime",
    "AgentState",
    "Artifact",
    "ArtifactTracker",
    "BackgroundJob",
    "BackgroundJobQueue",
    "CritiqueResult",
    "EpisodicMemory",
    "ExecutionGraph",
    "ExecutionNode",
    "Memory",
    "MultiAgent",
    "PlanningAgent",
    "ReActAgent",
    "RetryConfig",
    "RuntimeSession",
    "SlidingWindowMemory",
    "SelfReviewAgent",
    "SummaryMemory",
    "ToolPolicy",
    "TokenBudgetMemory",
    "VectorMemory",
    "build_specialist_role",
    "contains_citations",
    "create_specialist_agent",
    "evaluate_run",
    "file_exists",
    "is_valid_json",
    "load_checkpoint",
    "observation_stats",
    "require_approval",
    "retry_call",
    "route_task",
    "save_checkpoint",
    "summarize_observation",
    "validate_output",
    "validate_with",
]
