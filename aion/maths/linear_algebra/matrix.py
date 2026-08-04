"""
matrix.py — Comprehensive Matrix Library for aion.maths

100+ matrix functions covering:
  1.  Standard Generators          — zeros, ones, eye, full, arange, linspace …
  2.  Diagonal & Triangular        — diag, triu, tril, tridiagonal, block_diag …
  3.  Random Matrices              — uniform, normal, sparse, orthogonal …
  4.  Special / Named Matrices     — hilbert, toeplitz, vandermonde, hadamard …
  5.  Element-wise Operations      — add, subtract, scale, power, apply …
  6.  Core Linear Algebra          — multiply, determinant, inverse, rank …
  7.  Decompositions               — LU, QR, Cholesky, SVD, Eigenvalues …
  8.  Solvers & Properties         — solve, condition, is_symmetric …
  9.  Reshaping & Slicing          — reshape, flatten, hstack, vstack, pad …
 10.  Geometric / 3-D Matrices     — rotation, translation, projection …
 11.  Analysis & Statistics        — norm, trace, density, sum, std …
 12.  Custom Builders & Pipelines  — rule, distance, adjacency, pipe …

All functions return plain Python lists for maximum interoperability.
NumPy is used internally only where precision or performance demands it.
"""

from __future__ import annotations

import math
import random as _random
from typing import Callable, List, Optional, Sequence, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# Type alias used throughout this module
# ---------------------------------------------------------------------------
Matrix = List[List[float]]
Number = Union[int, float]


# ===========================================================================
# 1. STANDARD GENERATORS
# ===========================================================================

def zeros(rows: int, cols: int) -> Matrix:
    """
    Create a matrix filled with zeros.

    Args:
        rows: Number of rows (must be > 0).
        cols: Number of columns (must be > 0).

    Returns:
        (rows × cols) matrix of 0.0.

    Raises:
        ValueError: If rows or cols are not positive.

    Examples:
        >>> zeros(2, 3)
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    """
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive integers.")
    return [[0.0] * cols for _ in range(rows)]


def ones(rows: int, cols: int) -> Matrix:
    """
    Create a matrix filled with ones.

    Args:
        rows: Number of rows (must be > 0).
        cols: Number of columns (must be > 0).

    Returns:
        (rows × cols) matrix of 1.0.

    Examples:
        >>> ones(2, 2)
        [[1.0, 1.0], [1.0, 1.0]]
    """
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive integers.")
    return [[1.0] * cols for _ in range(rows)]


def eye(n: int, m: Optional[int] = None, k: int = 0) -> Matrix:
    """
    Create a matrix with 1s on the k-th diagonal.

    Args:
        n: Number of rows.
        m: Number of columns (defaults to n for a square matrix).
        k: Diagonal offset — 0 is main, positive is upper, negative is lower.

    Returns:
        (n × m) matrix.

    Examples:
        >>> eye(3)
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        >>> eye(2, 3, k=1)
        [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    """
    if n <= 0:
        raise ValueError("n must be a positive integer.")
    cols = m if m is not None else n
    if cols <= 0:
        raise ValueError("m must be a positive integer.")
    return [[1.0 if j - i == k else 0.0 for j in range(cols)] for i in range(n)]


def identity(n: int) -> Matrix:
    """
    Create a square n × n identity matrix (shorthand for eye(n)).

    Args:
        n: Size of the identity matrix.

    Returns:
        n × n identity matrix.

    Examples:
        >>> identity(2)
        [[1.0, 0.0], [0.0, 1.0]]
    """
    return eye(n)


def full(rows: int, cols: int, fill_value: Number) -> Matrix:
    """
    Create a matrix filled with a constant value.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        fill_value: Value to fill every element with.

    Returns:
        (rows × cols) matrix filled with fill_value.

    Examples:
        >>> full(2, 3, 7)
        [[7, 7, 7], [7, 7, 7]]
    """
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive integers.")
    return [[fill_value] * cols for _ in range(rows)]


