# PyTekt transformer — examples

Runnable examples for the `pytekt.former` module.

## Single entry point

From the project root:

```bash
python -m pytekt.former.example
```

Runs a single script that demonstrates: tokenizer/dataset, forward pass, short training, attention visualization, text generation, and training metrics plot. Outputs are written next to `example.py` (e.g. `example_attention.png`, `example_training_metrics.png`).

## Scripts in this folder

| Script | Description |
|--------|--------------|
| **attention_demo** | Build a small model, run one forward pass, save attention heatmaps (one head and all heads) as PNG. No training. |
| **text_generation** | Build dataset and model (same as training script), then generate text from a prompt using temperature-based sampling. |

Run with:

```bash
python -m pytekt.former.examples.attention_demo
python -m pytekt.former.examples.text_generation
```

## Full training

Training with config and plots is in the experiments package:

```bash
python -m pytekt.former.experiments.train_small_model
```

See `pytekt/former/README.md` for full documentation.
