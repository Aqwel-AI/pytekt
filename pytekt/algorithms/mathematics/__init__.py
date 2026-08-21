"""
Mathematics & Numerical Algorithms Subpackage
=============================================

Provides mathematical, number-theoretic, computational geometry, and statistical algorithms:
- math_number_theory: primes (sieve, Miller-Rabin), GCD/LCM (extended Euclidean), modular arithmetic, Chinese Remainder Theorem
- numerical: root finding (Newton-Raphson, bisection), numerical integration (Simpson, trapezoidal), matrix decompositions
- geometry: convex hull (Graham scan, Jarvis march), line intersection, polygon area (shoelace), closest pair of points
- statistics: descriptive stats, moments, correlation, hypothesis testing helpers, bootstrapping
"""

from __future__ import annotations

from . import geometry, math_number_theory, numerical, statistics

__all__ = [
    "geometry",
    "math_number_theory",
    "numerical",
    "statistics",
]
