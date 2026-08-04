"""Trigonometry mathematics functions."""

from .._shared import Any, Callable, List, Optional, Sequence, Tuple, Union, math, np, random


def sin(x: Union[int, float]) -> float:
    """
    Calculate the sine of x (in radians).
    
    Args:
        x: Angle in radians
        
    Returns:
        Sine of x
        
    Examples:
        >>> sin(0)
        0.0
        >>> sin(math.pi / 2)
        1.0
    """
    return math.sin(x)


def cos(x: Union[int, float]) -> float:
    """
    Calculate the cosine of x (in radians).
    
    Args:
        x: Angle in radians
        
    Returns:
        Cosine of x
        
    Examples:
        >>> cos(0)
        1.0
        >>> cos(math.pi)
        -1.0
    """
    return math.cos(x)


def tan(x: Union[int, float]) -> float:
    """
    Calculate the tangent of x (in radians).
    
    Args:
        x: Angle in radians
        
    Returns:
        Tangent of x
        
    Examples:
        >>> tan(0)
        0.0
        >>> tan(math.pi / 4)
        1.0
    """
    return math.tan(x)


def asin(x: Union[int, float]) -> float:
    """
    Calculate the arcsine of x.
    
    Args:
        x: Input value (must be between -1 and 1)
        
    Returns:
        Arcsine of x in radians
        
    Raises:
        ValueError: If x is not in [-1, 1]
        
    Examples:
        >>> asin(0)
        0.0
        >>> asin(1)
        1.5707963267948966
    """
    if not -1 <= x <= 1:
        raise ValueError("asin input must be in range [-1, 1]")
    return math.asin(x)


def acos(x: Union[int, float]) -> float:
    """
    Calculate the arccosine of x.
    
    Args:
        x: Input value (must be between -1 and 1)
        
    Returns:
        Arccosine of x in radians
        
    Raises:
        ValueError: If x is not in [-1, 1]
        
    Examples:
        >>> acos(1)
        0.0
        >>> acos(0)
        1.5707963267948966
    """
    if not -1 <= x <= 1:
        raise ValueError("acos input must be in range [-1, 1]")
    return math.acos(x)


def atan(x: Union[int, float]) -> float:
    """
    Calculate the arctangent of x.
    
    Args:
        x: Input value
        
    Returns:
        Arctangent of x in radians
        
    Examples:
        >>> atan(0)
        0.0
        >>> atan(1)
        0.7853981633974483
    """
    return math.atan(x)


def degrees(x: Union[int, float]) -> float:
    """
    Convert angle from radians to degrees.
    
    Args:
        x: Angle in radians
        
    Returns:
        Angle in degrees
        
    Examples:
        >>> degrees(math.pi)
        180.0
        >>> degrees(math.pi / 2)
        90.0
    """
    return math.degrees(x)


def radians(x: Union[int, float]) -> float:
    """
    Convert angle from degrees to radians.
    
    Args:
        x: Angle in degrees
        
    Returns:
        Angle in radians
        
    Examples:
        >>> radians(180)
        3.141592653589793
        >>> radians(90)
        1.5707963267948966
    """
    return math.radians(x)


__all__ = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'degrees', 'radians']
