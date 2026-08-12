# pytekt.former.experiments — Examples

The main end-to-end training entry point lives **one level up**:

```bash
pip install -e ".[former]"
python -m pytekt.former.experiments.train_small_model
```

That script reads **`../config.yaml`** (or built-in defaults) and saves metrics / weights.

## Optional helper

| Script | Content |
|--------|---------|
| **demo_config.py** | Load `config.yaml` from the parent `experiments/` folder and print top-level keys (no training). |

```bash
python -m pytekt.former.experiments.examples.demo_config
```

Parent docs: [`../README.md`](../README.md)
