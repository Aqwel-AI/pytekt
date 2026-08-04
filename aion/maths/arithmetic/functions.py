"""Arithmetic mathematics functions."""

from .._shared import Any, List, Optional, Union, math


def addition(a: Union[Union[int, float], List[Union[int, float]], str], 
             b: Union[Union[int, float], List[Union[int, float]], str]) -> Union[Union[int, float], List[Union[int, float]]]:
    """
    Perform addition between two values with support for scalars, lists, and numeric strings.
    
    This function handles multiple input types:
    - Numbers: Direct addition
    - Lists: Element-wise addition with padding
    - Strings: Comma-separated numeric strings converted to lists
    - Mixed types: Scalar-vector operations
    
    Args:
        a: First operand (number, list of numbers, or comma-separated numeric string)
        b: Second operand (number, list of numbers, or comma-separated numeric string)
    
    Returns:
        Result of addition operation
        
    Raises:
        ValueError: If string cannot be converted to numbers
        TypeError: If inputs are of unsupported types
        
    Examples:
        >>> addition(5, 10)
        15
        >>> addition("1,2,3", "4,5,6")
        [5.0, 7.0, 9.0]
        >>> addition([1, 2, 3], 5)
        [6, 7, 8]
        >>> addition(5, [10, 20])
        [15, 25]
        >>> addition([1, 2], [3, 4, 5])  # Shorter list padded with zeros
        [4, 6, 5]
    """
    def _str_to_list(s: str) -> List[float]:
        """Convert comma-separated string to list of numbers."""
        try:
            return [float(x.strip()) for x in s.split(',')]
        except ValueError:
            raise ValueError(f"Cannot convert '{s}' to list of numbers")
    
    def _is_number(x: Any) -> bool:
        """Check if value is a number."""
        return isinstance(x, (int, float))
    
    # Convert strings to lists
    if isinstance(a, str):
        a = _str_to_list(a)
    if isinstance(b, str):
        b = _str_to_list(b)
    
    # Number + Number
    if _is_number(a) and _is_number(b):
        return a + b
    
    # Number + List or List + Number (scalar-vector operations)
    if _is_number(a) and isinstance(b, (list, tuple)):
        return [a + x for x in b]
    if _is_number(b) and isinstance(a, (list, tuple)):
        return [b + x for x in a]
    
    # List + List (element-wise with padding)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        max_len = max(len(a), len(b))
        # Pad shorter list with zeros
        a_pad = list(a) + [0] * (max_len - len(a))
        b_pad = list(b) + [0] * (max_len - len(b))
        return [x + y for x, y in zip(a_pad, b_pad)]
    
    # Invalid input types
    raise TypeError("Inputs must be numbers, lists/tuples of numbers, or numeric strings")


def subtraction(a: Union[Union[int, float], List[Union[int, float]], str], 
                b: Union[Union[int, float], List[Union[int, float]], str]) -> Union[Union[int, float], List[Union[int, float]]]:
    """
    Perform subtraction between two values with support for scalars, lists, and numeric strings.
    
    Args:
        a: First operand (minuend)
        b: Second operand (subtrahend)
    
    Returns:
        Result of subtraction operation (a - b)
        
    Examples:
        >>> subtraction(10, 4)
        6
        >>> subtraction("10,20,30", "1,2,3")
        [9.0, 18.0, 27.0]
        >>> subtraction([5, 10], 3)
        [2, 7]
        >>> subtraction(3, [1, 2, 3])
        [2, 1, 0]
        >>> subtraction([5, 6], [2, 3, 4])
        [3, 3, -4]
    """
    def _str_to_list(s: str) -> List[float]:
        """Convert comma-separated string to list of numbers."""
        try:
            return [float(x.strip()) for x in s.split(',')]
        except ValueError:
            raise ValueError(f"Cannot convert '{s}' to list of numbers")
    
    def _is_number(x: Any) -> bool:
        """Check if value is a number."""
        return isinstance(x, (int, float))
    
    # Convert strings to lists
    if isinstance(a, str):
        a = _str_to_list(a)
    if isinstance(b, str):
        b = _str_to_list(b)
    
    # Number - Number
    if _is_number(a) and _is_number(b):
        return a - b
    
    # Number - List or List - Number
    if _is_number(a) and isinstance(b, (list, tuple)):
        return [a - x for x in b]
    if _is_number(b) and isinstance(a, (list, tuple)):
        return [x - b for x in a]
    
    # List - List (element-wise)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        max_len = max(len(a), len(b))
        a_pad = list(a) + [0] * (max_len - len(a))
        b_pad = list(b) + [0] * (max_len - len(b))
        return [x - y for x, y in zip(a_pad, b_pad)]
    
    # Invalid input
    raise TypeError("Inputs must be numbers, lists/tuples of numbers, or numeric strings")


