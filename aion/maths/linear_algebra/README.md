# aion.maths.linear_algebra

A comprehensive, lightweight linear algebra package for `aion`.

## Overview

The `aion.maths.linear_algebra` module is structured into two main sub-modules:
- **`matrix.py`**: Covers 2D matrix operations, including standard generators, decompositions (LU, QR, Cholesky, SVD, Eigenvalues), triangular/diagonal operations, solvers, shape manipulation, statistics, and projection.
- **`vectors.py`**: Covers 1D vector mathematics, including dot/cross products, magnitude, normalization, vector addition/subtraction/scaling, and angles.

All functions return standard Python lists for maximum interoperability. NumPy and SciPy are leveraged internally only when performance or numerical precision demands it.

## Quick Usage

### Vector Operations
```python
from aion.maths.linear_algebra import dot_product, vector_magnitude, normalize_vector

a = [1, 2, 3]
b = [4, 5, 6]

# Compute scalar dot product
dp = dot_product(a, b)  # 32.0

# Compute L2 magnitude
mag = vector_magnitude(a)  # ~3.74

# Normalize a vector
unit_a = normalize_vector(a)  # [0.267, 0.534, 0.801]
```

### Matrix Operations
```python
from aion.maths.linear_algebra import matrix_multiply, identity, solve_linear_system

# Multiply two matrices
A = [[1, 2], [3, 4]]
B = [[2, 0], [1, 2]]
C = matrix_multiply(A, B)  # [[4, 4], [10, 8]]

# Solve a linear system Ax = b
b = [5, 11]
x = solve_linear_system(A, b)  # [1.0, 2.0]
```

## Features

- **Standard Generators**: `zeros`, `ones`, `eye`, `identity`, `full`, `arange_matrix`, `linspace_matrix`
- **Diagonal & Triangular**: `diag`, `extract_diag`, `triu`, `tril`, `block_diag`
- **Random Matrices**: `random_uniform`, `random_normal`, `random_sparse`
- **Vector Math**: `dot_product`, `cross_product`, `vector_magnitude`, `normalize_vector`, `vector_add`, `vector_subtract`, `vector_scale`, `angle_between_vectors`
- **Matrix Decompositions**: `lu_decomposition`, `qr_decomposition`, `cholesky_decomposition`, `svd`, `eigenvalues`, `eigenvectors`
- **Solvers**: `solve_linear_system`, `least_squares`
- **Geometric Transformations**: `rotation_matrix_2d`, `rotation_matrix_3d_x`, `perspective_projection_matrix`
