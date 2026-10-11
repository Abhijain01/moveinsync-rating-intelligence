import pandas as pd

from rating_intel.classify import classify_frame
from rating_intel.trends import (detect_theme_spikes, half_split_table, monthly_summary,
                                 theme_counts_by_month, version_flags)


def test_monthly_summary_values(clean_df):
    m = monthly_summary(clean_df)
    assert len(m) == 10 and (m["reviews"] == 20).all() and (m["one_star"] == 4).all()
    assert (m["one_star_pct"] == 20.0).all()
    assert list(m["month_ist"]) == sorted(m["month_ist"])


def test_theme_counts_fill_missing_months(clean_df):
    pool = classify_frame(clean_df[clean_df["score"] <= 3])
    pool = pool[pool["month_ist"] != "2026-04"]  # drop one month entirely
    counts = theme_counts_by_month(pool, ["ACCESS_OTP"])
    assert "2026-04" in counts.index and counts.loc["2026-04", "ACCESS_OTP"] == 0
    assert counts.loc["2026-03", "ACCESS_OTP"] == 2


def make_counts(series):
    idx = pd.period_range("2026-01", periods=len(series), freq="M").astype(str)
    return pd.DataFrame({"X": series}, index=idx)


def test_flat_series_has_no_spike():
    assert len(detect_theme_spikes(make_counts([2, 3, 2, 3, 2, 3, 2, 3]))) == 0


def test_real_spike_is_flagged_with_context():
    s = detect_theme_spikes(make_counts([2, 3, 2, 3, 2, 3, 2, 14]))
    assert list(s["month_ist"]) == ["2026-08"] and s.iloc[0]["count"] == 14 and s.iloc[0]["expected"] < 3
    assert s.attrs["n_tests"] > 0


def test_volume_alone_does_not_flag_but_a_rate_jump_does():
    counts = make_counts([2, 2, 2, 2, 2, 2, 8])
    totals_same_rate = pd.Series([20, 20, 20, 20, 20, 20, 80], index=counts.index)   # 4x volume, same rate
    assert len(detect_theme_spikes(counts, totals=totals_same_rate)) == 0
    totals_flat = pd.Series([20] * 7, index=counts.index)                             # same volume, 4x rate
    assert len(detect_theme_spikes(counts, totals=totals_flat)) == 1


def test_partial_month_is_scaled_not_flagged():
    counts = make_counts([4, 4, 4, 4, 4, 2])          # last month is half as long
    totals = pd.Series([40, 40, 40, 40, 40, 20], index=counts.index)
    assert len(detect_theme_spikes(counts, totals=totals)) == 0


def test_strong_flag_needs_bonferroni():
    s = detect_theme_spikes(make_counts([1, 1, 1, 1, 1, 1, 30]))
    assert bool(s.iloc[0]["strong"]) and s.iloc[0]["p_value"] < 1e-6


def test_small_counts_never_flag_and_short_history_is_skipped():
    assert len(detect_theme_spikes(make_counts([0, 0, 0, 0, 4]))) == 0  # below min_count
    assert len(detect_theme_spikes(make_counts([1, 1, 20]))) == 0  # fewer than 3 baseline months


def test_half_split_detects_drop():
    rows = [{"date_ist": "2026-01-05", "A": 1} for _ in range(60)] + [{"date_ist": "2026-01-05", "A": 0} for _ in range(140)]
    rows += [{"date_ist": "2026-07-05", "A": 1} for _ in range(10)] + [{"date_ist": "2026-07-05", "A": 0} for _ in range(190)]
    t = half_split_table(pd.DataFrame(rows), ["A"], "2026-04-10").iloc[0]
    assert t["pct_h1"] == 30.0 and t["pct_h2"] == 5.0 and bool(t["passes_bonferroni"])


def test_half_split_handles_empty_half():
    rows = [{"date_ist": "2026-01-05", "A": 1}]
    t = half_split_table(pd.DataFrame(rows), ["A"], "2026-04-10").iloc[0]
    assert t["pool_h2"] == 0 and t["pct_h2"] is None or pd.isna(t["pct_h2"])


def test_version_flags_ignore_small_versions_and_flag_outlier():
    rows = [{"app_version": "9.9", "version_known": True, "score": 1 if i < 60 else 5} for i in range(100)]
    rows += [{"app_version": "1.0", "version_known": True, "score": 1 if i < 80 else 5} for i in range(400)]
    rows += [{"app_version": "tiny", "version_known": True, "score": 1} for _ in range(10)]
    v = version_flags(pd.DataFrame(rows)).set_index("app_version")
    assert "tiny" not in v.index and bool(v.loc["9.9", "flag_higher"]) and not bool(v.loc["1.0", "flag_higher"])
