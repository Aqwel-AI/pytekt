"""Number Theory mathematics functions."""

from .._shared import Any, Callable, List, Optional, Sequence, Tuple, Union, math, np, random


def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Integer to check
        
    Returns:
        True if n is prime, False otherwise
        
    Examples:
        >>> is_prime(7)
        True
        >>> is_prime(12)
        False
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n: Position in Fibonacci sequence (0-indexed)
        
    Returns:
        nth Fibonacci number
        
    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(10)
        55
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def prime_factors(n: int) -> List[int]:
    """
    Find all prime factors of a number.
    
    Args:
        n: Integer to factorize
        
    Returns:
        List of prime factors
        
    Examples:
        >>> prime_factors(12)
        [2, 2, 3]
        >>> prime_factors(17)
        [17]
    """
    if n <= 1:
        return []
    
    factors = []
    d = 2
    
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    
    if n > 1:
        factors.append(n)
    
    return factors


__all__ = ['is_prime', 'fibonacci', 'prime_factors']
