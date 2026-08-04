"""Machine Learning mathematics functions."""

from .._shared import Any, List, Sequence, Union, math
from ..linear_algebra import dot_product, vector_magnitude



def sigmoid(x: Union[int, float, List[Union[int, float]]]) -> Union[float, List[float]]:
    """
    Apply sigmoid activation function.
    
    Formula: 1 / (1 + e^(-x))
    
    Args:
        x: Input value(s)
        
    Returns:
        Sigmoid output(s) in range (0, 1)
        
    Examples:
        >>> sigmoid(0)
        0.5
        >>> sigmoid([0, 1, -1])
        [0.5, 0.7310585786300049, 0.2689414213699951]
    """
    def _sigmoid(val):
        return 1 / (1 + math.exp(-val))
    
    if isinstance(x, (list, tuple)):
        return [_sigmoid(val) for val in x]
    else:
        return _sigmoid(x)


def tanh_activation(x: Union[int, float, List[Union[int, float]]]) -> Union[float, List[float]]:
    """
    Apply hyperbolic tangent activation function.
    
    Args:
        x: Input value(s)
        
    Returns:
        Tanh output(s) in range (-1, 1)
        
    Examples:
        >>> tanh_activation(0)
        0.0
        >>> tanh_activation([0, 1, -1])
        [0.0, 0.7615941559557649, -0.7615941559557649]
    """
    def _tanh(val):
        return math.tanh(val)
    
    if isinstance(x, (list, tuple)):
        return [_tanh(val) for val in x]
    else:
        return _tanh(x)


def relu(x: Union[int, float, List[Union[int, float]]]) -> Union[float, List[float]]:
    """
    Apply ReLU (Rectified Linear Unit) activation function.
    
    Formula: max(0, x)
    
    Args:
        x: Input value(s)
        
    Returns:
        ReLU output(s)
        
    Examples:
        >>> relu(-2)
        0
        >>> relu([1, -1, 0, 3])
        [1, 0, 0, 3]
    """
    def _relu(val):
        return max(0, val)
    
    if isinstance(x, (list, tuple)):
        return [_relu(val) for val in x]
    else:
        return _relu(x)


def leaky_relu(x: Union[int, float, List[Union[int, float]]], alpha: float = 0.01) -> Union[float, List[float]]:
    """
    Apply Leaky ReLU activation function.
    
    Formula: max(alpha * x, x)
    
    Args:
        x: Input value(s)
        alpha: Slope for negative values (default=0.01)
        
    Returns:
        Leaky ReLU output(s)
        
    Examples:
        >>> leaky_relu(-2)
        -0.02
        >>> leaky_relu([1, -1, 0, 3])
        [1, -0.01, 0, 3]
    """
    def _leaky_relu(val):
        return max(alpha * val, val)
    
    if isinstance(x, (list, tuple)):
        return [_leaky_relu(val) for val in x]
    else:
        return _leaky_relu(x)


def softmax(x: Sequence[Union[int, float]]) -> List[float]:
    """
    Apply softmax activation function to a vector.
    
    Args:
        x: Input vector
        
    Returns:
        Softmax probabilities (sum to 1)
        
    Examples:
        >>> softmax([1, 2, 3])
        [0.09003057317038046, 0.24472847105479767, 0.6652409557748219]
    """
    # Subtract max for numerical stability
    x_shifted = [val - max(x) for val in x]
    exp_vals = [math.exp(val) for val in x_shifted]
    sum_exp = sum(exp_vals)
    return [val / sum_exp for val in exp_vals]


def mse_loss(y_true: Sequence[Union[int, float]], y_pred: Sequence[Union[int, float]]) -> float:
    """
    Calculate Mean Squared Error loss.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        MSE loss
        
    Raises:
        ValueError: If sequences have different lengths
        
    Examples:
        >>> mse_loss([1, 2, 3], [1.1, 2.1, 2.9])
        0.01
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    return sum((true - pred) ** 2 for true, pred in zip(y_true, y_pred)) / len(y_true)


def mae_loss(y_true: Sequence[Union[int, float]], y_pred: Sequence[Union[int, float]]) -> float:
    """
    Calculate Mean Absolute Error loss.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        MAE loss
        
    Examples:
        >>> mae_loss([1, 2, 3], [1.1, 2.1, 2.9])
        0.1
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    return sum(abs(true - pred) for true, pred in zip(y_true, y_pred)) / len(y_true)


def cross_entropy_loss(y_true: Sequence[Union[int, float]], y_pred: Sequence[Union[int, float]]) -> float:
    """
    Calculate cross-entropy loss for binary classification.
    
    Args:
        y_true: True binary labels (0 or 1)
        y_pred: Predicted probabilities
        
    Returns:
        Cross-entropy loss
        
    Examples:
        >>> cross_entropy_loss([1, 0, 1], [0.9, 0.1, 0.8])
        0.1053605156578263
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    
    epsilon = 1e-15  # Prevent log(0)
    y_pred_clipped = [max(epsilon, min(1 - epsilon, p)) for p in y_pred]
    
    return -sum(true * math.log(pred) + (1 - true) * math.log(1 - pred) 
                for true, pred in zip(y_true, y_pred_clipped)) / len(y_true)


def euclidean_distance(a: Sequence[Union[int, float]], b: Sequence[Union[int, float]]) -> float:
    """
    Calculate Euclidean distance between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Euclidean distance
        
    Raises:
        ValueError: If vectors have different lengths
        
    Examples:
        >>> euclidean_distance([0, 0], [3, 4])
        5.0
        >>> euclidean_distance([1, 2, 3], [4, 5, 6])
        5.196152422706632
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def manhattan_distance(a: Sequence[Union[int, float]], b: Sequence[Union[int, float]]) -> float:
    """
    Calculate Manhattan (L1) distance between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Manhattan distance
        
    Examples:
        >>> manhattan_distance([0, 0], [3, 4])
        7.0
        >>> manhattan_distance([1, 2, 3], [4, 5, 6])
        9.0
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    
    return sum(abs(x - y) for x, y in zip(a, b))


def cosine_similarity(a: Sequence[Union[int, float]], b: Sequence[Union[int, float]]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity (-1 to 1)
        
    Examples:
        >>> cosine_similarity([1, 0], [0, 1])
        0.0
        >>> cosine_similarity([1, 1], [1, 1])
        1.0
    """
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    
    dot_prod = dot_product(a, b)
    norm_a = vector_magnitude(a)
    norm_b = vector_magnitude(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_prod / (norm_a * norm_b)


def hamming_distance(a: Sequence[Any], b: Sequence[Any]) -> int:
    """
    Calculate Hamming distance between two sequences.
    
    Args:
        a: First sequence
        b: Second sequence
        
    Returns:
        Number of positions where elements differ
        
    Examples:
        >>> hamming_distance([1, 0, 1], [1, 1, 0])
        2
        >>> hamming_distance("hello", "hallo")
        1
    """
    if len(a) != len(b):
        raise ValueError("Sequences must have the same length")
    
    return sum(x != y for x, y in zip(a, b))


__all__ = ['sigmoid', 'tanh_activation', 'relu', 'leaky_relu', 'softmax', 'mse_loss', 'mae_loss', 'cross_entropy_loss', 'euclidean_distance', 'manhattan_distance', 'cosine_similarity', 'hamming_distance']
