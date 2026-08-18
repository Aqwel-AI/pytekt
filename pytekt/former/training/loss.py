"""
Loss functions for next-token prediction.

Cross-entropy loss over vocabulary with optional padding mask (targets == -1).
Numerically stable and supports backward through logits.
"""

import numpy as np
from ..core.tensor import Tensor


# -----------------------------------------------------------------------------
# Cross-entropy
# -----------------------------------------------------------------------------

def cross_entropy_loss(logits: Tensor, targets: np.ndarray) -> Tensor:
    """
    Cross-entropy loss for next-token prediction.

    Uses mean over valid positions (targets >= 0). Positions with target == -1
    are treated as padding and excluded from the loss.

    Parameters
    ----------
    logits : Tensor
        Unnormalized logits, shape (batch, seq, vocab_size).
    targets : np.ndarray
        Integer target token ids, shape (batch, seq); use -1 for padding.

    Returns
    -------
    Tensor
        Scalar loss; supports backward if logits.requires_grad.

    Notes
    -----
    Implementation is numerically stable (log-sum-exp) and builds a gradient
    for the backward pass through the logits.
    """
    batch, seq, vocab = logits.shape
    logits_flat = logits._data.reshape(-1, vocab)
    targets_flat = targets.reshape(-1)
    valid = targets_flat >= 0
    if not np.any(valid):
        return Tensor(np.array(0.0))
    logits_valid = logits_flat[valid]
    targets_valid = targets_flat[valid]
    # Log-sum-exp for numerical stability
    x_max = np.max(logits_valid, axis=1, keepdims=True)
    log_sum_exp = np.log(np.sum(np.exp(logits_valid - x_max), axis=1)) + x_max.squeeze(1)
    nll = log_sum_exp - logits_valid[np.arange(len(targets_valid)), targets_valid]
    loss_val = np.mean(nll)
    # Gradient of CE w.r.t. logits (softmax - one-hot) for backward
    grad_flat = np.zeros_like(logits_flat)
    exp_logits = np.exp(logits_valid - x_max)
    probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
    probs[np.arange(len(targets_valid)), targets_valid] -= 1
    grad_flat[valid] = probs / np.sum(valid)
    grad = grad_flat.reshape(batch, seq, vocab)

    def _ce_backward(g, o, lg):
        return (g * grad,)

    loss = Tensor(
        np.array(loss_val),
        requires_grad=logits.requires_grad,
        _grad_fn=_ce_backward if logits.requires_grad else None,
        _prev=(logits,) if logits.requires_grad else (),
    )
    return loss
