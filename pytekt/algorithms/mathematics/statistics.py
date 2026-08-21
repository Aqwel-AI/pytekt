"""Statistical algorithms (stdlib only)."""

from __future__ import annotations

import math
from collections import Counter
from typing import List, Tuple

from pytekt.algorithms.catalog import register_algorithm


@register_algorithm(category="statistics", summary="Arithmetic mean of values.")
def mean(values: List[float]) -> float:
    if not values:
        raise ValueError("empty input")
    return sum(values) / len(values)


@register_algorithm(category="statistics", summary="Median of values.")
def median(values: List[float]) -> float:
    if not values:
        raise ValueError("empty input")
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2:
        return sorted_vals[mid]
    return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2


@register_algorithm(category="statistics", summary="Mode (most frequent value).")
def mode(values: List[float]) -> float:
    if not values:
        raise ValueError("empty input")
    counts = Counter(values)
    return counts.most_common(1)[0][0]


@register_algorithm(category="statistics", summary="Population variance.")
def variance(values: List[float]) -> float:
    if not values:
        raise ValueError("empty input")
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / len(values)


@register_algorithm(category="statistics", summary="Population standard deviation.")
def std_dev(values: List[float]) -> float:
    return math.sqrt(variance(values))


@register_algorithm(category="statistics", summary="Sample variance (Bessel correction).")
def sample_variance(values: List[float]) -> float:
    if len(values) < 2:
        raise ValueError("need at least two values")
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - 1)


@register_algorithm(category="statistics", summary="p-th percentile (0-100).")
def percentile(values: List[float], p: float) -> float:
    if not values:
        raise ValueError("empty input")
    if not 0 <= p <= 100:
        raise ValueError("percentile must be in [0, 100]")
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


@register_algorithm(category="statistics", summary="Quartiles Q1, Q2, Q3.")
def quartiles(values: List[float]) -> Tuple[float, float, float]:
    return (
        percentile(values, 25),
        percentile(values, 50),
        percentile(values, 75),
    )


@register_algorithm(category="statistics", summary="Interquartile range Q3 - Q1.")
def iqr(values: List[float]) -> float:
    q1, _, q3 = quartiles(values)
    return q3 - q1


@register_algorithm(category="statistics", summary="Sample covariance of x and y.")
def covariance(x: List[float], y: List[float]) -> float:
    if len(x) != len(y) or not x:
        raise ValueError("x and y must have same non-zero length")
    mx, my = mean(x), mean(y)
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (len(x) - 1 if len(x) > 1 else 1)


@register_algorithm(category="statistics", summary="Pearson correlation coefficient.")
def pearson_correlation(x: List[float], y: List[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need at least two paired values")
    mx, my = mean(x), mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    den_y = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


@register_algorithm(category="statistics", summary="Spearman rank correlation.")
def spearman_correlation(x: List[float], y: List[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need at least two paired values")

    def ranks(vals: List[float]) -> List[float]:
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(vals):
            j = i
            while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg_rank = (i + j + 2) / 2
            for k in range(i, j + 1):
                r[order[k]] = avg_rank
            i = j + 1
        return r

    return pearson_correlation(ranks(x), ranks(y))


@register_algorithm(category="statistics", summary="Least-squares linear regression slope.")
def linear_regression_slope(x: List[float], y: List[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need at least two paired values")
    mx, my = mean(x), mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = sum((xi - mx) ** 2 for xi in x)
    if den == 0:
        raise ValueError("x has zero variance")
    return num / den


@register_algorithm(category="statistics", summary="Least-squares linear regression intercept.")
def linear_regression_intercept(x: List[float], y: List[float]) -> float:
    return mean(y) - linear_regression_slope(x, y) * mean(x)


@register_algorithm(category="statistics", summary="Coefficient of determination R-squared.")
def r_squared(x: List[float], y: List[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need at least two paired values")
    slope = linear_regression_slope(x, y)
    intercept = mean(y) - slope * mean(x)
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    ss_tot = sum((yi - mean(y)) ** 2 for yi in y)
    if ss_tot == 0:
        return 1.0
    return 1 - ss_res / ss_tot


@register_algorithm(category="statistics", summary="Moving median with window size k.")
def moving_median(values: List[float], k: int) -> List[float]:
    if k <= 0 or len(values) < k:
        return []
    out: List[float] = []
    for i in range(len(values) - k + 1):
        window = sorted(values[i : i + k])
        mid = k // 2
        if k % 2:
            out.append(window[mid])
        else:
            out.append((window[mid - 1] + window[mid]) / 2)
    return out


@register_algorithm(category="statistics", summary="Exponential moving average.")
def ema(values: List[float], alpha: float) -> List[float]:
    if not values:
        return []
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in (0, 1]")
    out = [values[0]]
    for v in values[1:]:
        out.append(alpha * v + (1 - alpha) * out[-1])
    return out


@register_algorithm(category="statistics", summary="Geometric mean of positive values.")
def geometric_mean(values: List[float]) -> float:
    if not values:
        raise ValueError("empty input")
    if any(v <= 0 for v in values):
        raise ValueError("values must be positive")
    log_sum = sum(math.log(v) for v in values)
    return math.exp(log_sum / len(values))


@register_algorithm(category="statistics", summary="Harmonic mean of positive values.")
def harmonic_mean(values: List[float]) -> float:
    if not values:
        raise ValueError("empty input")
    if any(v <= 0 for v in values):
        raise ValueError("values must be positive")
    return len(values) / sum(1 / v for v in values)


@register_algorithm(category="statistics", summary="Sample skewness.")
def skewness(values: List[float]) -> float:
    n = len(values)
    if n < 3:
        raise ValueError("need at least three values")
    m = mean(values)
    s = math.sqrt(sample_variance(values))
    if s == 0:
        return 0.0
    m3 = sum((x - m) ** 3 for x in values) / n
    return m3 / (s ** 3)


@register_algorithm(category="statistics", summary="Excess kurtosis (Fisher).")
def kurtosis(values: List[float]) -> float:
    n = len(values)
    if n < 4:
        raise ValueError("need at least four values")
    m = mean(values)
    s2 = sample_variance(values)
    if s2 == 0:
        return 0.0
    m4 = sum((x - m) ** 4 for x in values) / n
    return m4 / (s2 ** 2) - 3


@register_algorithm(category="statistics", summary="Z-score of value relative to sample.")
def z_score(value: float, values: List[float]) -> float:
    if len(values) < 2:
        raise ValueError("need at least two values")
    m = mean(values)
    s = math.sqrt(sample_variance(values))
    if s == 0:
        return 0.0
    return (value - m) / s


@register_algorithm(category="statistics", summary="Min-max normalization to [0, 1].")
def normalize_min_max(values: List[float]) -> List[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        return [0.0] * len(values)
    span = hi - lo
    return [(v - lo) / span for v in values]


@register_algorithm(category="statistics", summary="Softmax probabilities from logits.")
def softmax(logits: List[float]) -> List[float]:
    if not logits:
        return []
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    total = sum(exps)
    return [e / total for e in exps]


@register_algorithm(category="statistics", summary="Shannon entropy in bits.")
def shannon_entropy(probabilities: List[float]) -> float:
    if not probabilities:
        return 0.0
    total = sum(probabilities)
    if total <= 0:
        raise ValueError("probabilities must sum to positive")
    ent = 0.0
    for p in probabilities:
        q = p / total
        if q > 0:
            ent -= q * math.log2(q)
    return ent
