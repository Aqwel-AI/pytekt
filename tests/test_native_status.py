"""Tests for library-wide native backend reporting."""

from aion.native import (
    native_backends,
    native_build_info,
    native_status,
    native_status_report,
    using_any_native_extension,
)


def test_native_backends_contains_core_and_universe():
    backends = native_backends()
    assert "core" in backends
    assert "universe" in backends
    assert "bigdata" in backends
    assert backends["core"].module_name == "aion._aion_core"
    assert backends["universe"].module_name == "aion._aion_universe"
    assert backends["bigdata"].module_name == "aion._aion_bigdata"


def test_native_status_is_dict_shaped():
    status = native_status()
    assert isinstance(status["core"]["available"], bool)
    assert status["core"]["fallback"] == "NumPy"
    assert status["universe"]["fallback"] == "Pure Python"
    assert status["bigdata"]["fallback"] == "NumPy / Python"


def test_using_any_native_extension_returns_bool():
    assert isinstance(using_any_native_extension(), bool)


def test_native_build_info_exposes_sources():
    info = native_build_info()
    assert "src/aion_core.cpp" in info["sources"]
    assert "src/aion_bigdata.cpp" in info["sources"]
    assert "src/aion_universe.cpp" in info["sources"]
    assert info["pybind11_required"] is True


def test_native_status_report_mentions_both_backends():
    report = native_status_report()
    assert "aion core numerics" in report
    assert "aion universe astronomy" in report
    assert "aion big-data kernels" in report
