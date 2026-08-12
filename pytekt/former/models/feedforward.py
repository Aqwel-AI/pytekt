"""
Position-wise feed-forward network.

Two linear layers with ReLU in between: x -> W1*x+b1 -> ReLU -> W2*x+b2.
Standard in transformer blocks.
"""

import numpy as np
from typing import Optional
from ..core.tensor import Tensor
from ..core.operations import matmul, relu


# -----------------------------------------------------------------------------
# Feed-forward layer
# -----------------------------------------------------------------------------

class FeedForward:
    """
    Position-wise feed-forward: two linear layers with ReLU in between.

    Parameters
    ----------
    embed_dim : int
        Input and output dimension.
    hidden_dim : int, optional
        Hidden dimension; default 4 * embed_dim.
    """

    def __init__(self, embed_dim: int, hidden_dim: Optional[int] = None):
        hidden_dim = hidden_dim or 4 * embed_dim
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        scale = 0.02
        self.W1 = Tensor(
            np.random.randn(embed_dim, hidden_dim).astype(np.float64) * scale,
            requires_grad=True,
        )
        self.b1 = Tensor(np.zeros(hidden_dim), requires_grad=True)
        self.W2 = Tensor(
            np.random.randn(hidden_dim, embed_dim).astype(np.float64) * scale,
            requires_grad=True,
        )
        self.b2 = Tensor(np.zeros(embed_dim), requires_grad=True)

    def forward(self, x: Tensor) -> Tensor:
        """
        Forward: x @ W1 + b1 -> ReLU -> @ W2 + b2.

        Parameters
        ----------
        x : Tensor
            Input, shape (batch, seq, embed_dim).

        Returns
        -------
        Tensor
            Output, shape (batch, seq, embed_dim).
        """
        h = matmul(x, self.W1) + self.b1
        h = relu(h)
        return matmul(h, self.W2) + self.b2

    def parameters(self):
        """Return W1, b1, W2, b2."""
        return [self.W1, self.b1, self.W2, self.b2]
