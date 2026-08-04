import pytest

from aion import maths


def test_math_sections_are_discoverable():
    sections = maths.list_sections()

    assert "arithmetic" in sections
    assert "linear_algebra" in sections
    assert "machine_learning" in sections
    assert "matrix_multiply" in maths.section_functions("linear_algebra")
    assert maths.linear_algebra.matrix_multiply([[2]], [[4]]) == [[8]]


def test_section_functions_returns_a_copy():
    sections = maths.section_functions()
    sections.pop("arithmetic")

    assert "arithmetic" in maths.list_sections()


def test_unknown_math_section_has_helpful_error():
    with pytest.raises(ValueError, match="Unknown maths section"):
        maths.section_functions("calculus")
