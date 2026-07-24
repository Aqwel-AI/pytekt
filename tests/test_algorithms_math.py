"""Smoke tests for math algorithms."""

from aion.algorithms import get_algorithm


def test_gcd_lcm():
    assert get_algorithm("gcd")(48, 18) == 6
    assert get_algorithm("lcm")(4, 6) == 12


def test_sieve():
    primes = get_algorithm("sieve_primes")(20)
    assert primes == [2, 3, 5, 7, 11, 13, 17, 19]


def test_mod_pow():
    assert get_algorithm("mod_pow")(2, 10, 1000) == 24
