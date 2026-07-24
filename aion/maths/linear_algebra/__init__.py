"""Vectors, matrices, decompositions, and linear algebra helpers."""

from .functions import (
    cross_product,
    determinant,
    dot_product,
    eigenvalues,
    matrix_inverse,
    matrix_multiply,
    matrix_rank,
    normalize_vector,
    svd,
    transpose,
    vector_magnitude,
)

__all__ = [
    "dot_product", "transpose", "matrix_multiply", "normalize_vector",
    "determinant", "matrix_inverse", "eigenvalues", "svd", "matrix_rank",
    "cross_product", "vector_magnitude",
]
