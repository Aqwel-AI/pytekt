"""
Text dataset and data loader for next-token prediction.

Sliding-window over tokenized text: each sample is a contiguous segment
with targets equal to the next token. get_batch returns random batches.
"""

import numpy as np
from typing import Iterator, Tuple, Optional, Callable
from .tokenizer import SimpleTokenizer


# -----------------------------------------------------------------------------
# Dataset and loader
# -----------------------------------------------------------------------------

class TextDataset:
    """
    Sliding-window next-token prediction dataset from raw text.

    Parameters
    ----------
    text : str
        Raw text corpus.
    seq_length : int
        Context length (number of input tokens per sample).
    tokenizer : SimpleTokenizer, optional
        Tokenizer to use; if None, a new one is created with the given level.
    level : str, optional
        "char" or "word"; used only when tokenizer is None (default "char").
    """

    def __init__(
        self,
        text: str,
        seq_length: int,
        tokenizer: Optional[SimpleTokenizer] = None,
        level: str = "char",
    ):
        self.seq_length = seq_length
        self.tokenizer = tokenizer or SimpleTokenizer(level=level)
        self.tokenizer.fit(text)
        self.ids = np.array(self.tokenizer.encode(text), dtype=np.int64)
        self.vocab_size = self.tokenizer.vocab_size

    def __len__(self) -> int:
        """Number of valid sliding windows (excluding last token)."""
        return max(0, len(self.ids) - self.seq_length)

    def get_batch(
        self,
        batch_size: int,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Draw a random batch of (inputs, targets).

        Parameters
        ----------
        batch_size : int
            Number of samples in the batch.

        Returns
        -------
        inputs : np.ndarray
            Shape (batch_size, seq_length); integer token ids.
        targets : np.ndarray
            Shape (batch_size, seq_length); next token for each position.

        Raises
        ------
        ValueError
            If the dataset is too small for seq_length.
        """
        n = len(self.ids) - self.seq_length - 1
        if n <= 0:
            raise ValueError("Dataset too small for seq_length")
        indices = np.random.randint(0, n, size=batch_size)
        inputs = np.zeros((batch_size, self.seq_length), dtype=np.int64)
        targets = np.zeros((batch_size, self.seq_length), dtype=np.int64)
        for i, start in enumerate(indices):
            inputs[i] = self.ids[start : start + self.seq_length]
            targets[i] = self.ids[start + 1 : start + self.seq_length + 1]
        return inputs, targets


def create_dataloader(
    text: str,
    seq_length: int,
    batch_size: int,
    level: str = "char",
    tokenizer: Optional[SimpleTokenizer] = None,
) -> Tuple[TextDataset, Callable[[], Tuple[np.ndarray, np.ndarray]]]:
    """
    Build a TextDataset and a get_batch callable.

    Parameters
    ----------
    text : str
        Raw text corpus.
    seq_length : int
        Context length.
    batch_size : int
        Batch size for get_batch().
    level : str, optional
        "char" or "word" (default "char").
    tokenizer : SimpleTokenizer, optional
        Tokenizer; if None, one is created from text.

    Returns
    -------
    dataset : TextDataset
        The constructed dataset (for vocab_size, tokenizer, etc.).
    get_batch : callable
        No arguments; returns (inputs, targets) each call.
    """
    dataset = TextDataset(text, seq_length, tokenizer=tokenizer, level=level)

    def get_batch() -> Tuple[np.ndarray, np.ndarray]:
        return dataset.get_batch(batch_size)

    return dataset, get_batch
