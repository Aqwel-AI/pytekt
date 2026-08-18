"""Numerical methods (stdlib only)."""

from __future__ import annotations

import math
import random
from typing import Callable, List, Tuple

from .catalog import register_algorithm


@register_algorithm(category="numerical", summary="Root of f(x)=0 on [a,b] via bisection.")
def bisection_root(f: Callable[[float], float], a: float, b: float, tol: float = 1e-9) -> float:
    if f(a) * f(b) > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")
    while b - a > tol:
        mid = (a + b) / 2
        if f(a) * f(mid) <= 0:
            b = mid
        else:
            a = mid
    return (a + b) / 2


@register_algorithm(category="numerical", summary="Root via Newton-Raphson iteration.")
def newton_raphson_root(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    tol: float = 1e-9,
    max_iter: int = 100,
) -> float:
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        dfx = df(x)
        if dfx == 0:
            raise ValueError("derivative is zero")
        x -= fx / dfx
    return x


@register_algorithm(category="numerical", summary="Root via secant method.")
def secant_root(
    f: Callable[[float], float],
    x0: float,
    x1: float,
    tol: float = 1e-9,
    max_iter: int = 100,
) -> float:
    f0, f1 = f(x0), f(x1)
    for _ in range(max_iter):
        if abs(f1) < tol:
            return x1
        denom = f1 - f0
        if denom == 0:
            raise ValueError("secant denominator zero")
        x2 = x1 - f1 * (x1 - x0) / denom
        x0, f0, x1, f1 = x1, f1, x2, f(x2)
    return x1


