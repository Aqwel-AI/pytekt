"""Linear Algebra mathematics functions."""

from .._shared import Any, Callable, List, Optional, Sequence, Tuple, Union, math, np, random


def dot_product(a: Sequence[Union[int, float]], b: Sequence[Union[int, float]]) -> float:
    """
    Calculate the dot product (scalar product) of two vectors.
    
    The dot product is the sum of the products of corresponding elements.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Dot product as a scalar value
        
    Raises:
        ValueError: If vectors have different lengths
        
    Examples:
        >>> dot_product([1, 2, 3], [4, 5, 6])
        32  # 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
        >>> dot_product([1, 0], [0, 1])
        0  # Orthogonal vectors
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    return sum(x * y for x, y in zip(a, b))


def transpose(matrix: Sequence[Sequence[Union[int, float]]]) -> List[List[Union[int, float]]]:
    """
    Calculate the transpose of a matrix (flip rows and columns).
    
    Args:
        matrix: 2D matrix as a sequence of sequences
        
    Returns:
        Transposed matrix
        
    Examples:
        >>> transpose([[1, 2], [3, 4], [5, 6]])
        [[1, 3, 5], [2, 4, 6]]
        >>> transpose([[1, 2, 3]])  # Row vector to column vector
        [[1], [2], [3]]
    """
    return [list(row) for row in zip(*matrix)]


def matrix_multiply(a: Sequence[Sequence[Union[int, float]]], 
                    b: Sequence[Sequence[Union[int, float]]]) -> List[List[Union[int, float]]]:
    """
    Multiply two matrices using standard matrix multiplication.
    
    The number of columns in matrix A must equal the number of rows in matrix B.
    
    Args:
        a: First matrix (m × n)
        b: Second matrix (n × p)
        
    Returns:
        Product matrix (m × p)
        
    Raises:
        ValueError: If matrices have incompatible dimensions
        
    Examples:
        >>> matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
        [[19, 22], [43, 50]]
        >>> matrix_multiply([[1, 2, 3]], [[1], [2], [3]])  # Row × Column
        [[14]]
    """
    # Check dimension compatibility
    if len(a[0]) != len(b):
        raise ValueError("Matrix A's columns must equal Matrix B's rows")
    
    # Initialize result matrix with zeros
    result = [[0] * len(b[0]) for _ in range(len(a))]
    
    # Perform matrix multiplication
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                result[i][j] += a[i][k] * b[k][j]
    
    return result


def normalize_vector(v: Sequence[Union[int, float]], norm: str = "l2") -> List[float]:
    """
    Normalize a vector using L1 (Manhattan) or L2 (Euclidean) norm.
    
    Args:
        v: Input vector
        norm: Normalization type ('l1' for Manhattan, 'l2' for Euclidean)
        
    Returns:
        Normalized vector (unit vector in the specified norm)
        
    Raises:
        ValueError: If norm is not 'l1' or 'l2'
        
    Examples:
        >>> normalize_vector([3, 4], norm="l2")
        [0.6, 0.8]  # L2 norm: sqrt(3²+4²) = 5, so [3/5, 4/5]
        >>> normalize_vector([3, 4], norm="l1")
        [0.428..., 0.571...]  # L1 norm: |3|+|4| = 7, so [3/7, 4/7]
    """
    if norm == "l1":
        norm_value = sum(abs(x) for x in v)
    elif norm == "l2":
        norm_value = math.sqrt(sum(x ** 2 for x in v))
    else:
        raise ValueError("Norm must be 'l1' or 'l2'")
    
    if norm_value == 0:
        return list(v)  # Zero vector remains zero
    
    return [x / norm_value for x in v]


def determinant(matrix: Sequence[Sequence[Union[int, float]]]) -> float:
    """
    Calculate the determinant of a square matrix.
    
    Args:
        matrix: Square matrix as a sequence of sequences
        
    Returns:
        Determinant of the matrix
        
    Raises:
        ValueError: If matrix is not square
        
    Examples:
        >>> determinant([[1, 2], [3, 4]])
        -2.0
        >>> determinant([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        1.0
    """
    matrix = [list(row) for row in matrix]
    n = len(matrix)
    
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square")
    
    if n == 1:
        return float(matrix[0][0])
    elif n == 2:
        return float(matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0])
    else:
        # Use NumPy for larger matrices
        return float(np.linalg.det(matrix))


def matrix_inverse(matrix: Sequence[Sequence[Union[int, float]]]) -> List[List[float]]:
    """
    Calculate the inverse of a square matrix.
    
    Args:
        matrix: Square matrix as a sequence of sequences
        
    Returns:
        Inverse matrix
        
    Raises:
        ValueError: If matrix is not square or is singular
        
    Examples:
        >>> matrix_inverse([[1, 2], [3, 4]])
        [[-2.0, 1.0], [1.5, -0.5]]
    """
    matrix = np.array(matrix)
    
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Matrix must be square")
    
    try:
        inv_matrix = np.linalg.inv(matrix)
        return inv_matrix.tolist()
    except np.linalg.LinAlgError:
        raise ValueError("Matrix is singular and cannot be inverted")


def eigenvalues(matrix: Sequence[Sequence[Union[int, float]]]) -> List[complex]:
    """
    Calculate the eigenvalues of a square matrix.
    
    Args:
        matrix: Square matrix as a sequence of sequences
        
    Returns:
        List of eigenvalues (may be complex)
        
    Raises:
        ValueError: If matrix is not square
        
    Examples:
        >>> eigenvalues([[1, 2], [3, 4]])
        [(-0.37228132326901431+0j), (5.3722813232690143+0j)]
    """
    matrix = np.array(matrix)
    
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Matrix must be square")
    
    eigenvals = np.linalg.eigvals(matrix)
    return eigenvals.tolist()


def svd(matrix: Sequence[Sequence[Union[int, float]]]) -> Tuple[List[List[float]], List[float], List[List[float]]]:
    """
    Perform Singular Value Decomposition (SVD) on a matrix.
    
    Args:
        matrix: Input matrix as a sequence of sequences
        
    Returns:
        Tuple of (U, S, V_transpose) where A = U @ S @ V_transpose
        
    Examples:
        >>> U, S, Vt = svd([[1, 2], [3, 4], [5, 6]])
        >>> len(U), len(S), len(Vt)
        (3, 2, 2)
    """
    matrix = np.array(matrix)
    U, S, Vt = np.linalg.svd(matrix)
    return U.tolist(), S.tolist(), Vt.tolist()


def matrix_rank(matrix: Sequence[Sequence[Union[int, float]]]) -> int:
    """
    Calculate the rank of a matrix.
    
    Args:
        matrix: Input matrix as a sequence of sequences
        
    Returns:
        Rank of the matrix
        
    Examples:
        >>> matrix_rank([[1, 2], [3, 4]])
        2
        >>> matrix_rank([[1, 2], [2, 4]])
        1
    """
    matrix = np.array(matrix)
    return int(np.linalg.matrix_rank(matrix))


def cross_product(a: Sequence[Union[int, float]], b: Sequence[Union[int, float]]) -> List[float]:
    """
    Calculate the cross product of two 3D vectors.
    
    Args:
        a: First 3D vector
        b: Second 3D vector
        
    Returns:
        Cross product vector
        
    Raises:
        ValueError: If vectors are not 3D
        
    Examples:
        >>> cross_product([1, 0, 0], [0, 1, 0])
        [0.0, 0.0, 1.0]
        >>> cross_product([1, 2, 3], [4, 5, 6])
        [-3.0, 6.0, -3.0]
    """
    if len(a) != 3 or len(b) != 3:
        raise ValueError("Cross product requires 3D vectors")
    
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ]


def vector_magnitude(v: Sequence[Union[int, float]]) -> float:
    """
    Calculate the magnitude (length) of a vector.
    
    Args:
        v: Input vector
        
    Returns:
        Magnitude of the vector
        
    Examples:
        >>> vector_magnitude([3, 4])
        5.0
        >>> vector_magnitude([1, 1, 1])
        1.7320508075688772
    """
    return math.sqrt(sum(x ** 2 for x in v))


__all__ = ['dot_product', 'transpose', 'matrix_multiply', 'normalize_vector', 'determinant', 'matrix_inverse', 'eigenvalues', 'svd', 'matrix_rank', 'cross_product', 'vector_magnitude']
