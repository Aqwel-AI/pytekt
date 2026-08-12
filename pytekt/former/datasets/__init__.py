"""
Dataset loading and tokenization.

TextDataset builds a sliding-window next-token dataset from raw text.
create_dataloader returns (dataset, get_batch). SimpleTokenizer provides
character- or word-level encode/decode.
"""

from .loader import TextDataset, create_dataloader
from .tokenizer import SimpleTokenizer

__all__ = ["TextDataset", "create_dataloader", "SimpleTokenizer"]
