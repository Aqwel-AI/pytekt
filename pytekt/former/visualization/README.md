# pytekt.former.visualization — Package documentation

## 1. Title and overview

**`pytekt.former.visualization`** provides **matplotlib** plots for transformer **debugging and reporting**: attention **heatmaps** (single or all heads), **training loss / metrics** over time, and **weight spectrum** (eigenvalues or singular values of weight matrices).

Intended for notebooks and experiment scripts; requires a display or non-interactive backend (e.g. `Agg`) in CI.

---

## 2. Module layout

| File | Role |
|------|------|
| `attention_map.py` | `plot_attention_map`, `plot_multi_head_attention` — heatmaps from attention weights. |
| `training_metrics.py` | `plot_training_metrics` — loss (and related series) from `Trainer.history`. |
| `weight_spectrum.py` | `plot_weight_spectrum` — spectrum of a 2D weight matrix. |

---

## 3. Public API (from `pytekt.former.visualization`)

| Symbol | Description |
|--------|-------------|
| `plot_attention_map` | Single attention matrix heatmap. |
| `plot_multi_head_attention` | Grid of heads (layer visualization). |
| `plot_training_metrics` | Line plot from training history dict/list. |
| `plot_weight_spectrum` | Distribution of singular values or eigenvalues. |

```python
from pytekt.former.visualization import plot_training_metrics, plot_attention_map

plot_training_metrics(trainer.history)
```

---

## 4. Conventions

- Functions typically return a **matplotlib `Figure`**; call `plt.savefig` or use `Figure.savefig` for files.
- Match tensor shapes expected by each function (see docstrings in source).

---

## 5. Dependencies

- **Matplotlib** ≥ 3.5 (included in `pip install pytekt[former]`).

---

## Examples

[`examples/README.md`](examples/README.md) — `python -m pytekt.former.visualization.examples.demo_attention_plot` (writes `attention_demo.png`).

---

## 6. See also

- Parent: [`../README.md`](../README.md)
- Example scripts: [`../examples/README.md`](../examples/README.md) (`attention_demo`, etc.)
- Package examples folder: [`../examples/`](../examples/) for PNG outputs and demos
