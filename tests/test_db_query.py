"""Unit tests for SQL filter compilation."""

from aion.db.types import Filter, compile_sql_filters, parse_filters


def test_parse_filters_suffix():
    f = parse_filters({"age__gte": 18, "name": "Alice"})
    assert len(f) == 2
    ops = {x.field: x.op for x in f}
    assert ops["age"] == "gte"
    assert ops["name"] == "eq"


def test_compile_sql_filters():
    where, params = compile_sql_filters([
        Filter("age", "gt", 25),
        Filter("city", "eq", "Yerevan"),
    ])
    assert "age > ?" in where
    assert "city = ?" in where
    assert params == [25, "Yerevan"]


def test_compile_in_empty():
    where, params = compile_sql_filters([Filter("id", "in", [])])
    assert where == "0 = 1"
    assert params == []
