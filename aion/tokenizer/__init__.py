"""
Tokenization: BPE, WordPiece, and vocabulary management.

Trainable tokenizers that work standalone or integrate with
:mod:`aion.former` for transformer training.

Examples
--------
>>> from aion.tokenizer import BPETokenizer
>>> tok = BPETokenizer()
>>> tok.train(["hello world", "hello there"])
>>> tok.encode("hello world")
[...]
>>> tok.decode(tok.encode("hello world"))
'hello world'
"""

from .bpe import BPETokenizer
from .wordpiece import WordPieceTokenizer
from .vocab import Vocabulary

__all__ = [
    "BPETokenizer",
    "Vocabulary",
    "WordPieceTokenizer",
]