def multiplication(a: Union[Union[int, float], List[Union[int, float]], str], 
                  b: Union[Union[int, float], List[Union[int, float]], str]) -> Union[Union[int, float], List[Union[int, float]]]:
    """
    Perform multiplication between two values with support for scalars, lists, and numeric strings.
    
    Args:
        a: First operand (multiplicand)
        b: Second operand (multiplier)
    
    Returns:
        Result of multiplication operation
        
    Examples:
        >>> multiplication(5, 10)
        50
        >>> multiplication("1,2,3", "4,5,6")
        [4.0, 10.0, 18.0]
        >>> multiplication([1, 2, 3], 5)
        [5, 10, 15]
        >>> multiplication(5, [10, 20])
        [50, 100]
        >>> multiplication([1, 2], [3, 4, 5])
        [3, 8, 0]
    """
    def _str_to_list(s: str) -> List[float]:
        """Convert comma-separated string to list of numbers."""
        try:
            return [float(x.strip()) for x in s.split(',')]
        except ValueError:
            raise ValueError(f"Cannot convert '{s}' to list of numbers")
    
    def _is_number(x: Any) -> bool:
        """Check if value is a number."""
        return isinstance(x, (int, float))
    
    # Convert string inputs to lists
    if isinstance(a, str):
        a = _str_to_list(a)
    if isinstance(b, str):
        b = _str_to_list(b)
    
    # Number * Number
    if _is_number(a) and _is_number(b):
        return a * b
    
    # Number * List or List * Number (scalar multiplication)
    if _is_number(a) and isinstance(b, (list, tuple)):
        return [a * x for x in b]
    if _is_number(b) and isinstance(a, (list, tuple)):
        return [b * x for x in a]
    
    # List * List (element-wise multiplication)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        max_len = max(len(a), len(b))
        a_pad = list(a) + [0] * (max_len - len(a))
        b_pad = list(b) + [0] * (max_len - len(b))
        return [x * y for x, y in zip(a_pad, b_pad)]
    
    # Invalid input
    raise TypeError("Inputs must be numbers, lists/tuples of numbers, or numeric strings")


def division(a: Union[Union[int, float], List[Union[int, float]], str], 
             b: Union[Union[int, float], List[Union[int, float]], str]) -> Union[Optional[float], List[Optional[float]]]:
    """
    Perform division between two values with support for scalars, lists, and numeric strings.
    Handles division by zero gracefully by returning None.
    
    Args:
        a: First operand (dividend)
        b: Second operand (divisor)
    
    Returns:
        Result of division operation (None for division by zero)
        
    Examples:
        >>> division(10, 2)
        5.0
        >>> division(10, 0)
        None
        >>> division([10, 20], 2)
        [5.0, 10.0]
        >>> division(10, [2, 0, 5])
        [5.0, None, 2.0]
        >>> division([10, 20], [2, 0])
        [5.0, None]
        >>> division("10,20", "2,5")
        [5.0, 4.0]
    """
    def _str_to_list(s: str) -> List[float]:
        """Convert comma-separated string to list of numbers."""
        try:
            return [float(x.strip()) for x in s.split(',')]
        except ValueError:
            raise ValueError(f"Cannot convert '{s}' to list of numbers")
    
    def _is_number(x: Any) -> bool:
        """Check if value is a number."""
        return isinstance(x, (int, float))
    
    def _safe_div(x: float, y: float) -> Optional[float]:
        """Safe division that returns None for division by zero."""
        return x / y if y != 0 else None
    
    # Convert strings to lists if needed
    if isinstance(a, str):
        a = _str_to_list(a)
    if isinstance(b, str):
        b = _str_to_list(b)
    
    # Number ÷ Number
    if _is_number(a) and _is_number(b):
        return _safe_div(a, b)
    
    # Number ÷ List
    if _is_number(a) and isinstance(b, (list, tuple)):
        return [_safe_div(a, x) for x in b]
    
    # List ÷ Number
    if _is_number(b) and isinstance(a, (list, tuple)):
        return [_safe_div(x, b) for x in a]
    
    # List ÷ List (element-wise, pad with zeros if lengths differ)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        max_len = max(len(a), len(b))
        a_pad = list(a) + [0] * (max_len - len(a))
        b_pad = list(b) + [0] * (max_len - len(b))
        return [_safe_div(x, y) for x, y in zip(a_pad, b_pad)]
    
    # Invalid input
    raise TypeError("Inputs must be numbers, lists/tuples, or numeric strings")


