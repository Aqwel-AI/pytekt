"""Number theory and modular arithmetic utilities."""

from __future__ import annotations

import random
from typing import List, Tuple

from .catalog import register_algorithm


@register_algorithm(category="math")
def gcd(a: int, b: int) -> int:
    """Greatest common divisor via Euclidean algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


@register_algorithm(category="math")
def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    if a == 0 or b == 0:
        return 0
    return abs(a // gcd(a, b) * b)


@register_algorithm(category="math")
def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Return (g, x, y) such that a*x + b*y = g = gcd(a, b)."""
    if b == 0:
        return abs(a), 1 if a >= 0 else -1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


@register_algorithm(category="math")
def mod_inverse(a: int, m: int) -> int:
    """Multiplicative inverse of a modulo m, or raise ValueError."""
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"No inverse for {a} mod {m}")
    return x % m


@register_algorithm(category="math")
def mod_pow(base: int, exp: int, mod: int) -> int:
    """Modular exponentiation (base^exp % mod)."""
    if mod == 1:
        return 0
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


@register_algorithm(category="math")
def is_prime(n: int) -> bool:
    """Primality test for small integers."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


@register_algorithm(category="math")
def sieve_primes(limit: int) -> List[int]:
    """Sieve of Eratosthenes up to limit (inclusive)."""
    if limit < 2:
        return []
    is_prime_arr = [True] * (limit + 1)
    is_prime_arr[0] = is_prime_arr[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime_arr[i]:
            for j in range(i * i, limit + 1, i):
                is_prime_arr[j] = False
    return [i for i, p in enumerate(is_prime_arr) if p]


@register_algorithm(category="math")
def prime_factors(n: int) -> List[int]:
    """Prime factorization of n (with repetition)."""
    n = abs(n)
    if n <= 1:
        return []
    factors: List[int] = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append(n)
    return factors


@register_algorithm(category="math")
def euler_totient(n: int) -> int:
    """Euler's totient function phi(n)."""
    n = abs(n)
    if n <= 0:
        return 0
    result = n
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


@register_algorithm(category="math")
def chinese_remainder_theorem(
    remainders: List[int], moduli: List[int]
) -> int:
    """Solve x ≡ r_i (mod m_i) for pairwise coprime moduli."""
    if len(remainders) != len(moduli) or not moduli:
        raise ValueError("remainders and moduli must be same non-empty length")
    total = 0
    prod = 1
    for m in moduli:
        prod *= m
    for r, m in zip(remainders, moduli):
        p = prod // m
        total += r * p * mod_inverse(p, m)
    return total % prod


@register_algorithm(category="math")
def factorial_mod(n: int, mod: int) -> int:
    """Compute n! % mod."""
    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    for i in range(2, n + 1):
        result = (result * i) % mod
    return result


@register_algorithm(category="math")
def binomial_coefficient(n: int, k: int) -> int:
    """Binomial coefficient C(n, k)."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


@register_algorithm(category="math")
def fibonacci_nth(n: int) -> int:
    """Nth Fibonacci number (0-indexed: F(0)=0, F(1)=1)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@register_algorithm(category="math")
def is_perfect_square(n: int) -> bool:
    """Return True if n is a perfect square."""
    if n < 0:
        return False
    root = integer_sqrt_floor(n)
    return root * root == n


