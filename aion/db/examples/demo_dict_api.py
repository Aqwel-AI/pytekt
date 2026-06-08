"""Demo: Mongo-style dict filters on SQLite."""

from __future__ import annotations

import aion.db as db


def main() -> None:
    conn = db.connect("sqlite://./demo_dict.db")
    conn.products.insert_many([
        {"name": "Widget", "price": 9.99, "active": True},
        {"name": "Gadget", "price": 19.99, "active": False},
    ])
    cheap = conn.products.find(price__lt=15)
    print("price < 15:", cheap)
    print("count active:", conn.products.count(active=True))
    conn.close()
    print("demo_dict_api ok")


if __name__ == "__main__":
    main()
