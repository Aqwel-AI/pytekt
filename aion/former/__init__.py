"""
Aion — Transformer module
=========================

Lightweight decoder-only (GPT-style) transformer training for research and
experimentation. Provides NumPy-backed autograd, multi-head attention,
training pipeline, and visualization. Use for education and small-scale
experiments.

Example
-------
    from aion.former import Transformer, Trainer
    from aion.former.datasets import create_dataloader
    from aion.former.visualization import plot_attention_map, plot_training_metrics

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

__version__ = "0.2.0"

from .models import Transformer, MultiHeadAttention, FeedForward, Embedding, PositionalEncoding
from .training import Trainer, Adam, cross_entropy_loss
from .datasets import TextDataset, create_dataloader, SimpleTokenizer
from .visualization import (
    plot_attention_map,
    plot_multi_head_attention,
    plot_training_metrics,
    plot_weight_spectrum,
)

__all__ = [
    "__version__",
    "Transformer",
    "MultiHeadAttention",
    "FeedForward",
    "Embedding",
    "PositionalEncoding",
    "Trainer",
    "Adam",
    "cross_entropy_loss",
    "TextDataset",
    "create_dataloader",
    "SimpleTokenizer",
    "plot_attention_map",
    "plot_multi_head_attention",
    "plot_training_metrics",
    "plot_weight_spectrum",
]
