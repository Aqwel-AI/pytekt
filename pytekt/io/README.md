# pytekt.io — Package documentation

## 1. Title and overview

**`pytekt.io`** provides **low-level, safe file I/O** primitives: **streaming** line and chunk reads, **atomic** text/byte writes (crash-safe replace), and **SHA-256** hashing for integrity checks. Use **`pytekt.files`** when you want higher-level CRUD helpers and user-facing messages.

---

## 2. Module layout

| File | Role |
|------|------|
| `streaming.py` | `iter_lines`, `read_chunks` — memory-efficient reads for large files. |
| `atomic.py` | `atomic_write`, `atomic_write_bytes`, `save_automatically` — write-to-temp then replace. |
| `checksum.py` | `file_sha256`, `verify_sha256` — reproducible digests. |

---

## 3. Public API (from `pytekt.io`)

| Symbol | Description |
|--------|-------------|
| `iter_lines` | Stream text lines from a path (`pathlib` / `PathLike`). |
| `read_chunks` | Stream fixed-size binary chunks. |
| `atomic_write` | Write string data via temp file + rename. |
| `atomic_write_bytes` | Same for raw bytes. |
| `save_automatically` | Convenience wrapper for periodic saves. |
| `file_sha256` | Compute hex digest of a file. |
| `verify_sha256` | Check file against an expected digest. |

```python
from pathlib import Path
from pytekt.io import iter_lines, atomic_write, file_sha256

for line in iter_lines(Path("log.txt")):
    process(line)
```

---

## 4. Examples

Runnable scripts: **[examples/](examples/)** — see [examples/README.md](examples/README.md).

```bash
python -m pytekt.io.examples.demo_atomic_checksum
```

---

## 5. Conventions

- **Encoding:** Text helpers default to UTF-8 unless overridden.
- **Atomic writes:** Rely on same-filesystem rename semantics; avoid cross-device paths for the temp file.

---

## 6. Dependencies

**Standard library only** (plus **`pathlib`** / **`hashlib`** / **`os`** as used internally).

---

## 7. See also

- Higher-level files API: **`pytekt.files`**
- Tabular / JSONL loads: **`csv`**, **`json`**, or **pandas** in your application code
- Root README: [../../README.md](../../README.md)
