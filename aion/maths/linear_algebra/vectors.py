"""
vectors.py — Vector Mathematics Library for aion.maths.linear_algebra
"""

from __future__ import annotations

import math
from typing import List, Sequence, Union

Number = Union[int, float]
Vector = List[float]



def dot_product(a: Sequence[Number], b: Sequence[Number]) -> float:
    """
    Compute the scalar dot product of two vectors.

    Args:
        a: First vector (length n).
        b: Second vector (length n).

    Returns:
        Scalar dot product aᵀb.

    Raises:
        ValueError: If vectors have different lengths.

    Examples:
        >>> dot_product([1, 2, 3], [4, 5, 6])
        32.0
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length.")
    return float(sum(x * y for x, y in zip(a, b)))


def cross_product(a: Sequence[Number], b: Sequence[Number]) -> List[float]:
    """
    Compute the cross product of two 3-D vectors.

    Args:
        a: First 3-D vector.
        b: Second 3-D vector.

    Returns:
        Cross product vector (length 3).

    Raises:
        ValueError: If either vector is not 3-D.

    Examples:
        >>> cross_product([1, 0, 0], [0, 1, 0])
        [0.0, 0.0, 1.0]
    """
    if len(a) != 3 or len(b) != 3:
        raise ValueError("Cross product requires 3-D vectors.")
    return [
        float(a[1] * b[2] - a[2] * b[1]),
        float(a[2] * b[0] - a[0] * b[2]),
        float(a[0] * b[1] - a[1] * b[0]),
    ]


def vector_magnitude(v: Sequence[Number]) -> float:
    """
    Compute the Euclidean magnitude (L₂ norm) of a vector.

    Args:
        v: Input vector.

    Returns:
        Magnitude ‖v‖₂.

    Examples:
        >>> vector_magnitude([3, 4])
        5.0
    """
    return math.sqrt(sum(x * x for x in v))


def normalize_vector(v: Sequence[Number], norm: str = "l2") -> List[float]:
    """
    Normalize a vector to unit length.

    Args:
        v: Input vector.
        norm: "l2" (Euclidean, default) or "l1" (Manhattan).

    Returns:
        Normalized unit vector.

    Raises:
        ValueError: If norm is not "l1" or "l2".

    Examples:
        >>> normalize_vector([3, 4])
        [0.6, 0.8]
    """
    if norm == "l2":
        mag = math.sqrt(sum(x * x for x in v))
    elif norm == "l1":
        mag = sum(abs(x) for x in v)
    else:
        raise ValueError("norm must be 'l1' or 'l2'.")
    if mag == 0:
        return [float(x) for x in v]
    return [float(x / mag) for x in v]


def vector_add(a: Sequence[Number], b: Sequence[Number]) -> List[float]:
    """
    Element-wise addition of two equal-length vectors.

    Examples:
        >>> vector_add([1, 2], [3, 4])
        [4.0, 6.0]
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length.")
    return [float(x + y) for x, y in zip(a, b)]


def vector_subtract(a: Sequence[Number], b: Sequence[Number]) -> List[float]:
    """
    Element-wise subtraction of two equal-length vectors (a − b).

    Examples:
        >>> vector_subtract([5, 7], [2, 3])
        [3.0, 4.0]
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length.")
    return [float(x - y) for x, y in zip(a, b)]


def vector_scale(v: Sequence[Number], scalar: Number) -> List[float]:
    """
    Multiply every element of *v* by *scalar*.

    Examples:
        >>> vector_scale([1, 2, 3], 3)
        [3.0, 6.0, 9.0]
    """
    return [float(x * scalar) for x in v]


def angle_between_vectors(a: Sequence[Number], b: Sequence[Number]) -> float:
    """
    Compute the angle in radians between two vectors.

    Args:
        a: First vector.
        b: Second vector (same length as a).

    Returns:
        Angle in [0, π] radians.

    Raises:
        ValueError: If a vector has zero magnitude.

    Examples:
        >>> round(angle_between_vectors([1, 0], [0, 1]), 4)
        1.5708
    """
    mag_a, mag_b = vector_magnitude(a), vector_magnitude(b)
    if mag_a == 0 or mag_b == 0:
        raise ValueError("Cannot compute angle: zero-magnitude vector.")
    cos_theta = max(-1.0, min(1.0, dot_product(a, b) / (mag_a * mag_b)))
    return math.acos(cos_theta)


def vector_project(u: Sequence[Number], v: Sequence[Number]) -> Vector:
    """
    Project vector *u* onto vector *v*.

    Args:
        u: The vector to project.
        v: The vector onto which *u* is projected.

    Returns:
        Projected vector.

    Raises:
        ValueError: If v has zero magnitude or if vectors have different lengths.

    Examples:
        >>> vector_project([3, 4], [1, 0])
        [3.0, 0.0]
    """
    if len(u) != len(v):
        raise ValueError("Vectors must have the same length.")
    mag_v_sq = sum(x * x for x in v)
    if mag_v_sq == 0:
        raise ValueError("Cannot project onto a zero-magnitude vector.")
    scale = dot_product(u, v) / mag_v_sq
    return vector_scale(v, scale)


def vector_reject(u: Sequence[Number], v: Sequence[Number]) -> Vector:
    """
    Compute the vector rejection of *u* from *v* (the orthogonal component).

    Args:
        u: The source vector.
        v: The reference vector.

    Returns:
        Vector component of *u* orthogonal to *v*.

    Examples:
        >>> vector_reject([3, 4], [1, 0])
        [0.0, 4.0]
    """
    proj = vector_project(u, v)
    return vector_subtract(u, proj)


def scalar_triple_product(u: Sequence[Number], v: Sequence[Number], w: Sequence[Number]) -> float:
    """
    Compute the scalar triple product u · (v × w).

    Args:
        u: First 3D vector.
        v: Second 3D vector.
        w: Third 3D vector.

    Returns:
        Scalar triple product.

    Raises:
        ValueError: If any vector is not 3D.

    Examples:
        >>> scalar_triple_product([1, 0, 0], [0, 1, 0], [0, 0, 1])
        1.0
    """
    if len(u) != 3 or len(v) != 3 or len(w) != 3:
        raise ValueError("Scalar triple product requires 3D vectors.")
    return dot_product(u, cross_product(v, w))


__all__ = [
    "Vector",
    "dot_product",
    "cross_product",
    "vector_magnitude",
    "normalize_vector",
    "vector_add",
    "vector_subtract",
    "vector_scale",
    "angle_between_vectors",
    "vector_project",
    "vector_reject",
    "scalar_triple_product",
]
