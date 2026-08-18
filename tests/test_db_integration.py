"""Optional integration tests — require live database servers."""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def _skip_unless_env(var: str) -> str:
    val = os.environ.get(var, "").strip()
    if not val:
        pytest.skip(f"Set {var} to run this integration test")
    return val


@pytest.mark.skipif(
    not os.environ.get("PYTEKT_TEST_MYSQL_URL"),
    reason="Set PYTEKT_TEST_MYSQL_URL for MySQL integration test",
)
def test_mysql_connect():
    import pytekt.db as db

    conn = db.connect(os.environ["PYTEKT_TEST_MYSQL_URL"])
    conn.probe.insert({"ping": 1})
    assert conn.probe.count() >= 1
    conn.close()


@pytest.mark.skipif(
    not os.environ.get("PYTEKT_TEST_MONGO_URL"),
    reason="Set PYTEKT_TEST_MONGO_URL for MongoDB integration test",
)
def test_mongo_connect():
    import pytekt.db as db

    conn = db.connect(os.environ["PYTEKT_TEST_MONGO_URL"])
    conn.probe.insert({"ping": 1})
    assert conn.probe.count() >= 1
    conn.close()
