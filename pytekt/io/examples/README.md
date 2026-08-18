# pytekt.io — Examples

Small scripts showing **streaming reads**, **atomic writes**, and **SHA-256** checks. No extra dependencies beyond **`pytekt`**.

## Run

From the repo root (editable install):

```bash
pip install -e .
python -m pytekt.io.examples.demo_atomic_checksum
```

| Script | What it does |
|--------|----------------|
| **demo_atomic_checksum.py** | `atomic_write` a UTF-8 file, `iter_lines`, `file_sha256` + `verify_sha256`. |

Package reference: [`../README.md`](../README.md).
