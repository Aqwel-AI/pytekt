"""Statistics mathematics functions."""

from .._shared import Any, Callable, List, Optional, Sequence, Tuple, Union, math, np, random


def mean(data: Sequence[Union[int, float]]) -> float:
    """
    Calculate the arithmetic mean (average) of a sequence of numbers.
    
    Args:
        data: Sequence of numbers
        
    Returns:
        Arithmetic mean of the data
        
    Raises:
        ValueError: If data is empty
        
    Examples:
        >>> mean([1, 2, 3, 4, 5])
        3.0
        >>> mean([1.5, 2.5, 3.5])
        2.5
    """
    if not data:
        raise ValueError("Cannot calculate mean of empty sequence")
    return sum(data) / len(data)


def median(data: Sequence[Union[int, float]]) -> float:
    """
    Calculate the median (middle value) of a sequence of numbers.
    
    For even-length sequences, returns the average of the two middle values.
    
    Args:
        data: Sequence of numbers
        
    Returns:
        Median value of the data
        
    Raises:
        ValueError: If data is empty
        
    Examples:
        >>> median([1, 3, 5, 7, 9])
        5.0  # Middle value
        >>> median([1, 2, 3, 4])
        2.5  # Average of 2 and 3
    """
    if not data:
        raise ValueError("Cannot calculate median of empty sequence")
    
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        return float(sorted_data[mid])


def variance(data: Sequence[Union[int, float]], ddof: int = 0) -> float:
    """
    Calculate the variance of a sequence of numbers.
    
    Variance measures how spread out the data points are from the mean.
    
    Args:
        data: Sequence of numbers
        ddof: Delta degrees of freedom (0 for population variance, 1 for sample variance)
        
    Returns:
        Variance of the data
        
    Raises:
        ValueError: If data has fewer than 2 elements when ddof=1
        
    Examples:
        >>> variance([1, 2, 3, 4, 5])
        2.0  # Population variance
        >>> variance([1, 2, 3, 4, 5], ddof=1)
        2.5  # Sample variance (Bessel's correction)
    """
    if len(data) <= ddof:
        raise ValueError(f"Variance requires at least {ddof + 1} data points")
    
    m = mean(data)
    return sum((x - m) ** 2 for x in data) / (len(data) - ddof)


def std_dev(data: Sequence[Union[int, float]], ddof: int = 0) -> float:
    """
    Calculate the standard deviation of a sequence of numbers.
    
    Standard deviation is the square root of variance.
    
    Args:
        data: Sequence of numbers
        ddof: Delta degrees of freedom (0 for population std, 1 for sample std)
        
    Returns:
        Standard deviation of the data
        
    Examples:
        >>> std_dev([1, 2, 3, 4, 5])
        1.4142135623730951
        >>> std_dev([1, 2, 3, 4, 5], ddof=1)
        1.5811388300841898
    """
    return math.sqrt(variance(data, ddof))


def min_max_scale(data: Sequence[Union[int, float]]) -> List[float]:
    """
    Scale data to the range [0, 1] using min-max normalization.
    
    Formula: (x - min) / (max - min)
    
    Args:
        data: Sequence of numbers
        
    Returns:
        List of scaled values in range [0, 1]
        
    Examples:
        >>> min_max_scale([1, 2, 3, 4, 5])
        [0.0, 0.25, 0.5, 0.75, 1.0]
        >>> min_max_scale([10, 10, 10])  # All same values
        [0.0, 0.0, 0.0]
    """
    if not data:
        return []
    
    min_val = min(data)
    max_val = max(data)
    
    if max_val == min_val:
        return [0.0] * len(data)
    
    return [(x - min_val) / (max_val - min_val) for x in data]


def z_score(data: Sequence[Union[int, float]]) -> List[float]:
    """
    Calculate z-scores (standardized values) for a sequence of numbers.
    
    Z-score indicates how many standard deviations a value is from the mean.
    Formula: (x - mean) / std_dev
    
    Args:
        data: Sequence of numbers
        
    Returns:
        List of z-scores
        
    Examples:
        >>> z_score([1, 2, 3, 4, 5])
        [-1.414..., -0.707..., 0.0, 0.707..., 1.414...]
        >>> z_score([5, 5, 5])  # All same values
        [0.0, 0.0, 0.0]
    """
    if not data:
        return []
    
    m = mean(data)
    s = std_dev(data)
    
    if s == 0:
        return [0.0] * len(data)
    
    return [(x - m) / s for x in data]


def correlation(x: Sequence[Union[int, float]], y: Sequence[Union[int, float]]) -> float:
    """
    Calculate Pearson correlation coefficient between two variables.
    
    Args:
        x: First variable
        y: Second variable
        
    Returns:
        Correlation coefficient (-1 to 1)
        
    Examples:
        >>> correlation([1, 2, 3, 4], [2, 4, 6, 8])
        1.0
        >>> correlation([1, 2, 3], [3, 2, 1])
        -1.0
    """
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    n = len(x)
    if n < 2:
        raise ValueError("Need at least 2 data points")
    
    mean_x = mean(x)
    mean_y = mean(y)
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
    sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
    
    denominator = math.sqrt(sum_sq_x * sum_sq_y)
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def linear_regression(x: Sequence[Union[int, float]], y: Sequence[Union[int, float]]) -> Tuple[float, float]:
    """
    Perform simple linear regression and return slope and intercept.
    
    Args:
        x: Independent variable
        y: Dependent variable
        
    Returns:
        Tuple of (slope, intercept)
        
    Examples:
        >>> linear_regression([1, 2, 3, 4], [2, 4, 6, 8])
        (2.0, 0.0)
    """
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    n = len(x)
    if n < 2:
        raise ValueError("Need at least 2 data points")
    
    mean_x = mean(x)
    mean_y = mean(y)
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denominator = sum((xi - mean_x) ** 2 for xi in x)
    
    if denominator == 0:
        slope = 0.0
    else:
        slope = numerator / denominator
    
    intercept = mean_y - slope * mean_x
    
    return slope, intercept


def covariance(x: Sequence[Union[int, float]], y: Sequence[Union[int, float]]) -> float:
    """
    Calculate covariance between two variables.
    
    Args:
        x: First variable
        y: Second variable
        
    Returns:
        Covariance value
        
    Examples:
        >>> covariance([1, 2, 3], [2, 4, 6])
        2.0
    """
    if len(x) != len(y):
        raise ValueError("Variables must have the same length")
    
    n = len(x)
    if n < 2:
        raise ValueError("Need at least 2 data points")
    
    mean_x = mean(x)
    mean_y = mean(y)
    
    return sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / (n - 1)


__all__ = ['mean', 'median', 'variance', 'std_dev', 'min_max_scale', 'z_score', 'correlation', 'linear_regression', 'covariance']
