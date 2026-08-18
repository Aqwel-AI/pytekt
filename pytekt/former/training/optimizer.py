"""
Adam optimizer for Tensor parameters.

First-order optimizer with bias-corrected moment estimates. step() updates
parameters in place; zero_grad() clears gradients before backward.
"""

import numpy as np
from typing import List
from ..core.tensor import Tensor


# -----------------------------------------------------------------------------
# Adam
# -----------------------------------------------------------------------------

class Adam:
    """
    Adam optimizer for a list of Tensor parameters.

    Parameters
    ----------
    params : list of Tensor
        Parameters to optimize; only those with requires_grad=True are updated.
    lr : float, optional
        Learning rate (default 1e-3).
    beta1, beta2 : float, optional
        Decay rates for first and second moment (default 0.9, 0.999).
    eps : float, optional
        Small constant for numerical stability (default 1e-8).
    """

    def __init__(
        self,
        params: List[Tensor],
        lr: float = 1e-3,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
    ):
        self.params = [p for p in params if p.requires_grad]
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.t = 0
        # First and second moment buffers (same shape as each parameter)
        self.m = [np.zeros_like(p._data, dtype=np.float64) for p in self.params]
        self.v = [np.zeros_like(p._data, dtype=np.float64) for p in self.params]

    def step(self) -> None:
        """Perform one optimizer step: update parameters using current gradients."""
        self.t += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = np.asarray(p.grad, dtype=np.float64).copy()
            data = np.asarray(p._data, dtype=np.float64).copy()
            self.m[i] = (self.beta1 * self.m[i] + (1 - self.beta1) * g).astype(np.float64)
            self.v[i] = (self.beta2 * self.v[i] + (1 - self.beta2) * (g * g)).astype(np.float64)
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            p._data = data - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)

    def zero_grad(self) -> None:
        """Clear gradients on all parameters."""
        for p in self.params:
            p.grad = None