def power(base: Union[int, float], exponent: Union[int, float]) -> float:
    """
    Calculate base raised to the power of exponent.
    
    Args:
        base: Base number
        exponent: Exponent number
        
    Returns:
        Result of base^exponent
        
    Examples:
        >>> power(2, 3)
        8.0
        >>> power(9, 0.5)
        3.0
    """
    return float(base ** exponent)


def sqrt(x: Union[int, float]) -> float:
    """
    Calculate the square root of a number.
    
    Args:
        x: Input number (must be non-negative)
        
    Returns:
        Square root of x
        
    Raises:
        ValueError: If x is negative
        
    Examples:
        >>> sqrt(16)
        4.0
        >>> sqrt(2)
        1.4142135623730951
    """
    if x < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(x)


def log(x: Union[int, float], base: Union[int, float] = math.e) -> float:
    """
    Calculate the logarithm of x to the given base.
    
    Args:
        x: Input number (must be positive)
        base: Base of logarithm (default is e for natural log)
        
    Returns:
        Logarithm of x to the given base
        
    Raises:
        ValueError: If x <= 0 or base <= 0 or base == 1
        
    Examples:
        >>> log(10, 10)
        1.0
        >>> log(math.e)
        1.0
    """
    if x <= 0:
        raise ValueError("Logarithm input must be positive")
    if base <= 0 or base == 1:
        raise ValueError("Logarithm base must be positive and not equal to 1")
    
    if base == math.e:
        return math.log(x)
    else:
        return math.log(x) / math.log(base)


def log10(x: Union[int, float]) -> float:
    """
    Calculate the base-10 logarithm of x.
    
    Args:
        x: Input number (must be positive)
        
    Returns:
        Base-10 logarithm of x
        
    Examples:
        >>> log10(100)
        2.0
        >>> log10(1000)
        3.0
    """
    return log(x, 10)


def exp(x: Union[int, float]) -> float:
    """
    Calculate e raised to the power of x.
    
    Args:
        x: Exponent
        
    Returns:
        e^x
        
    Examples:
        >>> exp(0)
        1.0
        >>> exp(1)
        2.718281828459045
    """
    return math.exp(x)


def abs_value(x: Union[int, float]) -> Union[int, float]:
    """
    Calculate the absolute value of a number.
    
    Args:
        x: Input number
        
    Returns:
        Absolute value of x
        
    Examples:
        >>> abs_value(-5)
        5
        >>> abs_value(3.14)
        3.14
    """
    return abs(x)


def factorial(n: int) -> int:
    """
    Calculate the factorial of a non-negative integer.
    
    Args:
        n: Non-negative integer
        
    Returns:
        n! (factorial of n)
        
    Raises:
        ValueError: If n is negative
        
    Examples:
        >>> factorial(5)
        120
        >>> factorial(0)
        1
    """
    if n < 0:
        raise ValueError("Factorial is only defined for non-negative integers")
    return math.factorial(n)


def gcd(a: int, b: int) -> int:
    """
    Calculate the greatest common divisor of two integers.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Greatest common divisor of a and b
        
    Examples:
        >>> gcd(48, 18)
        6
        >>> gcd(17, 13)
        1
    """
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """
    Calculate the least common multiple of two integers.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Least common multiple of a and b
        
    Examples:
        >>> lcm(12, 18)
        36
        >>> lcm(7, 5)
        35
    """
    return abs(a * b) // gcd(a, b) if a != 0 and b != 0 else 0


__all__ = ['addition', 'subtraction', 'multiplication', 'division', 'power', 'sqrt', 'log', 'log10', 'exp', 'abs_value', 'factorial', 'gcd', 'lcm']
