"""SQLite-backed persistent vector store with brute-force cosine search."""

from __future__ import annotations

import json
import sqlite3
import threading
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class PersistentVectorStore:
    """
    Persistent vector store using SQLite for storage and brute-force cosine
    similarity for retrieval. Suitable for small-to-medium collections
    (up to ~100k vectors).

    Parameters
    ----------
    db_path : str
        Path to the SQLite database.
    dimension : int
        Vector dimensionality (must be consistent across all inserts).
    """

    def __init__(self, db_path: str = ".aion_vectors.db", dimension: int = 384) -> None:
        self._db_path = db_path
        self._dim = dimension
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, timeout=5)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS vectors "
                "(id TEXT PRIMARY KEY, vector BLOB NOT NULL, text TEXT, metadata TEXT)"
            )

    def add(
        self,
        id: str,
        vector: np.ndarray,
        text: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Insert or update a vector."""
        blob = vector.astype(np.float32).tobytes()
        meta_json = json.dumps(metadata or {}, default=str)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO vectors (id, vector, text, metadata) VALUES (?, ?, ?, ?)",
                    (id, blob, text, meta_json),
                )

    def add_batch(
        self,
        ids: List[str],
        vectors: np.ndarray,
        texts: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Insert multiple vectors in a single transaction."""
        texts = texts or [""] * len(ids)
        metadatas = metadatas or [{}] * len(ids)
        rows = []
        for i, (vid, vec) in enumerate(zip(ids, vectors)):
            rows.append((
                vid,
                vec.astype(np.float32).tobytes(),
                texts[i],
                json.dumps(metadatas[i], default=str),
            ))
        with self._lock:
            with self._connect() as conn:
                conn.executemany(
                    "INSERT OR REPLACE INTO vectors (id, vector, text, metadata) VALUES (?, ?, ?, ?)",
                    rows,
                )

    def query(
        self,
        vector: np.ndarray,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return the *top_k* most similar vectors by cosine similarity."""
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT id, vector, text, metadata FROM vectors"
                ).fetchall()

        if not rows:
            return []

        query_vec = vector.astype(np.float32)
        q_norm = np.linalg.norm(query_vec)
        if q_norm == 0:
            return []

        results: List[Tuple[float, str, str, str]] = []
        for vid, blob, text, meta_json in rows:
            stored = np.frombuffer(blob, dtype=np.float32)
            s_norm = np.linalg.norm(stored)
            if s_norm == 0:
                continue
            sim = float(np.dot(query_vec, stored) / (q_norm * s_norm))
            results.append((sim, vid, text, meta_json))

        results.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": vid,
                "score": score,
                "text": text,
                "metadata": json.loads(meta_json),
            }
            for score, vid, text, meta_json in results[:top_k]
        ]

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT vector, text, metadata FROM vectors WHERE id = ?", (id,)
                ).fetchone()
        if row is None:
            return None
        blob, text, meta_json = row
        return {
            "id": id,
            "vector": np.frombuffer(blob, dtype=np.float32).copy(),
            "text": text,
            "metadata": json.loads(meta_json),
        }

    def delete(self, id: str) -> bool:
        with self._lock:
            with self._connect() as conn:
                c = conn.execute("DELETE FROM vectors WHERE id = ?", (id,))
                return c.rowcount > 0

    def clear(self) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute("DELETE FROM vectors")

    def size(self) -> int:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute("SELECT COUNT(*) FROM vectors").fetchone()
                return row[0] if row else 0

    def __len__(self) -> int:
        return self.size()
