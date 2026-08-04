"""Utilities mathematics functions."""

from .._shared import Any, Callable, List, Optional, Sequence, Tuple, Union, math, np, random


def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Input value
        min_val: Minimum bound
        max_val: Maximum bound
        
    Returns:
        Clamped value
        
    Examples:
        >>> clamp(5, 0, 10)
        5
        >>> clamp(-1, 0, 10)
        0
        >>> clamp(15, 0, 10)
        10
    """
    return max(min_val, min(value, max_val))


def lerp(a: Union[int, float], b: Union[int, float], t: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        a: Start value
        b: End value
        t: Interpolation parameter (0.0 to 1.0)
        
    Returns:
        Interpolated value
        
    Examples:
        >>> lerp(0, 10, 0.5)
        5.0
        >>> lerp(10, 20, 0.2)
        12.0
    """
    return a + t * (b - a)


__all__ = ['clamp', 'lerp']
