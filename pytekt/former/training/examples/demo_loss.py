"""Cross-entropy loss backward on random logits."""
from __future__ import annotations

import numpy as np

from pytekt.former.core import Tensor
from pytekt.former.training import cross_entropy_loss


def main() -> None:
    batch, seq, vocab = 2, 4, 12
    logits = Tensor(
        np.random.randn(batch, seq, vocab).astype(np.float64) * 0.1,
        requires_grad=True,
    )
    targets = np.random.randint(0, vocab, size=(batch, seq), dtype=np.int64)
    loss = cross_entropy_loss(logits, targets)
    loss.backward()
    assert logits.grad is not None
    print("demo_loss ok — mean loss =", float(np.asarray(loss._data)))


if __name__ == "__main__":
    main()
