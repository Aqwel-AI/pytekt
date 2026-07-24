# aion.db — Unified database layer

Python-first database access for **SQLite** (zero extra deps), **MySQL**, **PostgreSQL**, **MongoDB**, and **Redis** (optional: `pip install aqwel-aion[db]`).

## Quick start

```python
import aion.db as db

conn = db.connect("sqlite://./app.db")
conn.users.insert({"name": "Alice", "score": 10})
print(conn.users.find(name="Alice"))

rows = (
    conn.table("users")
    .where(conn.col.score > 5)
    .select("name", "score")
    .all()
)
```

## Engines

| Engine | Install | URL example |
|--------|---------|-------------|
| sqlite | core | `sqlite://./app.db` |
| mysql | `[db]` | `mysql://user:pass@localhost:3306/mydb` |
| postgresql | `[db]` | `postgresql://user:pass@localhost:5432/mydb` |
| mongodb | `[db]` | `mongodb://localhost:27017/mydb` |
| redis | `[db]` | `redis://localhost:6379/0` |

## Dict API

```python
conn.users.insert({"name": "Alice", "tags": ["ai"]})
conn.users.find(name="Alice")
conn.users.find(score__gte=5)
conn.users.find_one(id=1)
conn.users.update({"name": "Alice"}, {"score": 99})
conn.users.delete(name="Bob")
```

## Aion-only features

- `conn.docs.hybrid_search(text="...", vector=[...], top_k=10)`
- `db.agent_memory(conn, thread_id="t1")`
- `db.bulk_upsert(conn, "items", rows, key_field="id")`
- `db.sync_usage(conn)` / `db.sync_tracker(conn)`
- `DbReadStep`, `DbWriteStep`, `DbUpsertStep` for pipelines
- `@db.cached` query result cache

## Backward compatibility

`aion.store` (`KeyValueStore`, `ChatHistoryStore`) remains unchanged. SQLite connections expose `.kv` and `.chat` wrappers (`save_thread`, `list_threads`, …).

## CLI and agent

```bash
aion db status
aion db sync-usage
aion db sync-tracker
aion db demo
```

Agent slash commands (**not available** — no `aion agent` in 0.2.0):

```
/db status
/db sync all
/db memory
```

Agent chat persistence to `~/.aion/agent.db` is planned for the restored agent. Use `aion db …` CLI today.

Configure a remote DB:

```bash
aion config db.url "mysql://user:pass@localhost/mydb"
```

## Pandas export

```python
df = conn.table("users").select("name", "score").to_df()  # pip install pandas
```

## Demos

```bash
python -m aion.db.examples.demo_connect
python -m aion.db.examples.demo_dict_api
python -m aion.db.examples.demo_hybrid_search
```

## See also

- [`aion/store/README.md`](../store/README.md) — legacy SQLite stores
- [`aion/pipeline`](../pipeline/) — pipeline steps
