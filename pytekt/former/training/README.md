# pytekt.former.training — Package documentation

## 1. Title and overview

**`pytekt.former.training`** wires the **Transformer** into a small training loop: **cross-entropy loss** for next-token prediction, **Adam** optimizer, and **`Trainer`** with `train_step` / `train_epoch`. It also exposes **checkpoint I/O** (NumPy `.npz` weights + optional JSON sidecar metadata).

---

## 2. Module layout

| File | Role |
|------|------|
| `loss.py` | `cross_entropy_loss` — logits vs integer targets; optional padding mask. |
| `optimizer.py` | `Adam` — step updates `Tensor` parameters with `.grad`. |
| `trainer.py` | `Trainer` — forward, loss, `backward`, optimizer step; records `history`. |
| `checkpoint.py` | `save_transformer_weights`, `load_transformer_weights`, `save_checkpoint_sidecar_meta`. |

---

## 3. Public API (from `pytekt.former.training`)

| Symbol | Description |
|--------|-------------|
| `Trainer` | `(model, lr=...)`; `train_step(get_batch)`, `train_epoch(get_batch, steps)`. |
| `Adam` | Optimizer over model parameters (internal use by `Trainer`). |
| `cross_entropy_loss` | Next-token CE from logits `(B, T, V)` and targets `(B, T)`. |
| `save_transformer_weights` / `load_transformer_weights` | Persist / restore NumPy arrays for `Transformer` parameters. |
| `save_checkpoint_sidecar_meta` | Write JSON metadata next to a checkpoint (experiment tracking). |

```python
from pytekt.former.training import Trainer, cross_entropy_loss

trainer = Trainer(model, lr=1e-3)
loss = trainer.train_epoch(get_batch, steps_per_epoch=50)
```

---

## 4. Conventions

- **`get_batch`:** Callable with no arguments, returning `(input_ids, target_ids)` as arrays or tensors compatible with the model forward (see `Trainer` implementation).
- **History:** `trainer.history` typically stores per-step or per-epoch loss for plotting (`plot_training_metrics`).

---

## 5. Dependencies

- **NumPy**; **PyYAML** only if you load experiment YAML elsewhere (checkpoints are NumPy + optional JSON).

---

## Examples

[`examples/README.md`](examples/README.md) — `python -m pytekt.former.training.examples.demo_loss`.

---

## 6. See also

- Parent: [`../README.md`](../README.md)
- Models: [`../models/README.md`](../models/README.md)
- Visualization: [`../visualization/README.md`](../visualization/README.md)
- Experiments script: [`../experiments/README.md`](../experiments/README.md)
