"""Probability mathematics functions."""

from .._shared import Any, Callable, List, Optional, Sequence, Tuple, Union, math, np, random


from ..arithmetic.functions import factorial


def normal_pdf(x: Union[int, float], mu: float = 0.0, sigma: float = 1.0) -> float:
    """
    Calculate the probability density function of a normal distribution.
    
    Args:
        x: Input value
        mu: Mean (default=0.0)
        sigma: Standard deviation (default=1.0)
        
    Returns:
        PDF value at x
        
    Examples:
        >>> normal_pdf(0)
        0.3989422804014327
        >>> normal_pdf(1, mu=0, sigma=1)
        0.24197072451914337
    """
    if sigma <= 0:
        raise ValueError("Standard deviation must be positive")
    
    coefficient = 1 / (sigma * math.sqrt(2 * math.pi))
    exponent = -0.5 * ((x - mu) / sigma) ** 2
    return coefficient * math.exp(exponent)


def normal_cdf(x: Union[int, float], mu: float = 0.0, sigma: float = 1.0) -> float:
    """
    Calculate the cumulative distribution function of a normal distribution.
    
    Args:
        x: Input value
        mu: Mean (default=0.0)
        sigma: Standard deviation (default=1.0)
        
    Returns:
        CDF value at x
        
    Examples:
        >>> normal_cdf(0)
        0.5
        >>> normal_cdf(1)
        0.8413447460685429
    """
    if sigma <= 0:
        raise ValueError("Standard deviation must be positive")
    
    # Standardize
    z = (x - mu) / sigma
    
    # Use error function approximation
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def binomial_pmf(k: int, n: int, p: float) -> float:
    """
    Calculate the probability mass function of a binomial distribution.
    
    Args:
        k: Number of successes
        n: Number of trials
        p: Probability of success
        
    Returns:
        PMF value
        
    Examples:
        >>> binomial_pmf(2, 5, 0.3)
        0.3087
    """
    if not 0 <= k <= n:
        return 0.0
    if not 0 <= p <= 1:
        raise ValueError("Probability must be between 0 and 1")
    
    # Binomial coefficient
    binom_coeff = factorial(n) // (factorial(k) * factorial(n - k))
    return binom_coeff * (p ** k) * ((1 - p) ** (n - k))


def poisson_pmf(k: int, lam: float) -> float:
    """
    Calculate the probability mass function of a Poisson distribution.
    
    Args:
        k: Number of events
        lam: Average rate (lambda parameter)
        
    Returns:
        PMF value
        
    Examples:
        >>> poisson_pmf(2, 3.0)
        0.22404180765538775
    """
    if k < 0:
        return 0.0
    if lam <= 0:
        raise ValueError("Lambda must be positive")
    
    return (lam ** k) * math.exp(-lam) / factorial(k)


__all__ = ['normal_pdf', 'normal_cdf', 'binomial_pmf', 'poisson_pmf']
