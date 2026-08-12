"""
Training loop: forward, loss, backward, optimizer step.

Trainer holds the model and Adam optimizer; train_step runs one batch,
train_epoch runs multiple steps and records mean loss in history.
evaluate computes mean loss without updating parameters.
"""

import numpy as np
from typing import Optional, Callable, List, Dict, Any
from ..core.tensor import Tensor
from .loss import cross_entropy_loss
from .optimizer import Adam


def _make_causal_attention_mask(
    seq_len: int,
    num_heads: int,
    batch_size: int,
    mask_value: float = -1e9,
) -> np.ndarray:
    """
    Create an additive causal mask for attention scores.

    Disallows attention to future positions (upper triangular part).
    Returned shape: (batch, num_heads, seq, seq).
    """
    base = np.zeros((seq_len, seq_len), dtype=np.float64)
    base[np.triu_indices(seq_len, k=1)] = mask_value
    return np.broadcast_to(base[None, None, :, :], (batch_size, num_heads, seq_len, seq_len)).copy()


# -----------------------------------------------------------------------------
# Trainer
# -----------------------------------------------------------------------------

class Trainer:
    """
    Train a transformer for next-token prediction.

    Parameters
    ----------
    model : object with .forward() and .parameters()
        The transformer model (e.g. aion.former.Transformer).
    lr : float, optional
        Learning rate for Adam (default 1e-3).
    beta1, beta2 : float, optional
        Adam momentum parameters (default 0.9, 0.999).

    Attributes
    ----------
    history : list of dict
        One dict per epoch, e.g. [{"loss": 0.5}, ...].
    """

    def __init__(
        self,
        model: Any,
        lr: float = 1e-3,
        beta1: float = 0.9,
        beta2: float = 0.999,
    ):
        self.model = model
        self.optimizer = Adam(model.parameters(), lr=lr, beta1=beta1, beta2=beta2)
        self.history: List[Dict[str, float]] = []

    def train_step(
        self,
        token_ids: np.ndarray,
        targets: np.ndarray,
        mask: Optional[np.ndarray] = None,
    ) -> float:
        """
        One training step: zero_grad, forward, loss, backward, step.

        Parameters
        ----------
        token_ids : np.ndarray
            Input token ids, shape (batch, seq).
        targets : np.ndarray
            Target (next) token ids, shape (batch, seq); use -1 for padding.
        mask : np.ndarray, optional
            Attention mask if needed.

        Returns
        -------
        float
            Scalar loss for this batch.
        """
        self.optimizer.zero_grad()
        if mask is None:
            # Next-token prediction needs causal attention: position i can only
            # attend to <= i within the sequence.
            seq_len = int(token_ids.shape[1])
            num_heads = int(getattr(self.model, "num_heads", 1))
            batch_size = int(token_ids.shape[0])
            mask = _make_causal_attention_mask(seq_len, num_heads, batch_size)
        logits, _ = self.model.forward(token_ids, mask)
        loss = cross_entropy_loss(logits, targets)
        loss.backward()
        self.optimizer.step()
        return float(loss._data)

    def train_epoch(
        self,
        get_batch: Callable[[], tuple],
        steps_per_epoch: int,
    ) -> float:
        """
        Run one epoch: steps_per_epoch batches, then append mean loss to history.

        Parameters
        ----------
        get_batch : callable
            No arguments; returns (token_ids, targets).
        steps_per_epoch : int
            Number of batches per epoch.

        Returns
        -------
        float
            Mean loss over the epoch.
        """
        total_loss = 0.0
        for _ in range(steps_per_epoch):
            token_ids, targets = get_batch()
            loss = self.train_step(token_ids, targets)
            total_loss += loss
        mean_loss = total_loss / steps_per_epoch
        self.history.append({"loss": mean_loss})
        return mean_loss

    def evaluate(
        self,
        get_batch: Callable[[], tuple],
        num_batches: int = 10,
    ) -> float:
        """
        Compute mean loss over batches without updating parameters.

        Parameters
        ----------
        get_batch : callable
            No arguments; returns (token_ids, targets).
        num_batches : int, optional
            Number of batches to average (default 10).

        Returns
        -------
        float
            Mean loss.
        """
        total_loss = 0.0
        for _ in range(num_batches):
            token_ids, targets = get_batch()
            self.optimizer.zero_grad()
            seq_len = int(token_ids.shape[1])
            num_heads = int(getattr(self.model, "num_heads", 1))
            batch_size = int(token_ids.shape[0])
            mask = _make_causal_attention_mask(seq_len, num_heads, batch_size)
            logits, _ = self.model.forward(token_ids, mask)
            loss = cross_entropy_loss(logits, targets)
            total_loss += float(loss._data)
        return total_loss / num_batches
