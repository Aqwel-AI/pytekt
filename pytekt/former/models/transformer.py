"""
Transformer decoder-only stack (GPT-style).

Implements TransformerBlock (pre-norm attention + pre-norm FFN) and
Transformer (embedding → positional encoding → N blocks → final ln → LM head).
"""

import numpy as np
from typing import Optional, List, Tuple
from ..core.tensor import Tensor
from ..core.operations import layer_norm, matmul
from .embedding import Embedding, PositionalEncoding
from .attention import MultiHeadAttention
from .feedforward import FeedForward


# -----------------------------------------------------------------------------
# Single block and full model
# -----------------------------------------------------------------------------

class TransformerBlock:
    """
    Single transformer block: pre-norm attention + residual, pre-norm FFN + residual.

    Parameters
    ----------
    embed_dim : int
        Embedding dimension (model width).
    num_heads : int
        Number of attention heads; embed_dim must be divisible by num_heads.
    hidden_dim : int, optional
        Hidden dimension of the feed-forward layer; default 4 * embed_dim.
    """

    def __init__(self, embed_dim: int, num_heads: int, hidden_dim: Optional[int] = None):
        self.embed_dim = embed_dim
        self.attn = MultiHeadAttention(embed_dim, num_heads)
        self.ff = FeedForward(embed_dim, hidden_dim)
        # Layer norm parameters (learnable scale and shift)
        scale = 0.02
        self.ln1_gamma = Tensor(np.ones(embed_dim), requires_grad=True)
        self.ln1_beta = Tensor(np.zeros(embed_dim), requires_grad=True)
        self.ln2_gamma = Tensor(np.ones(embed_dim), requires_grad=True)
        self.ln2_beta = Tensor(np.zeros(embed_dim), requires_grad=True)

    def forward(
        self,
        x: Tensor,
        mask: Optional[np.ndarray] = None,
    ) -> Tuple[Tensor, np.ndarray]:
        """
        Forward pass: pre-norm attention + residual, then pre-norm FFN + residual.

        Parameters
        ----------
        x : Tensor
            Input, shape (batch, seq, embed_dim).
        mask : np.ndarray, optional
            Additive attention mask (e.g. causal).

        Returns
        -------
        x : Tensor
            Output, same shape as input.
        attn_weights : np.ndarray
            Attention weights for this block; shape (batch, num_heads, seq, seq).
        """
        normed = layer_norm(x, self.ln1_gamma, self.ln1_beta)
        attn_out, attn_weights = self.attn.forward(normed, mask)
        x = x + attn_out
        normed2 = layer_norm(x, self.ln2_gamma, self.ln2_beta)
        x = x + self.ff.forward(normed2)
        return x, attn_weights

    def parameters(self) -> List[Tensor]:
        """Return all trainable parameters in this block."""
        return (
            self.attn.parameters()
            + self.ff.parameters()
            + [self.ln1_gamma, self.ln1_beta, self.ln2_gamma, self.ln2_beta]
        )


class Transformer:
    """
    Decoder-only transformer for next-token prediction (LM head on last dimension).

    Parameters
    ----------
    vocab_size : int
        Size of the token vocabulary.
    embed_dim : int, optional
        Embedding dimension (default 128).
    num_heads : int, optional
        Number of attention heads (default 4).
    num_layers : int, optional
        Number of transformer blocks (default 2).
    max_seq_len : int, optional
        Maximum sequence length (default 64).
    hidden_dim : int, optional
        Feed-forward hidden dimension; default 4 * embed_dim.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        num_heads: int = 4,
        num_layers: int = 2,
        max_seq_len: int = 64,
        hidden_dim: Optional[int] = None,
    ):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len
        self.embedding = Embedding(vocab_size, embed_dim)
        self.pos_encoding = PositionalEncoding(embed_dim, max_seq_len)
        self.blocks = [
            TransformerBlock(embed_dim, num_heads, hidden_dim)
            for _ in range(num_layers)
        ]
        self.ln_f_gamma = Tensor(np.ones(embed_dim), requires_grad=True)
        self.ln_f_beta = Tensor(np.zeros(embed_dim), requires_grad=True)
        # LM head: project hidden state to vocabulary logits
        scale = 0.02
        self.lm_head = Tensor(
            np.random.randn(embed_dim, vocab_size).astype(np.float64) * scale,
            requires_grad=True,
        )

    def forward(
        self,
        token_ids: np.ndarray,
        mask: Optional[np.ndarray] = None,
    ) -> Tuple[Tensor, List[np.ndarray]]:
        """
        Forward pass: embed → add position → N blocks → final ln → logits.

        Parameters
        ----------
        token_ids : np.ndarray
            Integer token ids; shape (batch, seq).
        mask : np.ndarray, optional
            Additive attention mask.

        Returns
        -------
        logits : Tensor
            Shape (batch, seq, vocab_size); unnormalized log-probabilities.
        attention_weights_list : list of np.ndarray
            One array per block; each shape (batch, num_heads, seq, seq).
        """
        x = self.embedding(token_ids)
        x = self.pos_encoding.forward(x)
        attention_weights_list = []
        for block in self.blocks:
            x, attn_weights = block.forward(x, mask)
            attention_weights_list.append(attn_weights)
        x = layer_norm(x, self.ln_f_gamma, self.ln_f_beta)
        logits = matmul(x, self.lm_head)
        return logits, attention_weights_list

    def parameters(self) -> List[Tensor]:
        """Return all trainable parameters of the model."""
        params = (
            [self.embedding.weight]
            + [self.ln_f_gamma, self.ln_f_beta, self.lm_head]
        )
        for block in self.blocks:
            params.extend(block.parameters())
        return params
