"""
LLM output evaluation: similarity, faithfulness, toxicity, cost tracking.

Tools for assessing the quality, safety, and cost of LLM outputs. Works
with :mod:`aion.embed` for semantic similarity and :mod:`aion.providers`
for cost estimation.

Examples
--------
>>> from aion.llm_eval import semantic_similarity, estimate_cost
>>> semantic_similarity("The cat sat", "A cat was sitting")
0.87
>>> estimate_cost("openai", prompt_tokens=500, completion_tokens=200)
{'cost_usd': 0.0009, ...}
"""

from .similarity import semantic_similarity, batch_similarity, relevance_score
from .faithfulness import faithfulness_score, check_groundedness
from .toxicity import toxicity_check, contains_pii
from .cost import estimate_cost, CostTracker

__all__ = [
    "CostTracker",
    "batch_similarity",
    "check_groundedness",
    "contains_pii",
    "estimate_cost",
    "faithfulness_score",
    "relevance_score",
    "semantic_similarity",
    "toxicity_check",
]