@register_algorithm(category="numerical", summary="Definite integral via composite trapezoidal rule.")
def trapezoidal_integration(f: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return total * h


@register_algorithm(category="numerical", summary="Definite integral via composite Simpson's rule.")
def simpson_integration(f: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
    if n <= 0 or n % 2:
        n += 1
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        coeff = 4 if i % 2 else 2
        total += coeff * f(a + i * h)
    return total * h / 3


@register_algorithm(category="numerical", summary="Two-point Gauss-Legendre quadrature on [a,b].")
def gauss_legendre_2pt(f: Callable[[float], float], a: float, b: float) -> float:
    mid = (a + b) / 2
    half = (b - a) / 2
    t1, t2 = -1 / math.sqrt(3), 1 / math.sqrt(3)
    return half * (f(mid + half * t1) + f(mid + half * t2))


@register_algorithm(category="numerical", summary="ODE dy/dx=f(x,y) via explicit Euler method.")
def euler_method(
    f: Callable[[float, float], float],
    x0: float,
    y0: float,
    x_end: float,
    steps: int = 100,
) -> List[Tuple[float, float]]:
    if steps <= 0:
        raise ValueError("steps must be positive")
    h = (x_end - x0) / steps
    out = [(x0, y0)]
    x, y = x0, y0
    for _ in range(steps):
        y += h * f(x, y)
        x += h
        out.append((x, y))
    return out


@register_algorithm(category="numerical", summary="ODE dy/dx=f(x,y) via classical RK4.")
def runge_kutta4(
    f: Callable[[float, float], float],
    x0: float,
    y0: float,
    x_end: float,
    steps: int = 100,
) -> List[Tuple[float, float]]:
    if steps <= 0:
        raise ValueError("steps must be positive")
    h = (x_end - x0) / steps
    out = [(x0, y0)]
    x, y = x0, y0
    for _ in range(steps):
        k1 = f(x, y)
        k2 = f(x + 0.5 * h, y + 0.5 * h * k1)
        k3 = f(x + 0.5 * h, y + 0.5 * h * k2)
        k4 = f(x + h, y + h * k3)
        y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x += h
        out.append((x, y))
    return out


@register_algorithm(category="numerical", summary="First derivative via forward finite difference.")
def forward_difference(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
    return (f(x + h) - f(x)) / h


@register_algorithm(category="numerical", summary="Second derivative via central finite difference.")
def central_second_derivative(f: Callable[[float], float], x: float, h: float = 1e-4) -> float:
    return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h)


@register_algorithm(category="numerical", summary="Evaluate polynomial coefficients at x via Horner's method.")
def horner_evaluate(coeffs: List[float], x: float) -> float:
    result = 0.0
    for c in reversed(coeffs):
        result = result * x + c
    return result


@register_algorithm(category="numerical", summary="Lagrange interpolation at x from points (xs, ys).")
def lagrange_interpolate(xs: List[float], ys: List[float], x: float) -> float:
    n = len(xs)
    total = 0.0
    for i in range(n):
        term = ys[i]
        for j in range(n):
            if i != j:
                term *= (x - xs[j]) / (xs[i] - xs[j])
        total += term
    return total


@register_algorithm(category="numerical", summary="Forward difference table for equally spaced ys.")
def forward_difference_table(ys: List[float]) -> List[List[float]]:
    table = [ys[:]]
    while len(table[-1]) > 1:
        prev = table[-1]
        table.append([prev[i + 1] - prev[i] for i in range(len(prev) - 1)])
    return table


@register_algorithm(category="numerical", summary="Natural cubic spline y-values at query points.")
def natural_cubic_spline(xs: List[float], ys: List[float], queries: List[float]) -> List[float]:
    n = len(xs) - 1
    if n < 1:
        return []
    h = [xs[i + 1] - xs[i] for i in range(n)]
    alpha = [0.0] * (n + 1)
    for i in range(1, n):
        alpha[i] = (3 / h[i]) * (ys[i + 1] - ys[i]) - (3 / h[i - 1]) * (ys[i] - ys[i - 1])
    l = [1.0] + [0.0] * n
    mu = [0.0] * (n + 1)
    z = [0.0] * (n + 1)
    for i in range(1, n):
        l[i] = 2 * (xs[i + 1] - xs[i - 1]) - h[i - 1] * mu[i - 1]
        mu[i] = h[i] / l[i]
        z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i]
    c = [0.0] * (n + 1)
    b = [0.0] * n
    d = [0.0] * n
    for j in range(n - 1, -1, -1):
        c[j] = z[j] - mu[j] * c[j + 1]
        b[j] = (ys[j + 1] - ys[j]) / h[j] - h[j] * (c[j + 1] + 2 * c[j]) / 3
        d[j] = (c[j + 1] - c[j]) / (3 * h[j])
    out: List[float] = []
    for x in queries:
        i = 0
        while i < n - 1 and x > xs[i + 1]:
            i += 1
        dx = x - xs[i]
        out.append(ys[i] + b[i] * dx + c[i] * dx * dx + d[i] * dx * dx * dx)
    return out


@register_algorithm(category="numerical", summary="Matrix-vector multiplication.")
def matrix_vector_multiply(matrix: List[List[float]], vector: List[float]) -> List[float]:
    return [sum(row[j] * vector[j] for j in range(len(vector))) for row in matrix]


@register_algorithm(category="numerical", summary="Solve Ax=b via Gaussian elimination with partial pivoting.")
def gauss_elimination_solve(a: List[List[float]], b: List[float]) -> List[float]:
    n = len(a)
    aug = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        if abs(div) < 1e-12:
            raise ValueError("singular matrix")
        for j in range(col, n + 1):
            aug[col][j] /= div
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            for j in range(col, n + 1):
                aug[row][j] -= factor * aug[col][j]
    return [aug[i][n] for i in range(n)]


@register_algorithm(category="numerical", summary="Solve Ax=b via Jacobi iteration.")
def jacobi_iteration(
    a: List[List[float]],
    b: List[float],
    x0: List[float],
    tol: float = 1e-8,
    max_iter: int = 1000,
) -> List[float]:
    n = len(b)
    x = x0[:]
    for _ in range(max_iter):
        x_new = x[:]
        for i in range(n):
            s = b[i] - sum(a[i][j] * x[j] for j in range(n) if j != i)
            x_new[i] = s / a[i][i]
        if max(abs(x_new[i] - x[i]) for i in range(n)) < tol:
            return x_new
        x = x_new
    return x


@register_algorithm(category="numerical", summary="Dominant eigenvalue estimate via power iteration.")
def power_iteration(matrix: List[List[float]], x0: List[float], max_iter: int = 1000) -> float:
    n = len(x0)
    x = x0[:]
    for _ in range(max_iter):
        y = [sum(matrix[i][j] * x[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(v * v for v in y))
        if norm == 0:
            return 0.0
        x = [v / norm for v in y]
    return sum(matrix[i][j] * x[j] for j in range(n)) * x[0] / x[0] if x[0] else 0.0


@register_algorithm(category="numerical", summary="Minimum of unimodal f on [a,b] via golden-section search.")
def golden_section_minimum(f: Callable[[float], float], a: float, b: float, tol: float = 1e-8) -> float:
    gr = (math.sqrt(5) - 1) / 2
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    while abs(b - a) > tol:
        if f(c) < f(d):
            b = d
        else:
            a = c
        c = b - gr * (b - a)
        d = a + gr * (b - a)
    return (a + b) / 2


@register_algorithm(category="numerical", summary="Minimum of f on [a,b] via Brent's method (simplified).")
def brent_minimum(f: Callable[[float], float], a: float, b: float, tol: float = 1e-8) -> float:
    gr = (math.sqrt(5) - 1) / 2
    c = (3 - math.sqrt(5)) / 2
    x = a + c * (b - a)
    fx = f(x)
    v = w = x
    fv = fw = fx
    for _ in range(200):
        mid = 0.5 * (a + b)
        if abs(x - mid) <= tol:
            break
        e = 0.0
        if abs(fw - fx) > abs(fv - fx):
            if w != x:
                e = w - x
            if v != x:
                e = v - x
        if abs(e) > tol:
            r = (x - w) * (fx - fv)
            q = (x - v) * (fx - fw)
            p = (x - v) * q - (x - w) * r
            q = 2 * (q - r)
            if q > 0:
                p = -p
            q = abs(q)
            r = e
            if abs(p) < abs(0.5 * q * r) and p > q * (a - x) and p < q * (b - x):
                e = p / q
                u = x + e
                if u - a < 2 * tol or b - u < 2 * tol:
                    e = math.copysign(tol, mid - x)
            else:
                e = (x < mid) - (x > mid)
                u = x + c * e * (b - a if e > 0 else a - b)
            fu = f(u)
            if fu <= fx:
                if u >= x:
                    a = x
                else:
                    b = x
                v, w, x = w, x, u
                fv, fw, fx = fw, fx, fu
            else:
                if u < x:
                    a = u
                else:
                    b = u
                if fu <= fw or w == x:
                    v, w = w, u
                    fv, fw = fu, fu
                elif fu <= fv or v == x or v == w:
                    v = u
                    fv = fu
        else:
            e = (x < mid) - (x > mid)
            u = x + c * e * (b - a if e > 0 else a - b)
            fu = f(u)
            if fu <= fx:
                if u >= x:
                    a = x
                else:
                    b = x
                v, w, x = w, x, u
                fv, fw, fx = fw, fx, fu
            else:
                if u < x:
                    a = u
                else:
                    b = u
    return x


@register_algorithm(category="numerical", summary="Integral estimate via Romberg extrapolation.")
def romberg_integration(f: Callable[[float], float], a: float, b: float, max_level: int = 6) -> float:
    r = [[0.0] * (max_level + 1) for _ in range(max_level + 1)]
    r[0][0] = 0.5 * (b - a) * (f(a) + f(b))
    for i in range(1, max_level + 1):
        h = (b - a) / (2 ** i)
        total = 0.0
        for k in range(1, 2 ** (i - 1)):
            total += f(a + (2 * k - 1) * h)
        r[i][0] = 0.5 * r[i - 1][0] + h * total
        for j in range(1, i + 1):
            factor = 4 ** j
            r[i][j] = (factor * r[i][j - 1] - r[i - 1][j - 1]) / (factor - 1)
    return r[max_level][max_level]


@register_algorithm(category="numerical", summary="Monte Carlo integral estimate on [a,b].")
def monte_carlo_integral(f: Callable[[float], float], a: float, b: float, samples: int = 10000) -> float:
    if samples <= 0:
        raise ValueError("samples must be positive")
    total = sum(f(a + (b - a) * random.random()) for _ in range(samples))
    return (b - a) * total / samples


@register_algorithm(category="numerical", summary="Solve x such that f(x)=y via bisection on inverse.")
def bisection_inverse(f: Callable[[float], float], y: float, a: float, b: float, tol: float = 1e-9) -> float:
    def g(x: float) -> float:
        return f(x) - y

    return bisection_root(g, a, b, tol)


@register_algorithm(category="numerical", summary="Natural logarithm via series (x in (0,2)).")
def log_series(x: float, terms: int = 50) -> float:
    if not (0 < x < 2):
        raise ValueError("x must be in (0, 2) for this series")
    z = x - 1
    total = 0.0
    for n in range(1, terms + 1):
        total += ((-1) ** (n + 1)) * (z ** n) / n
    return total


@register_algorithm(category="numerical", summary="Exponential via Taylor series.")
def exp_taylor(x: float, terms: int = 30) -> float:
    total = 1.0
    term = 1.0
    for n in range(1, terms):
        term *= x / n
        total += term
    return total