def zeros_like(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """
    Return a zero matrix with the same shape as *matrix*.

    Args:
        matrix: Reference matrix.

    Returns:
        Matrix of zeros matching input shape.

    Examples:
        >>> zeros_like([[1, 2], [3, 4]])
        [[0.0, 0.0], [0.0, 0.0]]
    """
    return zeros(len(matrix), len(matrix[0]))


def ones_like(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """
    Return a ones matrix with the same shape as *matrix*.

    Args:
        matrix: Reference matrix.

    Returns:
        Matrix of ones matching input shape.

    Examples:
        >>> ones_like([[1, 2], [3, 4]])
        [[1.0, 1.0], [1.0, 1.0]]
    """
    return ones(len(matrix), len(matrix[0]))


def full_like(matrix: Sequence[Sequence[Number]], fill_value: Number) -> Matrix:
    """
    Return a matrix filled with *fill_value* matching the shape of *matrix*.

    Args:
        matrix: Reference matrix.
        fill_value: Constant value for every element.

    Returns:
        Constant matrix matching input shape.

    Examples:
        >>> full_like([[1, 2], [3, 4]], 9)
        [[9, 9], [9, 9]]
    """
    return full(len(matrix), len(matrix[0]), fill_value)


def arange_matrix(rows: int, cols: int, start: float = 0.0, step: float = 1.0) -> Matrix:
    """
    Create a matrix with sequential values starting at *start* and spaced by *step*.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        start: Starting value (default 0.0).
        step: Increment between values (default 1.0).

    Returns:
        (rows × cols) matrix with sequential values.

    Examples:
        >>> arange_matrix(2, 3, start=1, step=2)
        [[1.0, 3.0, 5.0], [7.0, 9.0, 11.0]]
    """
    val = start
    result: Matrix = []
    for _ in range(rows):
        row = []
        for _ in range(cols):
            row.append(float(val))
            val += step
        result.append(row)
    return result


def linspace_matrix(rows: int, cols: int, start: float = 0.0, stop: float = 1.0) -> Matrix:
    """
    Create a matrix with linearly-spaced values from *start* to *stop*.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        start: First value in the sequence.
        stop: Last value in the sequence.

    Returns:
        (rows × cols) matrix with evenly-spaced values.

    Examples:
        >>> linspace_matrix(1, 5, 0, 1)
        [[0.0, 0.25, 0.5, 0.75, 1.0]]
    """
    total = rows * cols
    if total <= 1:
        vals = [float(start)] * total
    else:
        vals = [start + i * (stop - start) / (total - 1) for i in range(total)]
    result: Matrix = []
    idx = 0
    for _ in range(rows):
        row = [vals[idx + j] for j in range(cols)]
        idx += cols
        result.append(row)
    return result


# ===========================================================================
# 2. DIAGONAL & TRIANGULAR
# ===========================================================================

def diag(values: Sequence[Number], k: int = 0) -> Matrix:
    """
    Create a matrix with *values* placed on the k-th diagonal.

    Args:
        values: Values to put on the diagonal.
        k: Diagonal offset (0 = main, positive = upper, negative = lower).

    Returns:
        Square matrix with values on the k-th diagonal, zeros elsewhere.

    Examples:
        >>> diag([1, 2, 3])
        [[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 3.0]]
    """
    n = len(values) + abs(k)
    mat = zeros(n, n)
    for i, val in enumerate(values):
        if k >= 0:
            mat[i][i + k] = float(val)
        else:
            mat[i - k][i] = float(val)
    return mat


def extract_diag(matrix: Sequence[Sequence[Number]], k: int = 0) -> List[float]:
    """
    Extract elements from the k-th diagonal of a matrix.

    Args:
        matrix: Input matrix.
        k: Diagonal offset.

    Returns:
        List of diagonal elements.

    Examples:
        >>> extract_diag([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        [1.0, 5.0, 9.0]
    """
    rows, cols = len(matrix), len(matrix[0])
    result = []
    for i in range(rows):
        j = i + k
        if 0 <= j < cols:
            result.append(float(matrix[i][j]))
    return result


def triu(matrix: Sequence[Sequence[Number]], k: int = 0) -> Matrix:
    """
    Zero out elements below the k-th diagonal (upper triangular).

    Args:
        matrix: Input matrix.
        k: Diagonal offset — elements below this are zeroed.

    Returns:
        Upper-triangular form of the matrix.

    Examples:
        >>> triu([[1, 2], [3, 4]])
        [[1.0, 2.0], [0.0, 4.0]]
    """
    rows, cols = len(matrix), len(matrix[0])
    return [[float(matrix[i][j]) if j - i >= k else 0.0 for j in range(cols)] for i in range(rows)]


def tril(matrix: Sequence[Sequence[Number]], k: int = 0) -> Matrix:
    """
    Zero out elements above the k-th diagonal (lower triangular).

    Args:
        matrix: Input matrix.
        k: Diagonal offset — elements above this are zeroed.

    Returns:
        Lower-triangular form of the matrix.

    Examples:
        >>> tril([[1, 2], [3, 4]])
        [[1.0, 0.0], [3.0, 4.0]]
    """
    rows, cols = len(matrix), len(matrix[0])
    return [[float(matrix[i][j]) if j - i <= k else 0.0 for j in range(cols)] for i in range(rows)]


def upper_triangular(n: int, val: float = 1.0) -> Matrix:
    """
    Create an n × n upper-triangular matrix filled with *val*.

    Examples:
        >>> upper_triangular(3)
        [[1.0, 1.0, 1.0], [0.0, 1.0, 1.0], [0.0, 0.0, 1.0]]
    """
    return triu(full(n, n, val))


def lower_triangular(n: int, val: float = 1.0) -> Matrix:
    """
    Create an n × n lower-triangular matrix filled with *val*.

    Examples:
        >>> lower_triangular(3)
        [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]]
    """
    return tril(full(n, n, val))


def block_diag(*matrices: Sequence[Sequence[Number]]) -> Matrix:
    """
    Construct a block-diagonal matrix from several matrices.

    Args:
        *matrices: Any number of 2-D matrices placed on the diagonal.

    Returns:
        Combined block-diagonal matrix.

    Examples:
        >>> block_diag([[1, 2], [3, 4]], [[9]])
        [[1.0, 2.0, 0.0], [3.0, 4.0, 0.0], [0.0, 0.0, 9.0]]
    """
    tr = sum(len(m) for m in matrices)
    tc = sum(len(m[0]) for m in matrices)
    res = zeros(tr, tc)
    cr, cc = 0, 0
    for m in matrices:
        r, c = len(m), len(m[0])
        for i in range(r):
            for j in range(c):
                res[cr + i][cc + j] = float(m[i][j])
        cr += r
        cc += c
    return res


def tridiagonal(
    lower: Sequence[Number],
    main: Sequence[Number],
    upper: Sequence[Number],
) -> Matrix:
    """
    Create a tridiagonal matrix from three diagonals.

    Args:
        lower: Sub-diagonal elements (length n-1).
        main: Main diagonal elements (length n).
        upper: Super-diagonal elements (length n-1).

    Returns:
        n × n tridiagonal matrix.

    Examples:
        >>> tridiagonal([1, 1], [2, 2, 2], [3, 3])
        [[2.0, 3.0, 0.0], [1.0, 2.0, 3.0], [0.0, 1.0, 2.0]]
    """
    n = len(main)
    mat = diag(main)
    for i, v in enumerate(upper):
        mat[i][i + 1] = float(v)
    for i, v in enumerate(lower):
        mat[i + 1][i] = float(v)
    return mat


def anti_diagonal(values: Sequence[Number]) -> Matrix:
    """
    Create a square matrix with *values* along the anti-diagonal.

    Args:
        values: Values for the anti-diagonal (length n → n × n matrix).

    Returns:
        n × n matrix with values on the anti-diagonal.

    Examples:
        >>> anti_diagonal([1, 2, 3])
        [[0.0, 0.0, 1.0], [0.0, 2.0, 0.0], [3.0, 0.0, 0.0]]
    """
    n = len(values)
    mat = zeros(n, n)
    for i, v in enumerate(values):
        mat[i][n - 1 - i] = float(v)
    return mat


def exchange_matrix(n: int) -> Matrix:
    """
    Create an n × n exchange (reversal) matrix — 1s on the anti-diagonal.

    Examples:
        >>> exchange_matrix(3)
        [[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
    """
    return anti_diagonal([1.0] * n)


# ===========================================================================
# 3. RANDOM MATRICES
# ===========================================================================

def random_uniform(
    rows: int, cols: int, low: float = 0.0, high: float = 1.0, seed: Optional[int] = None
) -> Matrix:
    """
    Create a matrix with uniform random floats in [low, high).

    Args:
        rows: Number of rows.
        cols: Number of columns.
        low: Lower bound (inclusive).
        high: Upper bound (exclusive).
        seed: Optional random seed for reproducibility.

    Returns:
        (rows × cols) matrix of uniform random floats.

    Examples:
        >>> m = random_uniform(2, 2, seed=42); len(m)
        2
    """
    if seed is not None:
        _random.seed(seed)
    return [[_random.uniform(low, high) for _ in range(cols)] for _ in range(rows)]


def random_normal(
    rows: int, cols: int, mean: float = 0.0, std: float = 1.0, seed: Optional[int] = None
) -> Matrix:
    """
    Create a matrix with Gaussian random values.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        mean: Mean of the distribution.
        std: Standard deviation.
        seed: Optional random seed.

    Returns:
        (rows × cols) matrix of Gaussian random floats.

    Examples:
        >>> m = random_normal(3, 3, seed=0); len(m) == 3
        True
    """
    if seed is not None:
        _random.seed(seed)
    return [[_random.gauss(mean, std) for _ in range(cols)] for _ in range(rows)]


def random_randint(
    rows: int, cols: int, low: int = 0, high: int = 10, seed: Optional[int] = None
) -> List[List[int]]:
    """
    Create a matrix of random integers in [low, high].

    Args:
        rows: Number of rows.
        cols: Number of columns.
        low: Minimum integer value.
        high: Maximum integer value.
        seed: Optional random seed.

    Returns:
        (rows × cols) matrix of random integers.

    Examples:
        >>> m = random_randint(2, 2, 1, 5, seed=0); m[0][0] in range(1, 6)
        True
    """
    if seed is not None:
        _random.seed(seed)
    return [[_random.randint(low, high) for _ in range(cols)] for _ in range(rows)]


def random_bernoulli(
    rows: int, cols: int, p: float = 0.5, seed: Optional[int] = None
) -> List[List[int]]:
    """
    Create a binary matrix where each entry is 1 with probability *p*.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        p: Probability of a 1 (default 0.5).
        seed: Optional random seed.

    Returns:
        (rows × cols) binary integer matrix.

    Examples:
        >>> m = random_bernoulli(2, 2, p=1.0); m
        [[1, 1], [1, 1]]
    """
    if seed is not None:
        _random.seed(seed)
    return [[1 if _random.random() < p else 0 for _ in range(cols)] for _ in range(rows)]


def random_symmetric(
    n: int, low: float = -1.0, high: float = 1.0, seed: Optional[int] = None
) -> Matrix:
    """
    Create a random symmetric matrix (A = Aᵀ).

    Args:
        n: Dimension of the square matrix.
        low: Lower bound for random values.
        high: Upper bound for random values.
        seed: Optional random seed.

    Returns:
        n × n symmetric matrix.

    Examples:
        >>> m = random_symmetric(3, seed=0)
        >>> all(abs(m[i][j] - m[j][i]) < 1e-12 for i in range(3) for j in range(3))
        True
    """
    mat = random_uniform(n, n, low, high, seed=seed)
    for i in range(n):
        for j in range(i + 1, n):
            mat[j][i] = mat[i][j]
    return mat


def random_orthogonal(n: int, seed: Optional[int] = None) -> Matrix:
    """
    Generate a random orthogonal matrix Q (QᵀQ = I) via QR decomposition.

    Args:
        n: Dimension of the square matrix.
        seed: Optional NumPy random seed.

    Returns:
        n × n orthogonal matrix.

    Examples:
        >>> Q = random_orthogonal(3, seed=0)
        >>> len(Q) == 3
        True
    """
    if seed is not None:
        np.random.seed(seed)
    A = np.random.randn(n, n)
    Q, _ = np.linalg.qr(A)
    return Q.tolist()


def random_positive_definite(n: int, seed: Optional[int] = None) -> Matrix:
    """
    Generate a random symmetric positive-definite matrix (A = BBᵀ + nI).

    Args:
        n: Dimension of the square matrix.
        seed: Optional random seed.

    Returns:
        n × n positive-definite symmetric matrix.

    Examples:
        >>> A = random_positive_definite(2, seed=0)
        >>> all(A[i][i] > 0 for i in range(2))
        True
    """
    B = random_normal(n, n, seed=seed)
    res = zeros(n, n)
    for i in range(n):
        for j in range(n):
            res[i][j] = sum(B[i][k] * B[j][k] for k in range(n)) + (float(n) if i == j else 0.0)
    return res


def random_sparse(
    rows: int,
    cols: int,
    density: float = 0.1,
    low: float = 1.0,
    high: float = 10.0,
    seed: Optional[int] = None,
) -> Matrix:
    """
    Create a matrix where only a fraction *density* of entries are non-zero.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        density: Fraction of non-zero entries (0.0–1.0).
        low: Lower bound for non-zero values.
        high: Upper bound for non-zero values.
        seed: Optional random seed.

    Returns:
        (rows × cols) sparse matrix.

    Examples:
        >>> m = random_sparse(5, 5, density=0.2, seed=0)
        >>> sum(x != 0.0 for row in m for x in row) <= 25
        True
    """
    if seed is not None:
        _random.seed(seed)
    mat = zeros(rows, cols)
    for i in range(rows):
        for j in range(cols):
            if _random.random() < density:
                mat[i][j] = _random.uniform(low, high)
    return mat


def random_permutation_matrix(n: int, seed: Optional[int] = None) -> Matrix:
    """
    Generate a random n × n permutation matrix (one 1 per row and column).

    Args:
        n: Dimension.
        seed: Optional random seed.

    Returns:
        n × n permutation matrix.

    Examples:
        >>> P = random_permutation_matrix(3, seed=0)
        >>> [sum(row) for row in P]
        [1.0, 1.0, 1.0]
    """
    if seed is not None:
        _random.seed(seed)
    perm = list(range(n))
    _random.shuffle(perm)
    mat = zeros(n, n)
    for i, p in enumerate(perm):
        mat[i][p] = 1.0
    return mat


def random_correlation_matrix(n: int, seed: Optional[int] = None) -> Matrix:
    """
    Generate a random correlation matrix (positive semidefinite, diagonal = 1).

    Args:
        n: Dimension.
        seed: Optional random seed.

    Returns:
        n × n correlation matrix.

    Examples:
        >>> C = random_correlation_matrix(3, seed=0)
        >>> all(abs(C[i][i] - 1.0) < 1e-9 for i in range(3))
        True
    """
    A = random_positive_definite(n, seed=seed)
    d = [math.sqrt(A[i][i]) for i in range(n)]
    for i in range(n):
        for j in range(n):
            A[i][j] /= d[i] * d[j]
    return A


# ===========================================================================
# 4. SPECIAL / NAMED MATRICES
# ===========================================================================

def hilbert(n: int) -> Matrix:
    """
    Construct the n × n Hilbert matrix (H_ij = 1 / (i + j + 1)).

    The Hilbert matrix is a classic example of an ill-conditioned matrix,
    widely used in numerical analysis and linear algebra benchmarks.

    Args:
        n: Matrix dimension.

    Returns:
        n × n Hilbert matrix.

    Examples:
        >>> hilbert(2)
        [[1.0, 0.5], [0.5, 0.3333333333333333]]
    """
    return [[1.0 / (i + j + 1) for j in range(n)] for i in range(n)]


def inv_hilbert(n: int) -> Matrix:
    """
    Construct the exact integer inverse of the n × n Hilbert matrix.

    Args:
        n: Matrix dimension.

    Returns:
        n × n inverse Hilbert matrix.

    Examples:
        >>> inv_hilbert(2)
        [[4.0, -6.0], [-6.0, 12.0]]
    """
    mat = zeros(n, n)
    for i in range(n):
        for j in range(n):
            sign = (-1) ** (i + j)
            num = (i + j + 1) * math.comb(n + i, n - 1 - j) * math.comb(n + j, n - 1 - i)
            num *= math.comb(i + j, i) ** 2
            mat[i][j] = float(sign * num)
    return mat


def vandermonde(
    v: Sequence[Number], n: Optional[int] = None, increasing: bool = False
) -> Matrix:
    """
    Generate a Vandermonde matrix.

    Each row corresponds to an element of *v* raised to successive powers.

    Args:
        v: 1-D sequence of values (one per row).
        n: Number of columns (defaults to len(v)).
        increasing: If True powers go 0, 1, …, n-1; otherwise n-1, …, 0.

    Returns:
        Vandermonde matrix.

    Examples:
        >>> vandermonde([1, 2, 3], n=3, increasing=True)
        [[1.0, 1.0, 1.0], [1.0, 2.0, 4.0], [1.0, 3.0, 9.0]]
    """
    cols = len(v) if n is None else n
    return [
        [float(x ** (i if increasing else (cols - 1 - i))) for i in range(cols)]
        for x in v
    ]


def toeplitz(
    first_col: Sequence[Number],
    first_row: Optional[Sequence[Number]] = None,
) -> Matrix:
    """
    Construct a Toeplitz matrix (constant along each diagonal).

    Args:
        first_col: First column of the matrix.
        first_row: First row (defaults to *first_col*, giving a symmetric matrix).

    Returns:
        Toeplitz matrix.

    Examples:
        >>> toeplitz([1, 2, 3], [1, 4, 5])
        [[1.0, 4.0, 5.0], [2.0, 1.0, 4.0], [3.0, 2.0, 1.0]]
    """
    if first_row is None:
        first_row = first_col
    r, c = len(first_col), len(first_row)
    mat = zeros(r, c)
    for i in range(r):
        for j in range(c):
            mat[i][j] = float(first_col[i - j] if i >= j else first_row[j - i])
    return mat


def hankel(
    first_col: Sequence[Number],
    last_row: Optional[Sequence[Number]] = None,
) -> Matrix:
    """
    Construct a Hankel matrix (constant along each anti-diagonal).

    Args:
        first_col: First column of the matrix.
        last_row: Last row — defaults to zeros.

    Returns:
        Hankel matrix.

    Examples:
        >>> hankel([1, 2, 3])
        [[1.0, 2.0, 3.0], [2.0, 3.0, 0.0], [3.0, 0.0, 0.0]]
    """
    r = len(first_col)
    c = len(last_row) if last_row is not None else r
    tail = list(last_row[1:]) if last_row is not None else [0.0] * (c - 1)
    vals = list(first_col) + tail
    return [[float(vals[i + j]) for j in range(c)] for i in range(r)]


def circulant(v: Sequence[Number]) -> Matrix:
    """
    Construct a circulant matrix from a 1-D sequence.

    Each row is a cyclic permutation of the previous row.

    Args:
        v: Generator sequence (length n → n × n matrix).

    Returns:
        n × n circulant matrix.

    Examples:
        >>> circulant([1, 2, 3])
        [[1.0, 3.0, 2.0], [2.0, 1.0, 3.0], [3.0, 2.0, 1.0]]
    """
    n = len(v)
    return [[float(v[(j - i) % n]) for j in range(n)] for i in range(n)]


def hadamard_matrix(n: int) -> Matrix:
    """
    Construct a Sylvester-Hadamard matrix of order *n* (n must be a power of 2).

    Args:
        n: Order of the matrix (must be a positive power of 2).

    Returns:
        n × n Hadamard matrix with entries ±1.

    Raises:
        ValueError: If n is not a positive power of 2.

    Examples:
        >>> hadamard_matrix(2)
        [[1.0, 1.0], [1.0, -1.0]]
    """
    if n <= 0 or (n & (n - 1)) != 0:
        raise ValueError("n must be a positive power of 2.")
    H: Matrix = [[1.0]]
    while len(H) < n:
        top = [row + row for row in H]
        bottom = [row + [-x for x in row] for row in H]
        H = top + bottom
    return H


def pascal_matrix(n: int, kind: str = "symmetric") -> Matrix:
    """
    Construct a Pascal matrix.

    Args:
        n: Dimension.
        kind: One of "symmetric", "lower", or "upper".

    Returns:
        n × n Pascal matrix.

    Raises:
        ValueError: If kind is not recognised.

    Examples:
        >>> pascal_matrix(3, 'lower')
        [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 2.0, 1.0]]
    """
    mat = zeros(n, n)
    for i in range(n):
        for j in range(n):
            if kind == "symmetric":
                mat[i][j] = float(math.comb(i + j, i))
            elif kind == "lower":
                mat[i][j] = float(math.comb(i, j)) if i >= j else 0.0
            elif kind == "upper":
                mat[i][j] = float(math.comb(j, i)) if j >= i else 0.0
            else:
                raise ValueError("kind must be 'symmetric', 'lower', or 'upper'.")
    return mat


def companion_matrix(coefficients: Sequence[Number]) -> Matrix:
    """
    Construct the companion matrix for a monic polynomial.

    If p(x) = c₀ + c₁x + … + cₙ₋₁xⁿ⁻¹ + xⁿ, the companion matrix
    has eigenvalues equal to the polynomial's roots.

    Args:
        coefficients: Polynomial coefficients [c₀, c₁, …, cₙ₋₁] (excluding leading 1).

    Returns:
        n × n companion matrix.

    Examples:
        >>> companion_matrix([2, -3])  # x^2 - 3x + 2 → roots 1, 2
        [[0.0, -2.0], [1.0, 3.0]]
    """
    n = len(coefficients)
    mat = zeros(n, n)
    for i in range(n - 1):
        mat[i + 1][i] = 1.0
    for i in range(n):
        mat[i][n - 1] = -float(coefficients[i])
    return mat


def lehmer_matrix(n: int) -> Matrix:
    """
    Construct the n × n Lehmer matrix (L_ij = min(i,j) / max(i,j)).

    Args:
        n: Matrix dimension.

    Returns:
        n × n Lehmer matrix.

    Examples:
        >>> lehmer_matrix(2)
        [[1.0, 0.5], [0.5, 1.0]]
    """
    return [[min(i + 1, j + 1) / max(i + 1, j + 1) for j in range(n)] for i in range(n)]


def cauchy_matrix(x: Sequence[Number], y: Sequence[Number]) -> Matrix:
    """
    Construct a Cauchy matrix C_ij = 1 / (xᵢ − yⱼ).

    Args:
        x: Row parameter sequence.
        y: Column parameter sequence (no element shared with x).

    Returns:
        (len(x) × len(y)) Cauchy matrix.

    Raises:
        ValueError: If any xᵢ equals any yⱼ.

    Examples:
        >>> cauchy_matrix([1, 2], [3, 4])
        [[-0.5, -0.3333333333333333], [-1.0, -0.5]]
    """
    mat = zeros(len(x), len(y))
    for i, xi in enumerate(x):
        for j, yj in enumerate(y):
            if xi == yj:
                raise ValueError(f"x[{i}] == y[{j}]; denominator would be zero.")
            mat[i][j] = 1.0 / float(xi - yj)
    return mat


def laplacian_grid(rows: int, cols: int) -> Matrix:
    """
    Construct the 5-point discrete Laplacian matrix for a 2-D grid.

    Useful for solving PDEs on a rectangular grid of size rows × cols.
    The resulting matrix has size (rows*cols) × (rows*cols).

    Args:
        rows: Number of grid rows.
        cols: Number of grid columns.

    Returns:
        (rows*cols) × (rows*cols) Laplacian matrix.

    Examples:
        >>> L = laplacian_grid(2, 2); len(L)
        4
    """
    n = rows * cols
    mat = zeros(n, n)
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            mat[idx][idx] = -4.0
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    mat[idx][nr * cols + nc] = 1.0
    return mat


# ===========================================================================

# ===========================================================================
# 5. ELEMENT-WISE OPERATIONS
# ===========================================================================

# ===========================================================================

def matrix_add(a: Sequence[Sequence[Number]], b: Sequence[Sequence[Number]]) -> Matrix:
    """
    Element-wise addition of two same-shaped matrices (A + B).

    Args:
        a: First matrix (m × n).
        b: Second matrix (m × n).

    Returns:
        Element-wise sum matrix.

    Raises:
        ValueError: If dimensions differ.

    Examples:
        >>> matrix_add([[1, 2], [3, 4]], [[5, 6], [7, 8]])
        [[6.0, 8.0], [10.0, 12.0]]
    """
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        raise ValueError("Matrices must have identical dimensions for addition.")
    return [[float(a[i][j] + b[i][j]) for j in range(len(a[0]))] for i in range(len(a))]


def matrix_subtract(a: Sequence[Sequence[Number]], b: Sequence[Sequence[Number]]) -> Matrix:
    """
    Element-wise subtraction (A − B).

    Args:
        a: First matrix (m × n).
        b: Second matrix (m × n).

    Returns:
        Element-wise difference matrix.

    Raises:
        ValueError: If dimensions differ.

    Examples:
        >>> matrix_subtract([[5, 6], [7, 8]], [[1, 2], [3, 4]])
        [[4.0, 4.0], [4.0, 4.0]]
    """
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        raise ValueError("Matrices must have identical dimensions for subtraction.")
    return [[float(a[i][j] - b[i][j]) for j in range(len(a[0]))] for i in range(len(a))]


def matrix_multiply_elementwise(a: Sequence[Sequence[Number]], b: Sequence[Sequence[Number]]) -> Matrix:
    """
    Element-wise (Hadamard) product of two same-shaped matrices (A ∘ B).

    Args:
        a: First matrix (m × n).
        b: Second matrix (m × n).

    Returns:
        Element-wise product matrix.

    Examples:
        >>> matrix_multiply_elementwise([[1, 2], [3, 4]], [[2, 2], [2, 2]])
        [[2.0, 4.0], [6.0, 8.0]]
    """
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        raise ValueError("Matrices must have identical dimensions for element-wise multiplication.")
    return [[float(a[i][j] * b[i][j]) for j in range(len(a[0]))] for i in range(len(a))]


def matrix_scale(matrix: Sequence[Sequence[Number]], scalar: Number) -> Matrix:
    """
    Multiply every element of *matrix* by *scalar*.

    Args:
        matrix: Input matrix.
        scalar: Scalar multiplier.

    Returns:
        Scaled matrix.

    Examples:
        >>> matrix_scale([[1, 2], [3, 4]], 2)
        [[2.0, 4.0], [6.0, 8.0]]
    """
    return [[float(x * scalar) for x in row] for row in matrix]


def apply_function(matrix: Sequence[Sequence[Number]], fn: Callable[[float], float]) -> Matrix:
    """
    Apply a custom scalar function element-wise to a matrix.

    Args:
        matrix: Input matrix.
        fn: A callable that accepts and returns a float.

    Returns:
        Matrix with fn applied to every element.

    Examples:
        >>> apply_function([[1, 4], [9, 16]], math.sqrt)
        [[1.0, 2.0], [3.0, 4.0]]
    """
    return [[float(fn(x)) for x in row] for row in matrix]


def clip_matrix(matrix: Sequence[Sequence[Number]], min_val: float, max_val: float) -> Matrix:
    """
    Clamp every element of *matrix* to [min_val, max_val].

    Args:
        matrix: Input matrix.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.

    Returns:
        Clipped matrix.

    Examples:
        >>> clip_matrix([[−2, 5], [3, 10]], 0, 4)
        [[0, 4], [3, 4]]
    """
    return [[float(max(min_val, min(max_val, x))) for x in row] for row in matrix]


def binarize_matrix(matrix: Sequence[Sequence[Number]], threshold: float = 0.0) -> List[List[int]]:
    """
    Convert matrix to binary — 1 where value > threshold, else 0.

    Args:
        matrix: Input matrix.
        threshold: Decision boundary.

    Returns:
        Binary integer matrix.

    Examples:
        >>> binarize_matrix([[−1, 0.5], [0, 2]], threshold=0.0)
        [[0, 1], [0, 1]]
    """
    return [[1 if x > threshold else 0 for x in row] for row in matrix]


def normalize_matrix(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """
    Linearly scale all elements into [0, 1] using min–max normalization.

    Args:
        matrix: Input matrix.

    Returns:
        Normalized matrix with values in [0.0, 1.0].

    Examples:
        >>> normalize_matrix([[1, 2], [3, 4]])
        [[0.0, 0.333...], [0.666..., 1.0]]
    """
    flat = [float(x) for row in matrix for x in row]
    lo, hi = min(flat), max(flat)
    rng = hi - lo or 1.0
    rows, cols = len(matrix), len(matrix[0])
    return [[(float(matrix[i][j]) - lo) / rng for j in range(cols)] for i in range(rows)]


# ===========================================================================
# 6. CORE LINEAR ALGEBRA
# ===========================================================================

def transpose(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """
    Transpose a matrix (swap rows and columns).

    Args:
        matrix: Input matrix (m × n).

    Returns:
        Transposed (n × m) matrix.

    Examples:
        >>> transpose([[1, 2, 3], [4, 5, 6]])
        [[1, 4], [2, 5], [3, 6]]
    """
    return [list(row) for row in zip(*matrix)]


def matrix_multiply(a: Sequence[Sequence[Number]], b: Sequence[Sequence[Number]]) -> Matrix:
    """
    Standard matrix multiplication A @ B.

    Args:
        a: Left matrix (m × k).
        b: Right matrix (k × n).

    Returns:
        Product matrix (m × n).

    Raises:
        ValueError: If inner dimensions do not match.

    Examples:
        >>> matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
        [[19.0, 22.0], [43.0, 50.0]]
    """
    if len(a[0]) != len(b):
        raise ValueError("Inner dimensions must agree: A has %d cols, B has %d rows." % (len(a[0]), len(b)))
    m, k, n = len(a), len(b), len(b[0])
    result = zeros(m, n)
    for i in range(m):
        for j in range(n):
            result[i][j] = sum(float(a[i][p]) * float(b[p][j]) for p in range(k))
    return result


def determinant(matrix: Sequence[Sequence[Number]]) -> float:
    """
    Compute the determinant of a square matrix.

    Uses exact formulas for 1×1 and 2×2; delegates to NumPy for larger sizes.

    Args:
        matrix: Square matrix (n × n).

    Returns:
        Determinant value.

    Raises:
        ValueError: If the matrix is not square.

    Examples:
        >>> determinant([[1, 2], [3, 4]])
        −2.0
    """
    m = [list(row) for row in matrix]
    n = len(m)
    if any(len(row) != n for row in m):
        raise ValueError("Matrix must be square to compute determinant.")
    if n == 1:
        return float(m[0][0])
    if n == 2:
        return float(m[0][0] * m[1][1] - m[0][1] * m[1][0])
    return float(np.linalg.det(m))


def matrix_inverse(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """
    Compute the multiplicative inverse of a square matrix.

    Args:
        matrix: Square invertible matrix (n × n).

    Returns:
        Inverse matrix.

    Raises:
        ValueError: If the matrix is not square or is singular.

    Examples:
        >>> matrix_inverse([[2, 0], [0, 4]])
        [[0.5, 0.0], [0.0, 0.25]]
    """
    arr = np.array(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("Matrix must be square.")
    try:
        return np.linalg.inv(arr).tolist()
    except np.linalg.LinAlgError:
        raise ValueError("Matrix is singular and cannot be inverted.")


def matrix_rank(matrix: Sequence[Sequence[Number]]) -> int:
    """
    Calculate the rank of a matrix.

    Args:
        matrix: Input matrix.

    Returns:
        Numerical rank.

    Examples:
        >>> matrix_rank([[1, 2], [2, 4]])
        1
    """
    return int(np.linalg.matrix_rank(np.array(matrix, dtype=float)))


def matrix_trace(matrix: Sequence[Sequence[Number]]) -> float:
    """
    Sum of the main diagonal elements of a square matrix.

    Args:
        matrix: Square matrix (n × n).

    Returns:
        Trace value.

    Raises:
        ValueError: If not square.

    Examples:
        >>> matrix_trace([[1, 2], [3, 4]])
        5.0
    """
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square to compute trace.")
    return float(sum(matrix[i][i] for i in range(n)))


def matrix_power(matrix: Sequence[Sequence[Number]], power: int) -> Matrix:
    """
    Raise a square matrix to an integer power.

    Args:
        matrix: Square matrix (n × n).
        power: Integer exponent (≥ 0).

    Returns:
        Matrix raised to *power*.

    Raises:
        ValueError: If not square or power < 0.

    Examples:
        >>> matrix_power([[1, 1], [0, 1]], 3)
        [[1.0, 3.0], [0.0, 1.0]]
    """
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square.")
    if power < 0:
        raise ValueError("Power must be a non-negative integer.")
    return np.linalg.matrix_power(np.array(matrix, dtype=float), power).tolist()


def matrix_norm(matrix: Sequence[Sequence[Number]], ord: Optional[Union[int, str]] = "fro") -> float:
    """
    Compute a matrix norm.

    Args:
        matrix: Input matrix.
        ord: Norm type — 'fro' (Frobenius), 1, 2, or np.inf.

    Returns:
        Norm value.

    Examples:
        >>> round(matrix_norm([[1, 2], [3, 4]], 'fro'), 4)
        5.4772
    """
    return float(np.linalg.norm(np.array(matrix, dtype=float), ord=ord))


def pseudo_inverse(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """
    Compute the Moore–Penrose pseudo-inverse of a matrix.

    Works on non-square and rank-deficient matrices.

    Args:
        matrix: Input matrix (m × n).

    Returns:
        Pseudo-inverse (n × m) matrix.

    Examples:
        >>> A = [[1, 0], [0, 1], [0, 0]]
        >>> pseudo_inverse(A)  # returns 2x3 matrix
    """
    return np.linalg.pinv(np.array(matrix, dtype=float)).tolist()


# ===========================================================================
# 7. DECOMPOSITIONS
# ===========================================================================

def lu_decomposition(matrix: Sequence[Sequence[Number]]) -> Tuple[Matrix, Matrix]:
    """
    LU decomposition — A = L @ U (without pivoting).

    Args:
        matrix: Square matrix (n × n).

    Returns:
        Tuple (L, U) of lower and upper triangular matrices.

    Raises:
        ValueError: If not square or a zero pivot is encountered.

    Examples:
        >>> L, U = lu_decomposition([[2, 1], [4, 3]])
        >>> L
        [[1.0, 0.0], [2.0, 1.0]]
    """
    arr = np.array(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("Matrix must be square for LU decomposition.")
    n = arr.shape[0]
    L = np.eye(n, dtype=float)
    U = arr.copy()
    for i in range(n):
        if U[i, i] == 0:
            raise ValueError("Zero pivot encountered — use partial pivoting for this matrix.")
        for j in range(i + 1, n):
            factor = U[j, i] / U[i, i]
            L[j, i] = factor
            U[j, i:] -= factor * U[i, i:]
    return L.tolist(), U.tolist()


def qr_decomposition(matrix: Sequence[Sequence[Number]]) -> Tuple[Matrix, Matrix]:
    """
    QR decomposition — A = Q @ R via Gram-Schmidt (NumPy backend).

    Args:
        matrix: Input matrix (m × n).

    Returns:
        Tuple (Q, R) — orthogonal and upper-triangular matrices.

    Examples:
        >>> Q, R = qr_decomposition([[1, 2], [3, 4]])
        >>> round(Q[0][0], 4)
        -0.3162
    """
    Q, R = np.linalg.qr(np.array(matrix, dtype=float))
    return Q.tolist(), R.tolist()


def cholesky_decomposition(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """
    Cholesky decomposition — A = L @ Lᵀ for symmetric positive-definite A.

    Args:
        matrix: Symmetric positive-definite square matrix.

    Returns:
        Lower triangular factor L.

    Raises:
        ValueError: If not square, not symmetric, or not positive-definite.

    Examples:
        >>> cholesky_decomposition([[4, 2], [2, 3]])
        [[2.0, 0.0], [1.0, 1.4142...]]
    """
    arr = np.array(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("Matrix must be square.")
    if not np.allclose(arr, arr.T):
        raise ValueError("Matrix must be symmetric.")
    try:
        return np.linalg.cholesky(arr).tolist()
    except np.linalg.LinAlgError:
        raise ValueError("Matrix is not positive-definite.")


def svd(matrix: Sequence[Sequence[Number]]) -> Tuple[Matrix, List[float], Matrix]:
    """
    Singular Value Decomposition — A = U @ diag(S) @ Vᵀ.

    Args:
        matrix: Input matrix (m × n).

    Returns:
        Tuple (U, S, Vt) where S is a list of singular values.

    Examples:
        >>> U, S, Vt = svd([[1, 2], [3, 4], [5, 6]])
        >>> len(S)
        2
    """
    U, S, Vt = np.linalg.svd(np.array(matrix, dtype=float))
    return U.tolist(), S.tolist(), Vt.tolist()


def eigenvalues(matrix: Sequence[Sequence[Number]]) -> List[complex]:
    """
    Compute eigenvalues of a square matrix (may be complex).

    Args:
        matrix: Square matrix (n × n).

    Returns:
        List of n eigenvalues.

    Raises:
        ValueError: If matrix is not square.

    Examples:
        >>> eigenvalues([[2, 0], [0, 3]])
        [(2+0j), (3+0j)]
    """
    arr = np.array(matrix, dtype=float)
    if arr.shape[0] != arr.shape[1]:
        raise ValueError("Matrix must be square.")
    return np.linalg.eigvals(arr).tolist()


def eigenvectors(matrix: Sequence[Sequence[Number]]) -> Tuple[List[complex], Matrix]:
    """
    Compute eigenvalues and right eigenvectors of a square matrix.

    Args:
        matrix: Square matrix (n × n).

    Returns:
        Tuple (eigenvalues, eigenvectors) where each column of the matrix
        is an eigenvector corresponding to the matching eigenvalue.

    Examples:
        >>> vals, vecs = eigenvectors([[2, 0], [0, 3]])
        >>> vals
        [(2+0j), (3+0j)]
    """
    arr = np.array(matrix, dtype=float)
    if arr.shape[0] != arr.shape[1]:
        raise ValueError("Matrix must be square.")
    vals, vecs = np.linalg.eig(arr)
    return vals.tolist(), vecs.tolist()


# ===========================================================================
# 8. SOLVERS & MATRIX PROPERTIES
# ===========================================================================

def solve_linear_system(
    a: Sequence[Sequence[Number]],
    b: Union[Sequence[Number], Sequence[Sequence[Number]]],
) -> Union[List[float], Matrix]:
    """
    Solve the linear equation system A @ x = b.

    Args:
        a: Coefficient square matrix (n × n).
        b: Right-hand-side vector (n,) or matrix (n × k).

    Returns:
        Solution vector x or matrix X.

    Raises:
        ValueError: If A is not square or is singular.

    Examples:
        >>> solve_linear_system([[3, 1], [1, 2]], [9, 8])
        [2.0, 3.0]
    """
    a_arr = np.array(a, dtype=float)
    b_arr = np.array(b, dtype=float)
    if a_arr.ndim != 2 or a_arr.shape[0] != a_arr.shape[1]:
        raise ValueError("Coefficient matrix A must be square.")
    try:
        return np.linalg.solve(a_arr, b_arr).tolist()
    except np.linalg.LinAlgError:
        raise ValueError("Matrix A is singular — system has no unique solution.")


def least_squares(
    a: Sequence[Sequence[Number]],
    b: Sequence[Number],
) -> List[float]:
    """
    Solve the least-squares problem: minimise ‖Ax − b‖₂.

    Args:
        a: Coefficient matrix (m × n).
        b: Right-hand-side vector (m,).

    Returns:
        Least-squares solution vector (n,).

    Examples:
        >>> least_squares([[1, 1], [1, 2], [1, 3]], [1, 2, 2])
        [0.333..., 0.5]
    """
    x, _, _, _ = np.linalg.lstsq(np.array(a, dtype=float), np.array(b, dtype=float), rcond=None)
    return x.tolist()


def condition_number(matrix: Sequence[Sequence[Number]], p: Optional[Union[int, str]] = None) -> float:
    """
    Calculate the condition number of a matrix (ratio of largest to smallest singular value).

    Args:
        matrix: Input matrix.
        p: Norm order passed to numpy (None, 1, 2, np.inf, 'fro').

    Returns:
        Condition number (≥ 1.0).

    Examples:
        >>> round(condition_number([[1, 0], [0, 1]]), 2)
        1.0
    """
    return float(np.linalg.cond(np.array(matrix, dtype=float), p=p))


def is_symmetric(matrix: Sequence[Sequence[Number]], tol: float = 1e-8) -> bool:
    """
    Check if a matrix equals its own transpose within *tol*.

    Args:
        matrix: Input matrix.
        tol: Absolute numerical tolerance.

    Returns:
        True if symmetric.

    Examples:
        >>> is_symmetric([[1, 2], [2, 1]])
        True
    """
    arr = np.array(matrix, dtype=float)
    return arr.ndim == 2 and arr.shape[0] == arr.shape[1] and bool(np.allclose(arr, arr.T, atol=tol))


def is_positive_definite(matrix: Sequence[Sequence[Number]]) -> bool:
    """
    Check if a real symmetric matrix is positive-definite (all eigenvalues > 0).

    Args:
        matrix: Input square matrix.

    Returns:
        True if positive-definite.

    Examples:
        >>> is_positive_definite([[2, -1], [-1, 2]])
        True
    """
    arr = np.array(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        return False
    if not np.allclose(arr, arr.T):
        return False
    return bool(np.all(np.linalg.eigvalsh(arr) > 0))


def is_orthogonal(matrix: Sequence[Sequence[Number]], tol: float = 1e-8) -> bool:
    """
    Check if a matrix is orthogonal (QᵀQ = I).

    Args:
        matrix: Input square matrix.
        tol: Absolute numerical tolerance.

    Returns:
        True if orthogonal.

    Examples:
        >>> is_orthogonal([[0, 1], [-1, 0]])
        True
    """
    arr = np.array(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        return False
    return bool(np.allclose(arr.T @ arr, np.eye(arr.shape[0]), atol=tol))


def is_square_matrix(matrix: Sequence[Sequence[Number]]) -> bool:
    """Return True if *matrix* has equal numbers of rows and columns."""
    return len(matrix) == len(matrix[0])


def is_diagonal_matrix(matrix: Sequence[Sequence[Number]], tol: float = 1e-8) -> bool:
    """
    Return True if all off-diagonal elements are within *tol* of zero.

    Examples:
        >>> is_diagonal_matrix([[3, 0], [0, 7]])
        True
    """
    if not is_square_matrix(matrix):
        return False
    n = len(matrix)
    return all(abs(matrix[i][j]) <= tol for i in range(n) for j in range(n) if i != j)


def is_matrix_equal(
    a: Sequence[Sequence[Number]],
    b: Sequence[Sequence[Number]],
    tol: float = 1e-8,
) -> bool:
    """
    Check element-wise equality of two matrices within a tolerance.

    Args:
        a: First matrix.
        b: Second matrix.
        tol: Absolute tolerance.

    Returns:
        True if every |a_ij − b_ij| ≤ tol.

    Examples:
        >>> is_matrix_equal([[1, 2], [3, 4]], [[1, 2], [3, 4]])
        True
    """
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return False
    return all(abs(a[i][j] - b[i][j]) <= tol for i in range(len(a)) for j in range(len(a[0])))


# ===========================================================================
# 9. RESHAPING & SLICING
# ===========================================================================

def reshape_matrix(matrix: Sequence[Sequence[Number]], new_rows: int, new_cols: int) -> Matrix:
    """
    Reshape *matrix* into a new shape without changing element order.

    Args:
        matrix: Input matrix.
        new_rows: Target number of rows.
        new_cols: Target number of columns.

    Returns:
        Reshaped matrix.

    Raises:
        ValueError: If total element count changes.

    Examples:
        >>> reshape_matrix([[1, 2, 3], [4, 5, 6]], 3, 2)
        [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    """
    flat = [float(x) for row in matrix for x in row]
    if len(flat) != new_rows * new_cols:
        raise ValueError("Cannot reshape: element count mismatch.")
    return [flat[i * new_cols:(i + 1) * new_cols] for i in range(new_rows)]


def flatten_matrix(matrix: Sequence[Sequence[Number]]) -> List[float]:
    """
    Flatten a 2-D matrix into a 1-D list (row-major order).

    Examples:
        >>> flatten_matrix([[1, 2], [3, 4]])
        [1.0, 2.0, 3.0, 4.0]
    """
    return [float(x) for row in matrix for x in row]


def slice_matrix(
    matrix: Sequence[Sequence[Number]],
    row_start: int, row_end: int,
    col_start: int, col_end: int,
) -> Matrix:
    """
    Extract a rectangular submatrix.

    Args:
        matrix: Source matrix.
        row_start: First row index (inclusive).
        row_end: Last row index (exclusive).
        col_start: First column index (inclusive).
        col_end: Last column index (exclusive).

    Returns:
        Sub-matrix view.

    Examples:
        >>> slice_matrix([[1,2,3],[4,5,6],[7,8,9]], 0, 2, 1, 3)
        [[2.0, 3.0], [5.0, 6.0]]
    """
    return [
        [float(matrix[r][c]) for c in range(col_start, col_end)]
        for r in range(row_start, row_end)
    ]


def hstack(*matrices: Sequence[Sequence[Number]]) -> Matrix:
    """
    Horizontally stack matrices side-by-side.

    Args:
        *matrices: Matrices with equal numbers of rows.

    Returns:
        Horizontally concatenated matrix.

    Raises:
        ValueError: If row counts differ.

    Examples:
        >>> hstack([[1, 2]], [[3, 4]])
        [[1.0, 2.0, 3.0, 4.0]]
    """
    rows = len(matrices[0])
    if any(len(m) != rows for m in matrices):
        raise ValueError("All matrices must have the same number of rows for hstack.")
    return [[float(x) for m in matrices for x in m[r]] for r in range(rows)]


def vstack(*matrices: Sequence[Sequence[Number]]) -> Matrix:
    """
    Vertically stack matrices row-by-row.

    Args:
        *matrices: Matrices with equal numbers of columns.

    Returns:
        Vertically concatenated matrix.

    Raises:
        ValueError: If column counts differ.

    Examples:
        >>> vstack([[1, 2]], [[3, 4]])
        [[1.0, 2.0], [3.0, 4.0]]
    """
    cols = len(matrices[0][0])
    if any(len(m[0]) != cols for m in matrices):
        raise ValueError("All matrices must have the same number of columns for vstack.")
    return [[float(x) for x in row] for m in matrices for row in m]


def pad_matrix(
    matrix: Sequence[Sequence[Number]],
    pad_top: int = 0,
    pad_bottom: int = 0,
    pad_left: int = 0,
    pad_right: int = 0,
    value: float = 0.0,
) -> Matrix:
    """
    Pad a matrix with a constant value on all four sides.

    Args:
        matrix: Input matrix.
        pad_top: Rows to add above.
        pad_bottom: Rows to add below.
        pad_left: Columns to add to the left.
        pad_right: Columns to add to the right.
        value: Fill value (default 0.0).

    Returns:
        Padded matrix.

    Examples:
        >>> pad_matrix([[1, 2]], pad_top=1, pad_left=1)
        [[0.0, 0.0, 0.0], [0.0, 1.0, 2.0]]
    """
    r, c = len(matrix), len(matrix[0])
    nr, nc = r + pad_top + pad_bottom, c + pad_left + pad_right
    result = full(nr, nc, value)
    for i in range(r):
        for j in range(c):
            result[pad_top + i][pad_left + j] = float(matrix[i][j])
    return result


def kron(a: Sequence[Sequence[Number]], b: Sequence[Sequence[Number]]) -> Matrix:
    """
    Compute the Kronecker (tensor) product of two matrices.

    Args:
        a: First matrix.
        b: Second matrix.

    Returns:
        Kronecker product matrix.

    Examples:
        >>> kron([[1, 0], [0, 1]], [[0, 5], [6, 7]])
        [[0.0, 5.0, 0.0, 0.0], [6.0, 7.0, 0.0, 0.0], [0.0, 0.0, 0.0, 5.0], [0.0, 0.0, 6.0, 7.0]]
    """
    return np.kron(np.array(a), np.array(b)).tolist()


def flipud(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """Flip matrix upside down (reverse row order)."""
    return [[float(x) for x in row] for row in reversed(matrix)]


def fliplr(matrix: Sequence[Sequence[Number]]) -> Matrix:
    """Flip matrix left-to-right (reverse column order)."""
    return [[float(x) for x in reversed(row)] for row in matrix]


def rotate90(matrix: Sequence[Sequence[Number]], k: int = 1) -> Matrix:
    """
    Rotate matrix 90° counter-clockwise *k* times.

    Args:
        matrix: Input matrix.
        k: Number of 90° rotations.

    Returns:
        Rotated matrix.

    Examples:
        >>> rotate90([[1, 2], [3, 4]])
        [[2.0, 4.0], [1.0, 3.0]]
    """
    return np.rot90(np.array(matrix, dtype=float), k=k).tolist()


def split_matrix(
    matrix: Sequence[Sequence[Number]], num_sections: int, axis: int = 0
) -> List[Matrix]:
    """
    Split a matrix into *num_sections* sub-matrices along *axis*.

    Args:
        matrix: Input matrix.
        num_sections: Number of equally-sized parts.
        axis: 0 for row split, 1 for column split.

    Returns:
        List of sub-matrices.

    Examples:
        >>> split_matrix([[1,2],[3,4],[5,6]], 3, axis=0)
        [[[1.0, 2.0]], [[3.0, 4.0]], [[5.0, 6.0]]]
    """
    return [s.tolist() for s in np.array_split(np.array(matrix, dtype=float), num_sections, axis=axis)]


def repeat_matrix(matrix: Sequence[Sequence[Number]], row_reps: int, col_reps: int) -> Matrix:
    """
    Tile *matrix* by repeating it *row_reps × col_reps* times.

    Args:
        matrix: Input matrix.
        row_reps: Times to repeat vertically.
        col_reps: Times to repeat horizontally.

    Returns:
        Tiled matrix.

    Examples:
        >>> repeat_matrix([[1, 2]], 2, 3)
        [[1.0, 2.0, 1.0, 2.0, 1.0, 2.0], [1.0, 2.0, 1.0, 2.0, 1.0, 2.0]]
    """
    r, c = len(matrix), len(matrix[0])
    return [
        [float(matrix[i % r][j % c]) for j in range(c * col_reps)]
        for i in range(r * row_reps)
    ]


# ===========================================================================
# 10. GEOMETRIC / 3-D MATRICES
# ===========================================================================

def rotation_matrix_2d(angle_rad: float) -> Matrix:
    """
    2×2 rotation matrix for counter-clockwise rotation by *angle_rad*.

    Examples:
        >>> import math; R = rotation_matrix_2d(math.pi / 2)
        >>> round(R[0][0], 5)
        0.0
    """
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return [[c, -s], [s, c]]


def scaling_matrix_2d(sx: float, sy: float) -> Matrix:
    """2×2 scaling matrix."""
    return [[sx, 0.0], [0.0, sy]]


def shear_matrix_2d(shx: float = 0.0, shy: float = 0.0) -> Matrix:
    """2×2 shear matrix."""
    return [[1.0, shx], [shy, 1.0]]


def reflection_matrix_2d(normal: Sequence[float]) -> Matrix:
    """
    2×2 reflection matrix across the line defined by unit *normal*.

    Examples:
        >>> reflection_matrix_2d([1, 0])  # Reflect across Y-axis
        [[-1.0, 0.0], [0.0, 1.0]]
    """
    n = np.array(normal, dtype=float)
    n = n / np.linalg.norm(n)
    return (np.eye(2) - 2.0 * np.outer(n, n)).tolist()


def translation_matrix_2d(tx: float, ty: float) -> Matrix:
    """3×3 affine translation matrix for 2-D homogeneous coordinates."""
    return [[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]]


def rotation_matrix_3d_x(angle_rad: float) -> Matrix:
    """4×4 rotation matrix around the X-axis."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return [[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]]


def rotation_matrix_3d_y(angle_rad: float) -> Matrix:
    """4×4 rotation matrix around the Y-axis."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return [[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]]


def rotation_matrix_3d_z(angle_rad: float) -> Matrix:
    """4×4 rotation matrix around the Z-axis."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return [[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]]


def scaling_matrix_3d(sx: float, sy: float, sz: float) -> Matrix:
    """4×4 3-D scaling matrix."""
    return [[sx,0,0,0],[0,sy,0,0],[0,0,sz,0],[0,0,0,1]]


def translation_matrix_3d(tx: float, ty: float, tz: float) -> Matrix:
    """4×4 3-D translation matrix (homogeneous coordinates)."""
    return [[1,0,0,tx],[0,1,0,ty],[0,0,1,tz],[0,0,0,1]]


def euler_rotation_matrix(yaw: float, pitch: float, roll: float) -> Matrix:
    """
    3×3 rotation matrix from Euler angles (yaw, pitch, roll) in radians.

    Args:
        yaw: Rotation about Z-axis.
        pitch: Rotation about Y-axis.
        roll: Rotation about X-axis.

    Returns:
        3×3 combined rotation matrix.
    """
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    return [
        [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
        [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
        [-sp,   cp*sr,            cp*cr],
    ]


def perspective_projection_matrix(fov_rad: float, aspect: float, near: float, far: float) -> Matrix:
    """
    4×4 OpenGL-style perspective projection matrix.

    Args:
        fov_rad: Vertical field-of-view in radians.
        aspect: Width / height aspect ratio.
        near: Near clipping plane distance.
        far: Far clipping plane distance.

    Returns:
        4×4 perspective matrix.
    """
    f = 1.0 / math.tan(fov_rad / 2.0)
    return [
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), 2*far*near / (near - far)],
        [0, 0, -1, 0],
    ]


def orthographic_projection_matrix(
    left: float, right: float, bottom: float, top: float, near: float, far: float
) -> Matrix:
    """4×4 orthographic projection matrix."""
    return [
        [2/(right-left), 0, 0, -(right+left)/(right-left)],
        [0, 2/(top-bottom), 0, -(top+bottom)/(top-bottom)],
        [0, 0, -2/(far-near), -(far+near)/(far-near)],
        [0, 0, 0, 1],
    ]


def householder_reflection_matrix(v: Sequence[float]) -> Matrix:
    """
    Householder reflector H = I − 2vvᵀ / ‖v‖².

    Args:
        v: Reflection vector.

    Returns:
        n × n Householder matrix.

    Examples:
        >>> H = householder_reflection_matrix([1, 0])
        >>> H
        [[-1.0, 0.0], [0.0, 1.0]]
    """
    v_arr = np.array(v, dtype=float).reshape(-1, 1)
    n = len(v)
    H = np.eye(n) - 2.0 * (v_arr @ v_arr.T) / (v_arr.T @ v_arr)
    return H.tolist()


# ===========================================================================
# 11. ANALYSIS & STATISTICS
# ===========================================================================

def matrix_shape(matrix: Sequence[Sequence[Number]]) -> Tuple[int, int]:
    """Return (rows, cols) shape of *matrix*."""
    return len(matrix), len(matrix[0])


def matrix_size(matrix: Sequence[Sequence[Number]]) -> int:
    """Return total number of elements."""
    return len(matrix) * len(matrix[0])


def matrix_min(matrix: Sequence[Sequence[Number]]) -> float:
    """Return minimum value in *matrix*."""
    return float(min(x for row in matrix for x in row))


def matrix_max(matrix: Sequence[Sequence[Number]]) -> float:
    """Return maximum value in *matrix*."""
    return float(max(x for row in matrix for x in row))


def matrix_mean(matrix: Sequence[Sequence[Number]]) -> float:
    """Return mean of all elements."""
    return float(sum(x for row in matrix for x in row) / matrix_size(matrix))


def matrix_std(matrix: Sequence[Sequence[Number]]) -> float:
    """Return standard deviation of all elements."""
    return float(np.std(np.array(matrix, dtype=float)))


def matrix_sum(
    matrix: Sequence[Sequence[Number]], axis: Optional[int] = None
) -> Union[float, List[float]]:
    """
    Sum matrix elements.

    Args:
        matrix: Input matrix.
        axis: None → total sum; 0 → column sums; 1 → row sums.

    Returns:
        Scalar or list of sums.

    Examples:
        >>> matrix_sum([[1, 2], [3, 4]], axis=1)
        [3.0, 7.0]
    """
    if axis is None:
        return float(sum(x for row in matrix for x in row))
    if axis == 0:
        return [float(sum(matrix[r][c] for r in range(len(matrix)))) for c in range(len(matrix[0]))]
    if axis == 1:
        return [float(sum(row)) for row in matrix]
    raise ValueError("axis must be None, 0, or 1.")


def matrix_density(matrix: Sequence[Sequence[Number]], zero_tol: float = 1e-9) -> float:
    """Fraction of elements that are non-zero (0.0 → all zero, 1.0 → no zeros)."""
    total = matrix_size(matrix)
    nz = sum(1 for row in matrix for x in row if abs(x) > zero_tol)
    return nz / total


def matrix_sparsity(matrix: Sequence[Sequence[Number]], zero_tol: float = 1e-9) -> float:
    """Fraction of elements that are zero (1 − density)."""
    return 1.0 - matrix_density(matrix, zero_tol)


def matrix_frobenius_norm(matrix: Sequence[Sequence[Number]]) -> float:
    """Frobenius norm √(Σ xᵢⱼ²)."""
    return math.sqrt(sum(x * x for row in matrix for x in row))


def matrix_infinity_norm(matrix: Sequence[Sequence[Number]]) -> float:
    """Max absolute row sum norm."""
    return float(max(sum(abs(x) for x in row) for row in matrix))


def matrix_one_norm(matrix: Sequence[Sequence[Number]]) -> float:
    """Max absolute column sum norm."""
    cols = len(matrix[0])
    return float(max(sum(abs(matrix[r][c]) for r in range(len(matrix))) for c in range(cols)))


# ===========================================================================
# 12. CUSTOM BUILDERS & PIPELINE TOOLS
# ===========================================================================

def create_matrix_from_rule(
    rows: int, cols: int, rule_fn: Callable[[int, int], float]
) -> Matrix:
    """
    Build a matrix where entry (i, j) = rule_fn(i, j).

    Args:
        rows: Number of rows.
        cols: Number of columns.
        rule_fn: A function accepting (row_index, col_index) and returning a float.

    Returns:
        (rows × cols) matrix populated by rule_fn.

    Examples:
        >>> create_matrix_from_rule(3, 3, lambda i, j: i + j)
        [[0.0, 1.0, 2.0], [1.0, 2.0, 3.0], [2.0, 3.0, 4.0]]

        >>> create_matrix_from_rule(4, 4, lambda i, j: 1 if i == j else 0)  # identity
    """
    return [[float(rule_fn(i, j)) for j in range(cols)] for i in range(rows)]


def create_distance_matrix(
    points: Sequence[Sequence[float]], metric: str = "euclidean"
) -> Matrix:
    """
    Compute pairwise distance matrix for a set of point vectors.

    Args:
        points: Sequence of vectors (all same dimension).
        metric: "euclidean", "manhattan", or "cosine".

    Returns:
        Symmetric (n × n) distance matrix.

    Examples:
        >>> pts = [[0, 0], [3, 0], [0, 4]]
        >>> create_distance_matrix(pts)
        [[0.0, 3.0, 4.0], [3.0, 0.0, 5.0], [4.0, 5.0, 0.0]]
    """
    n = len(points)
    pts_arr = [np.array(p, dtype=float) for p in points]
    mat = zeros(n, n)
    for i in range(n):
        for j in range(i + 1, n):
            if metric == "euclidean":
                d = float(np.linalg.norm(pts_arr[i] - pts_arr[j]))
            elif metric == "manhattan":
                d = float(np.sum(np.abs(pts_arr[i] - pts_arr[j])))
            elif metric == "cosine":
                ni, nj = float(np.linalg.norm(pts_arr[i])), float(np.linalg.norm(pts_arr[j]))
                d = 1.0 - float(np.dot(pts_arr[i], pts_arr[j])) / (ni * nj) if ni and nj else 0.0
            else:
                raise ValueError(f"Unknown metric '{metric}'. Use 'euclidean', 'manhattan', or 'cosine'.")
            mat[i][j] = d
            mat[j][i] = d
    return mat


def create_adjacency_matrix(
    num_nodes: int,
    edges: Sequence[Tuple[int, int]],
    directed: bool = False,
) -> Matrix:
    """
    Build a graph adjacency matrix from edge tuples.

    Args:
        num_nodes: Total number of nodes.
        edges: Sequence of (u, v) edge tuples.
        directed: If False (default), edges are undirected.

    Returns:
        (num_nodes × num_nodes) binary adjacency matrix.

    Examples:
        >>> create_adjacency_matrix(3, [(0, 1), (1, 2)])
        [[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]]
    """
    mat = zeros(num_nodes, num_nodes)
    for u, v in edges:
        mat[u][v] = 1.0
        if not directed:
            mat[v][u] = 1.0
    return mat


def create_weight_matrix(
    num_nodes: int,
    weighted_edges: Sequence[Tuple[int, int, float]],
    directed: bool = False,
) -> Matrix:
    """
    Build a weighted graph adjacency matrix from (u, v, weight) tuples.

    Args:
        num_nodes: Total number of nodes.
        weighted_edges: Sequence of (u, v, weight) tuples.
        directed: If False (default), edges are undirected.

    Returns:
        (num_nodes × num_nodes) weighted adjacency matrix.

    Examples:
        >>> create_weight_matrix(3, [(0, 1, 0.9), (1, 2, 2.5)])
        [[0.0, 0.9, 0.0], [0.9, 0.0, 2.5], [0.0, 2.5, 0.0]]
    """
    mat = zeros(num_nodes, num_nodes)
    for u, v, w in weighted_edges:
        mat[u][v] = float(w)
        if not directed:
            mat[v][u] = float(w)
    return mat


def custom_matrix_pipe(
    matrix: Sequence[Sequence[Number]],
    *transforms: Callable[[Matrix], Matrix],
) -> Matrix:
    """
    Apply a chain of transformation functions to a matrix in order.

    Each transform receives the output of the previous one, allowing
    clean, readable matrix processing pipelines without nesting.

    Args:
        matrix: Starting matrix.
        *transforms: Functions of signature (Matrix) → Matrix.

    Returns:
        Final transformed matrix.

    Examples:
        >>> custom_matrix_pipe([[1, 2], [3, 4]], flipud, lambda m: matrix_scale(m, 2))
        [[6.0, 8.0], [2.0, 4.0]]
    """
    current: Matrix = [[float(x) for x in row] for row in matrix]
    for transform in transforms:
        current = transform(current)
    return current


class CustomMatrixBuilder:
    """
    Fluent builder for constructing matrices step-by-step.

    Supports method chaining so matrices can be built declaratively:

    Examples:
        >>> mat = (
        ...     CustomMatrixBuilder(3, 3)
        ...     .fill(0)
        ...     .set_entry(1, 1, 99)
        ...     .apply_rule(lambda i, j: i + j if i != 1 or j != 1 else 99)
        ...     .build()
        ... )
    """

    def __init__(self, rows: int, cols: int):
        """
        Initialise a rows × cols zero matrix.

        Args:
            rows: Number of rows.
            cols: Number of columns.
        """
        self._rows = rows
        self._cols = cols
        self._data: Matrix = zeros(rows, cols)

    def fill(self, value: float) -> "CustomMatrixBuilder":
        """Fill every element with *value*."""
        self._data = full(self._rows, self._cols, value)
        return self

    def set_entry(self, row: int, col: int, value: float) -> "CustomMatrixBuilder":
        """Set the element at (row, col) to *value*."""
        self._data[row][col] = float(value)
        return self

    def apply_rule(self, rule_fn: Callable[[int, int], float]) -> "CustomMatrixBuilder":
        """Replace every element (i, j) with rule_fn(i, j)."""
        self._data = create_matrix_from_rule(self._rows, self._cols, rule_fn)
        return self

    def apply_transform(self, transform: Callable[[Matrix], Matrix]) -> "CustomMatrixBuilder":
        """Apply an arbitrary transform function to the current state."""
        self._data = transform(self._data)
        return self

    def build(self) -> Matrix:
        """Return the constructed matrix as a plain Python list."""
        return [[v for v in row] for row in self._data]

    def __repr__(self) -> str:
        return f"CustomMatrixBuilder({self._rows}x{self._cols})"


# ===========================================================================
# Public API
# ===========================================================================

__all__ = [
    # 1. Standard Generators
    "zeros", "ones", "eye", "identity", "full",
    "zeros_like", "ones_like", "full_like",
    "arange_matrix", "linspace_matrix",
    # 2. Diagonal & Triangular
    "diag", "extract_diag", "triu", "tril",
    "upper_triangular", "lower_triangular",
    "block_diag", "tridiagonal", "anti_diagonal", "exchange_matrix",
    # 3. Random Matrices
    "random_uniform", "random_normal", "random_randint", "random_bernoulli",
    "random_symmetric", "random_orthogonal", "random_positive_definite",
    "random_sparse", "random_permutation_matrix", "random_correlation_matrix",
    # 4. Special / Named Matrices
    "hilbert", "inv_hilbert", "vandermonde", "toeplitz", "hankel", "circulant",
    "hadamard_matrix", "pascal_matrix", "companion_matrix",
    "lehmer_matrix", "cauchy_matrix", "laplacian_grid",
    # 5. Element-wise Operations
    "matrix_add", "matrix_subtract", "matrix_multiply_elementwise",
    "matrix_scale", "apply_function", "clip_matrix", "binarize_matrix", "normalize_matrix",
    # 6. Core Linear Algebra
    "transpose", "matrix_multiply", "determinant", "matrix_inverse",
    "matrix_rank", "matrix_trace", "matrix_power", "matrix_norm", "pseudo_inverse",
    # 7. Decompositions
    "lu_decomposition", "qr_decomposition", "cholesky_decomposition",
    "svd", "eigenvalues", "eigenvectors",
    # 8. Solvers & Properties
    "solve_linear_system", "least_squares", "condition_number",
    "is_symmetric", "is_positive_definite", "is_orthogonal",
    "is_square_matrix", "is_diagonal_matrix", "is_matrix_equal",
    # 9. Reshaping & Slicing
    "reshape_matrix", "flatten_matrix", "slice_matrix",
    "hstack", "vstack", "pad_matrix", "kron",
    "flipud", "fliplr", "rotate90", "split_matrix", "repeat_matrix",
    # 10. Geometric / 3-D
    "rotation_matrix_2d", "scaling_matrix_2d", "shear_matrix_2d",
    "reflection_matrix_2d", "translation_matrix_2d",
    "rotation_matrix_3d_x", "rotation_matrix_3d_y", "rotation_matrix_3d_z",
    "scaling_matrix_3d", "translation_matrix_3d",
    "euler_rotation_matrix", "perspective_projection_matrix",
    "orthographic_projection_matrix", "householder_reflection_matrix",
    # 11. Analysis & Statistics
    "matrix_shape", "matrix_size", "matrix_min", "matrix_max",
    "matrix_mean", "matrix_std", "matrix_sum",
    "matrix_density", "matrix_sparsity",
    "matrix_frobenius_norm", "matrix_infinity_norm", "matrix_one_norm",
    # 12. Custom Builders & Pipelines
    "create_matrix_from_rule", "create_distance_matrix",
    "create_adjacency_matrix", "create_weight_matrix",
    "custom_matrix_pipe", "CustomMatrixBuilder",
]
