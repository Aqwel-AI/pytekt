"""
Transformer model components.

Decoder-only stack: Transformer, TransformerBlock, MultiHeadAttention,
FeedForward, Embedding, PositionalEncoding. Full documentation:
aion/former/README.md and aion/former/docs/architecture.md.
"""

from .transformer import Transformer
from .attention import MultiHeadAttention
from .feedforward import FeedForward
from .embedding import Embedding, PositionalEncoding

__all__ = [
    "Transformer",
    "MultiHeadAttention",
    "FeedForward",
    "Embedding",
    "PositionalEncoding",
]
