import math

from rating_intel.stats import mde_proportion, poisson_sf, poisson_upper_bound, two_prop_z, wilson


def test_wilson_known_value():
    lo, hi = wilson(50, 100)
    assert abs(lo - 0.4038) < 1e-3 and abs(hi - 0.5962) < 1e-3


def test_wilson_edges():
    lo, hi = wilson(0, 10)
    assert lo == 0.0 and 0 < hi < 0.35
    assert all(math.isnan(x) for x in wilson(0, 0))


def test_two_prop_z_equal_and_different():
    z, p = two_prop_z(50, 100, 50, 100)
    assert z == 0 and p == 1
    z, p = two_prop_z(30, 100, 50, 100)
    assert z < 0 and p < 0.01
    assert two_prop_z(0, 0, 5, 10) == (0.0, 1.0) and two_prop_z(0, 10, 0, 10) == (0.0, 1.0)


def test_poisson_upper_bound():
    assert poisson_upper_bound(0) == 0
    assert poisson_upper_bound(5, 0.01) == 11  # P(X<=11) ~ 0.9945, P(X<=10) ~ 0.9863
    assert poisson_upper_bound(1, 0.01) == 4


def test_mde_shrinks_with_n():
    assert mde_proportion(0.24, 1000) < mde_proportion(0.24, 250)
    assert abs(mde_proportion(0.24, 238) - 0.110) < 0.003


def test_poisson_sf():
    assert poisson_sf(0, 3) == 1.0 and poisson_sf(5, 0) == 0.0
    assert abs(poisson_sf(1, 1.0) - (1 - math.exp(-1))) < 1e-12
    assert poisson_sf(12, 5) < 0.01 < poisson_sf(8, 5)
