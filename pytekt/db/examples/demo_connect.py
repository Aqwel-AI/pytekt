"""Demo: connect and dict API (SQLite, zero extra deps)."""

from __future__ import annotations

import pytekt.db as db


def main() -> None:
    conn = db.connect("sqlite://./demo_pytekt.db")
    print("Engines:", db.supported_engines())
    conn.users.insert({"name": "Alice", "tags": ["ai", "ml"]})
    print("Users:", conn.users.find(name="Alice"))
    row = (
        conn.table("users")
        .where(conn.col.name == "Alice")
        .select("name", "tags")
        .one()
    )
    print("Builder:", row)
    conn.close()
    print("demo_connect ok")


if __name__ == "__main__":
    main()
