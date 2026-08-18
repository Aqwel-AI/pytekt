# pytekt.former.experiments — Package documentation

## 1. Title and overview

**`pytekt.former.experiments`** holds **runnable training scripts** and **YAML configuration** for end-to-end demos: build a small `Transformer`, train on text with `Trainer`, save weights, and emit **matplotlib** plots (training loss, optional weight spectrum).

This is not imported as a heavy API surface; the main entry point is a **module script**.

---

## 2. Contents

| Path | Role |
|------|------|
| `train_small_model.py` | Loads `config.yaml` (or defaults), builds `TextDataset` + `Transformer` + `Trainer`, runs epochs, saves `.npz` weights and PNGs. |
| `config.yaml` | Model dims, training hyperparameters, data `seq_length` / `level` / optional `data_file`. |

---

## 3. How to run

From the repo (with `[former]` installed):

```bash
python -m pytekt.former.experiments.train_small_model
```

Override data by setting `data.data_file` in `config.yaml` to a text path, or edit defaults inside `train_small_model.py`.

**Outputs** (typical): training loss figure, optional weight spectrum, checkpoint weights via `save_transformer_weights`.

---

## 4. Dependencies

- **NumPy**, **Matplotlib**, **PyYAML** (all pulled in by `pip install pytekt[former]`).

---

## 5. Conventions

- Config is **optional**; if `config.yaml` is missing, built-in defaults match the small demo in `train_small_model.py`.
- For reproducible paper-style runs, copy `config.yaml` and version-control it with your experiment notes.

---

## Examples

[`examples/README.md`](examples/README.md) — points to `train_small_model` and `python -m pytekt.former.experiments.examples.demo_config`.

---

## 6. See also

- Parent: [`../README.md`](../README.md)
- Training API: [`../training/README.md`](../training/README.md)
- Interactive demos: [`../examples/README.md`](../examples/README.md)
