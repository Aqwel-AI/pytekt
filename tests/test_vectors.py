import pytest
import math
from aion.maths.linear_algebra.vectors import (
    dot_product,
    cross_product,
    vector_magnitude,
    normalize_vector,
    vector_add,
    vector_subtract,
    vector_scale,
    angle_between_vectors,
    vector_project,
    vector_reject,
    scalar_triple_product,
)


def test_dot_product():
    assert dot_product([1, 2, 3], [4, 5, 6]) == 32.0
    assert dot_product([0, 0], [1, 1]) == 0.0
    assert dot_product([-1, 2], [3, 4]) == 5.0
    with pytest.raises(ValueError, match="same length"):
        dot_product([1, 2], [1, 2, 3])


def test_cross_product():
    assert cross_product([1, 0, 0], [0, 1, 0]) == [0.0, 0.0, 1.0]
    assert cross_product([0, 1, 0], [1, 0, 0]) == [0.0, 0.0, -1.0]
    assert cross_product([1, 2, 3], [4, 5, 6]) == [-3.0, 6.0, -3.0]
    with pytest.raises(ValueError, match="3-D vectors"):
        cross_product([1, 2], [1, 2])


def test_vector_magnitude():
    assert vector_magnitude([3, 4]) == 5.0
    assert vector_magnitude([0, 0, 0]) == 0.0
    assert math.isclose(vector_magnitude([1, 1, 1]), math.sqrt(3))


def test_normalize_vector():
    assert normalize_vector([3, 4]) == [0.6, 0.8]
    assert normalize_vector([0, 0]) == [0.0, 0.0]
    assert normalize_vector([1, 1, 1, 1], norm="l1") == [0.25, 0.25, 0.25, 0.25]
    with pytest.raises(ValueError, match="norm must be"):
        normalize_vector([1, 2], norm="invalid")


def test_vector_add():
    assert vector_add([1, 2], [3, 4]) == [4.0, 6.0]
    with pytest.raises(ValueError, match="same length"):
        vector_add([1, 2], [1, 2, 3])


def test_vector_subtract():
    assert vector_subtract([5, 7], [2, 3]) == [3.0, 4.0]
    with pytest.raises(ValueError, match="same length"):
        vector_subtract([1, 2], [1, 2, 3])


def test_vector_scale():
    assert vector_scale([1, 2, 3], 3) == [3.0, 6.0, 9.0]
    assert vector_scale([0, 0], 5) == [0.0, 0.0]
    assert vector_scale([2.5, -4.0], -2) == [-5.0, 8.0]


def test_angle_between_vectors():
    assert math.isclose(angle_between_vectors([1, 0], [0, 1]), math.pi / 2)
    assert math.isclose(angle_between_vectors([1, 0], [1, 0]), 0.0)
    assert math.isclose(angle_between_vectors([1, 0], [-1, 0]), math.pi)
    with pytest.raises(ValueError, match="zero-magnitude vector"):
        angle_between_vectors([0, 0], [1, 1])


def test_vector_project():
    assert vector_project([3, 4], [1, 0]) == [3.0, 0.0]
    assert vector_project([3, 4], [0, 1]) == [0.0, 4.0]
    with pytest.raises(ValueError, match="same length"):
        vector_project([1, 2], [1, 2, 3])
    with pytest.raises(ValueError, match="zero-magnitude vector"):
        vector_project([1, 2], [0, 0])


def test_vector_reject():
    assert vector_reject([3, 4], [1, 0]) == [0.0, 4.0]
    assert vector_reject([3, 4], [0, 1]) == [3.0, 0.0]


def test_scalar_triple_product():
    assert scalar_triple_product([1, 0, 0], [0, 1, 0], [0, 0, 1]) == 1.0
    with pytest.raises(ValueError, match="3D vectors"):
        scalar_triple_product([1, 2], [1, 2], [1, 2])

