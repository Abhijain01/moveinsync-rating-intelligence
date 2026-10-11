"""Re-computes the headline counts, shares, p-values, reply rates and listing arithmetic quoted in docs/EXECUTIVE_RECOMMENDATION.md.
Skipped without the snapshot. Not covered: ranking scores (see scripts/prioritize.py), power figures (tests/test_stats.py)."""
import glob
from pathlib import Path

import pandas as pd
import pytest

from rating_intel.classify import classify_frame
from rating_intel.stats import two_prop_z, wilson

FILES = sorted(glob.glob(str(Path(__file__).resolve().parents[1] / "data" / "processed" / "run_20261010T203205Z" / "reviews_clean.csv")))
pytestmark = pytest.mark.skipif(not FILES, reason="snapshot not present")


@pytest.fixture(scope="module")
def data():
    df = pd.read_csv(FILES[0], encoding="utf-8-sig")
    w = df[df["date_ist"] >= "2025-10-10"]
    pool = classify_frame(w[w["score"] <= 3])
    return df, w, pool


def test_corpus_and_window_sizes(data):
    df, w, pool = data
    assert (len(df), len(w), len(pool)) == (24314, 2856, 846)
    assert round(100 * (w["score"] == 1).mean(), 1) == 24.0


def test_lifetime_shortfall_share():
    hist = [7335, 837, 1230, 7294, 98153]  # listing histogram, Phase 1 baseline
    shortfall = sum(c * (5 - (i + 1)) for i, c in enumerate(hist))
    assert round(100 * hist[0] * 4 / shortfall, 1) == 70.5


@pytest.mark.parametrize("cols,n", [
    (["CRASH_LOAD_PERF"], 150), (["LOGIN_SESSION", "ACCESS_OTP"], 105),
    (["TRACKING_LOCATION", "ETA_PICKUP_TIME"], 89),
    (["BOOKING_FAILURE", "BOOKING_RULES", "CANCEL_EDIT", "ADDRESS_LOCATION_MGMT"], 87),
    (["ROUTING_ALLOCATION", "VEHICLE_DRIVER_OPS"], 125), (["SUPPORT_HELPDESK", "DRIVER_CONTACT"], 62),
    (["NO_SHOW"], 21), (["FORCED_RATING", "PERMISSIONS_CONSENT", "FEEDBACK_FLOW_BROKEN"], 46)])
def test_cluster_reach(data, cols, n):
    pool = data[2]
    assert int((pool[cols].sum(axis=1) > 0).sum()) == n


def test_stability_interval_and_actionable_split(data):
    pool = data[2]
    lo, hi = wilson(150, 846)
    assert (round(100 * lo, 1), round(100 * hi, 1)) == (15.3, 20.4)
    assert (int(pool["actionable"].sum()), int(pool["generic_negative_only"].sum())) == (593, 162)


def test_no_aggregate_deterioration(data):
    w = data[1]
    h1, h2 = w[w["date_ist"] < "2026-04-10"], w[w["date_ist"] >= "2026-04-10"]
    assert (round(100 * (h1["score"] == 1).mean(), 1), round(100 * (h2["score"] == 1).mean(), 1)) == (23.1, 24.8)
    _, p = two_prop_z(int((h1["score"] == 1).sum()), len(h1), int((h2["score"] == 1).sum()), len(h2))
    assert round(p, 2) == 0.28


def test_reply_drought(data):
    df, w, pool = data
    assert (int(pool["has_reply"].sum()), len(pool)) == (30, 846)
    last = pool[pool["date_ist"] >= "2026-07-11"]
    assert (int(last["has_reply"].sum()), len(last)) == (2, 224)
    y = df[df["date_ist"].str[:4] == "2023"]
    assert round(100 * y["has_reply"].mean(), 1) == 97.8
    assert round(100 * y[y["score"] <= 3]["has_reply"].mean(), 1) == 96.1


def test_listing_arithmetic_quoted_in_the_recommendation():
    n, mean = 114855, 4.6377                       # listing metadata (docs/baseline.md)
    to_display_47 = (4.65 - mean) * n / (5 - 4.65)
    to_true_47 = (4.70 - mean) * n / (5 - 4.70)
    conversions = (4.65 - mean) * n / 4            # one-star -> five-star adds 4 points each
    assert round(to_display_47, -3) == 4000 and round(to_true_47, -3) == 24000
    assert round(conversions, -1) == 350 and round(100 * conversions / 7335, 1) == 4.8


def test_install_spike_is_the_only_strong_spike(data):
    from rating_intel.trends import detect_theme_spikes, theme_counts_by_month
    from rating_intel.taxonomy import CATEGORIES
    ids = [c["id"] for c in CATEGORIES if c["nature"] != "cross-cutting"]
    pool = data[2]
    s = detect_theme_spikes(theme_counts_by_month(pool, ids), totals=pool.groupby("month_ist").size())
    assert set(s["category"]) == {"INSTALL_ERROR"} and list(s["month_ist"]) == ["2026-07", "2026-08"]
    assert s["strong"].all() and s.attrs["n_tests"] == 230
