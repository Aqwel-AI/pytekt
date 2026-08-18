"""Single Transformer forward pass."""
from __future__ import annotations

import numpy as np

from pytekt.former.models import Transformer


def main() -> None:
    vocab_size = 32
    seq = 8
    batch = 2
    model = Transformer(
        vocab_size=vocab_size,
        embed_dim=32,
        num_heads=4,
        num_layers=1,
        max_seq_len=seq,
        hidden_dim=64,
    )
    token_ids = np.random.randint(0, vocab_size, size=(batch, seq), dtype=np.int64)
    logits, attn_list = model.forward(token_ids)
    assert logits.shape == (batch, seq, vocab_size)
    assert len(attn_list) == 1
    print("demo_forward ok — logits", tuple(logits.shape))


if __name__ == "__main__":
    main()