@register_algorithm(category="math")
def integer_sqrt_floor(n: int) -> int:
    """Floor of square root of n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    lo, hi = 1, n
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid * mid <= n:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi


@register_algorithm(category="math")
def integer_sqrt_ceil(n: int) -> int:
    """Ceiling of square root of n."""
    if n <= 0:
        return 0
    root = integer_sqrt_floor(n)
    return root if root * root == n else root + 1


@register_algorithm(category="math")
def divisors(n: int) -> List[int]:
    """All positive divisors of n in ascending order."""
    n = abs(n)
    if n == 0:
        return []
    small: List[int] = []
    large: List[int] = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            small.append(i)
            if i != n // i:
                large.append(n // i)
        i += 1
    return small + large[::-1]


@register_algorithm(category="math")
def divisor_count(n: int) -> int:
    """Number of positive divisors of n."""
    return len(divisors(n))


@register_algorithm(category="math")
def sum_of_divisors(n: int) -> int:
    """Sum of all positive divisors of n (sigma function)."""
    n = abs(n)
    if n <= 0:
        return 0
    total = 1
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            power_sum = 1
            power = p
            while temp % p == 0:
                power_sum += power
                power *= p
                temp //= p
            total *= power_sum
        p += 1 if p == 2 else 2
    if temp > 1:
        total *= 1 + temp
    return total


@register_algorithm(category="math")
def gcd_list(numbers: List[int]) -> int:
    """GCD of a list of integers."""
    if not numbers:
        return 0
    result = abs(numbers[0])
    for x in numbers[1:]:
        result = gcd(result, x)
    return result


@register_algorithm(category="math")
def lcm_list(numbers: List[int]) -> int:
    """LCM of a list of integers."""
    if not numbers:
        return 1
    result = abs(numbers[0])
    for x in numbers[1:]:
        result = lcm(result, x)
    return result


@register_algorithm(category="math")
def mod_multiply(a: int, b: int, mod: int) -> int:
    """Multiply a*b mod mod without overflow for moderate values."""
    return (a % mod) * (b % mod) % mod


@register_algorithm(category="math")
def miller_rabin(n: int, rounds: int = 8) -> bool:
    """Probabilistic primality test (Miller-Rabin)."""
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = mod_pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = mod_pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


@register_algorithm(category="math")
def is_power_of_two(n: int) -> bool:
    """Return True if n is a positive power of two."""
    return n > 0 and (n & (n - 1)) == 0


@register_algorithm(category="math")
def next_prime(n: int) -> int:
    """Smallest prime strictly greater than n (or n if n<2 and we want first prime)."""
    if n < 2:
        return 2
    candidate = n + 1 if n % 2 == 0 else n + 2
    if n == 2:
        return 3
    while not is_prime(candidate):
        candidate += 2
    return candidate


@register_algorithm(category="math")
def prime_pi(n: int) -> int:
    """Count of primes <= n."""
    return len(sieve_primes(n))


@register_algorithm(category="math")
def carmichael_lambda(n: int) -> int:
    """Carmichael function lambda(n)."""
    n = abs(n)
    if n <= 0:
        return 0
    if n == 1:
        return 1
    factors: dict[int, int] = {}
    temp = n
    for p in prime_factors(temp):
        factors[p] = factors.get(p, 0) + 1
    result = 1
    for p, e in factors.items():
        if p == 2 and e >= 3:
            lam = 2 ** (e - 2)
        else:
            lam = (p - 1) * p ** (e - 1)
        result = lcm(result, lam)
    return result


@register_algorithm(category="math")
def legendre_symbol(a: int, p: int) -> int:
    """Legendre symbol (a/p): -1, 0, or 1."""
    if p < 2 or not is_prime(p):
        raise ValueError("p must be an odd prime")
    a %= p
    if a == 0:
        return 0
    result = mod_pow(a, (p - 1) // 2, p)
    return -1 if result == p - 1 else result


@register_algorithm(category="math")
def solve_linear_congruence(a: int, b: int, m: int) -> List[int]:
    """Solve a*x ≡ b (mod m); return all solutions in [0, m-1]."""
    g, x0, _ = extended_gcd(a, m)
    if b % g != 0:
        return []
    m_prime = m // g
    x0 = (x0 * (b // g)) % m_prime
    return [(x0 + i * m_prime) % m for i in range(g)]


@register_algorithm(category="math")
def nth_root_floor(n: int, k: int) -> int:
    """Floor of the k-th root of n."""
    if n < 0 and k % 2 == 0:
        raise ValueError("even root of negative number")
    if n == 0:
        return 0
    if k <= 0:
        raise ValueError("k must be positive")
    lo, hi = 0, max(1, n)
    while lo <= hi:
        mid = (lo + hi) // 2
        power = mid**k
        if power <= n:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi


@register_algorithm(category="math")
def digit_sum(n: int) -> int:
    """Sum of decimal digits."""
    n = abs(n)
    total = 0
    while n:
        total += n % 10
        n //= 10
    return total


@register_algorithm(category="math")
def digital_root(n: int) -> int:
    """Repeated digit sum until single digit."""
    n = abs(n)
    if n == 0:
        return 0
    return 1 + (n - 1) % 9


@register_algorithm(category="math")
def is_palindrome_number(n: int) -> bool:
    """Return True if n reads the same forwards and backwards."""
    if n < 0:
        return False
    s = str(n)
    return s == s[::-1]


@register_algorithm(category="math")
def reverse_digits(n: int) -> int:
    """Reverse decimal digits (sign preserved)."""
    sign = -1 if n < 0 else 1
    rev = int(str(abs(n))[::-1])
    return sign * rev


@register_algorithm(category="math")
def combinations_count(n: int, k: int) -> int:
    """Number of k-combinations from n elements."""
    return binomial_coefficient(n, k)


@register_algorithm(category="math")
def permutations_count(n: int, k: int) -> int:
    """Number of k-permutations from n elements."""
    if k < 0 or k > n:
        return 0
    result = 1
    for i in range(n, n - k, -1):
        result *= i
    return result


@register_algorithm(category="math")
def catalan_number(n: int) -> int:
    """Nth Catalan number C_n = C(2n,n)/(n+1)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return binomial_coefficient(2 * n, n) // (n + 1)


@register_algorithm(category="math")
def stirling_second(n: int, k: int) -> int:
    """Stirling number of the second kind S(n, k)."""
    if k < 0 or k > n:
        return 0
    if k == 0:
        return 1 if n == 0 else 0
    return k * stirling_second(n - 1, k) + stirling_second(n - 1, k - 1)


@register_algorithm(category="math")
def mobius_mu(n: int) -> int:
    """Möbius function mu(n): 0, 1, or -1."""
    n = abs(n)
    if n == 1:
        return 1
    factors = prime_factors(n)
    if len(factors) != len(set(factors)):
        return 0
    return -1 if len(set(factors)) % 2 else 1


@register_algorithm(category="math")
def sqrt_mod(n: int, p: int) -> int:
    """Modular square root of n mod odd prime p (Tonelli-Shanks)."""
    n %= p
    if n == 0:
        return 0
    if legendre_symbol(n, p) != 1:
        raise ValueError(f"{n} is not a quadratic residue mod {p}")
    if p % 4 == 3:
        return mod_pow(n, (p + 1) // 4, p)
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while legendre_symbol(z, p) != -1:
        z += 1
    m = s
    c = mod_pow(z, q, p)
    t = mod_pow(n, q, p)
    r = mod_pow(n, (q + 1) // 2, p)
    while t != 1:
        i = 1
        temp = mod_pow(t, 2, p)
        while temp != 1:
            temp = mod_pow(temp, 2, p)
            i += 1
        b = mod_pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r
