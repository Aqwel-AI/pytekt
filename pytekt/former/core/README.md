# pytekt.former.core — Package documentation

## 1. Title and overview

**`pytekt.former.core`** is the NumPy-backed **tensor** and **autograd** layer for the decoder-only transformer in `pytekt.former`. It defines `Tensor` (forward values + optional gradient tracking) and differentiable **ops** used by `pytekt.former.models` (matmul, softmax, layer norm, ReLU, transpose).

**Scope:** educational / small-scale experiments—not a general deep-learning framework.

---

## 2. Module layout

| File | Role |
|------|------|
| `tensor.py` | `Tensor` class; operator overloads (`+`, `*`, `@`, etc.); `backward()` from a scalar loss. |
| `operations.py` | `matmul`, `softmax`, `layer_norm`, `relu`, `transpose`; also `scaled_dot_product_attention` (import from submodule if needed). |
| `autograd.py` | Thin re-export of `Tensor` for backward-related imports. |

---

## 3. Public API (from `pytekt.former.core`)

| Symbol | Description |
|--------|-------------|
| `Tensor` | Wraps `np.ndarray`; `requires_grad`, `grad`, `backward()`. |
| `matmul` | Matrix multiply; records graph when inputs require grad. |
| `softmax` | Softmax along an axis (default last). |
| `layer_norm` | Layer normalization with learnable `gamma`, `beta`. |
| `relu` | ReLU activation. |
| `transpose` | Permute dimensions. |

**Additional:** `scaled_dot_product_attention` lives in `operations.py` and is used by the model stack; import it explicitly if you extend attention outside `MultiHeadAttention`.

```python
from pytekt.former.core import Tensor, matmul, softmax, layer_norm
```

---

## 4. Conventions

- **dtype:** Values are coerced to **float64** for consistency.
- **Graph:** Non-leaf tensors carry `_grad_fn` and `_prev`; call `loss.backward()` on a scalar `Tensor`.
- **In-place:** Prefer functional ops; avoid mutating `Tensor._data` unless you know the graph implications.

---

## 5. Dependencies

- **NumPy** ≥ 1.20 (required by the parent `[former]` extra).

---

## Examples

Runnable demo: [`examples/README.md`](examples/README.md) (`python -m pytekt.former.core.examples.demo_tensor`).

---

## 6. See also

- Parent: [`../README.md`](../README.md)
- Architecture: [`../docs/architecture.md`](../docs/architecture.md)
- Models (built on core): [`../models/README.md`](../models/README.md)
