"""Minimal autograd demo: matmul + sum + backward."""
from __future__ import annotations

import numpy as np

from pytekt.former.core import Tensor, matmul


def main() -> None:
    a = Tensor(np.array([[2.0, 3.0]]), requires_grad=True)
    b = Tensor(np.array([[1.0], [1.0]]), requires_grad=True)
    y = matmul(a, b)
    loss = y.sum()
    loss.backward()
    assert a.grad is not None and b.grad is not None
    print("demo_tensor ok — loss =", float(np.asarray(loss._data)))


if __name__ == "__main__":
    main()
