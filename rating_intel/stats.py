"""Small, dependency-free statistics helpers (no scipy needed)."""
import math


def wilson(k, n, z=1.96):
    """Wilson score interval for a proportion. Returns (low, high) as fractions; (nan, nan) if n == 0."""
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def two_prop_z(k1, n1, k2, n2):
    """Two-sided pooled two-proportion z-test. Returns (z, p_value). (0.0, 1.0) when undefined."""
    if n1 <= 0 or n2 <= 0:
        return (0.0, 1.0)
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return (0.0, 1.0)
    z = (k1 / n1 - k2 / n2) / se
    return (z, math.erfc(abs(z) / math.sqrt(2)))


def poisson_upper_bound(mean, alpha=0.01):
    """Smallest integer c with P(X <= c) >= 1 - alpha for X ~ Poisson(mean).
    A count strictly greater than c is unusual at level alpha (one-sided)."""
    if mean <= 0:
        return 0
    pmf = math.exp(-mean)
    cdf = pmf
    c = 0
    while cdf < 1 - alpha and c < 100000:
        c += 1
        pmf *= mean / c
        cdf += pmf
    return c


def mde_proportion(p, n_per_group, z_alpha=1.96, z_power=0.8416):
    """Minimum detectable absolute difference between two groups of size n (alpha 5% two-sided, power 80%)."""
    if n_per_group <= 0:
        return float("nan")
    return (z_alpha + z_power) * math.sqrt(2 * p * (1 - p) / n_per_group)


def poisson_sf(k, mean):
    """P(X >= k) for X ~ Poisson(mean). Exact sum; fine for the small means used here."""
    if k <= 0:
        return 1.0
    if mean <= 0:
        return 0.0
    pmf = math.exp(-mean)
    cdf = pmf
    for i in range(1, k):
        pmf *= mean / i
        cdf += pmf
    return max(0.0, 1.0 - cdf)
