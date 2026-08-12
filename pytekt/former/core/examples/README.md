# pytekt.former.core — Examples

Small **stdlib + NumPy** scripts showing **`Tensor`** and **`matmul`** with a backward pass.

## Run

From the repository root with an editable install:

```bash
pip install -e ".[former]"
python -m pytekt.former.core.examples.demo_tensor
```

| Script | Content |
|--------|---------|
| **demo_tensor.py** | Build two trainable tensors, `matmul`, scalar `sum` loss, `backward()`, check `.grad`. |

Parent docs: [`../README.md`](../README.md)
