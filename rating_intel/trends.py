"""Trend, spike and version analysis on classified reviews."""
import pandas as pd

from .stats import poisson_sf, poisson_upper_bound, two_prop_z, wilson


def monthly_summary(df):
    """Per month (IST): reviews, one-star count and share, mean stars, reply rate."""
    if df.empty:
        return pd.DataFrame(columns=["month_ist", "reviews", "one_star", "one_star_pct", "mean_stars", "reply_rate_pct"])
    g = df.groupby("month_ist").agg(
        reviews=("score", "size"),
        one_star=("score", lambda s: int((s == 1).sum())),
        mean_stars=("score", "mean"),
        reply_rate=("has_reply", "mean"),
    ).reset_index()
    g["one_star_pct"] = (100 * g["one_star"] / g["reviews"]).round(1)
    g["mean_stars"] = g["mean_stars"].round(3)
    g["reply_rate_pct"] = (100 * g["reply_rate"]).round(1)
    return g.drop(columns="reply_rate").sort_values("month_ist").reset_index(drop=True)


def theme_counts_by_month(pool, ids):
    """Rows = every calendar month between first and last review, columns = category ids, values = counts."""
    if pool.empty:
        return pd.DataFrame(columns=ids)
    months = pd.period_range(pool["month_ist"].min(), pool["month_ist"].max(), freq="M").astype(str)
    counts = pool.groupby("month_ist")[ids].sum().reindex(months, fill_value=0)
    counts.index.name = "month_ist"
    return counts.astype(int)


def detect_theme_spikes(counts, totals=None, baseline_months=6, min_baseline_months=3, alpha=0.01, min_count=5):
    """Flag (category, month) where the count exceeds what the trailing rate predicts.

    `counts`: months x categories. `totals`: complaint-pool size per month (same index); if omitted every
    month counts as 1, i.e. plain counts. Expected count = trailing rate (sum of prior counts / sum of prior
    totals, up to `baseline_months` months) x this month's total, so a month with more reviews in all
    categories is not flagged merely for volume, and a partial month is scaled correctly.
    A flag needs count >= min_count and P(X >= count) < alpha under Poisson(expected). `strong` marks flags
    that also survive a Bonferroni correction over every month-category pair tested.
    Flags are prompts to read the reviews, not proof of an incident.
    """
    cols = ["month_ist", "category", "count", "expected", "upper_bound", "p_value", "strong"]
    tot = pd.Series(1.0, index=counts.index) if totals is None else totals.reindex(counts.index).fillna(0).astype(float)
    rows, n_tests = [], 0
    months = list(counts.index)
    for i, m in enumerate(months):
        lo = max(0, i - baseline_months)
        if i - lo < min_baseline_months:
            continue
        prior_tot = float(tot.iloc[lo:i].sum())
        if prior_tot <= 0:
            continue
        for cat in counts.columns:
            n_tests += 1
            rate = float(counts.iloc[lo:i][cat].sum()) / prior_tot
            expected = rate * float(tot.iloc[i])
            c = int(counts.iloc[i][cat])
            if c >= min_count and c > poisson_upper_bound(expected, alpha):
                pv = poisson_sf(c, expected)
                rows.append({"month_ist": m, "category": cat, "count": c, "expected": round(expected, 2),
                             "upper_bound": poisson_upper_bound(expected, alpha), "p_value": pv, "strong": False})
    out = pd.DataFrame(rows, columns=cols)
    if len(out):
        out["strong"] = out["p_value"] < 0.05 / max(1, n_tests)
        out["p_value"] = out["p_value"].map(lambda x: float(f"{x:.2e}"))
    out.attrs["n_tests"] = n_tests
    out.attrs["alpha"] = alpha
    return out


def half_split_table(pool, ids, split_date, bonferroni_over=None):
    """Compare each category's share of the pool before vs from `split_date` (ISO string)."""
    h1 = pool[pool["date_ist"] < split_date]
    h2 = pool[pool["date_ist"] >= split_date]
    m = bonferroni_over or max(1, len(ids))
    rows = []
    for cid in ids:
        k1, k2 = int(h1[cid].sum()), int(h2[cid].sum())
        z, p = two_prop_z(k1, len(h1), k2, len(h2))
        rows.append({"category": cid, "n_h1": k1, "pool_h1": len(h1), "n_h2": k2, "pool_h2": len(h2),
                     "pct_h1": round(100 * k1 / len(h1), 1) if len(h1) else None,
                     "pct_h2": round(100 * k2 / len(h2), 1) if len(h2) else None,
                     "z": round(z, 2), "p_value": round(p, 5), "passes_bonferroni": p < 0.05 / m})
    return pd.DataFrame(rows)


def version_flags(df, min_reviews=50, alpha=0.05):
    """One-star share per app version versus all other reviews in the window, Bonferroni over tested versions.

    A flag means 'look closer'. With many versions some will deviate by chance; the correction handles that
    only in part because versions are not independent samples of one population.
    """
    d = df[df["version_known"].astype(bool)]
    counts = d["app_version"].value_counts()
    tested = [v for v, c in counts.items() if c >= min_reviews]
    rows = []
    for v in tested:
        a = d[d["app_version"] == v]
        b = d[d["app_version"] != v]
        k1, n1 = int((a["score"] == 1).sum()), len(a)
        k2, n2 = int((b["score"] == 1).sum()), len(b)
        z, p = two_prop_z(k1, n1, k2, n2)
        lo, hi = wilson(k1, n1)
        rows.append({"app_version": v, "reviews": n1, "one_star": k1, "one_star_pct": round(100 * k1 / n1, 1),
                     "ci_low": round(100 * lo, 1), "ci_high": round(100 * hi, 1),
                     "rest_one_star_pct": round(100 * k2 / n2, 1) if n2 else None,
                     "p_value": round(p, 5),
                     "flag_higher": bool(z > 0 and p < alpha / max(1, len(tested)))})
    return pd.DataFrame(rows, columns=["app_version", "reviews", "one_star", "one_star_pct", "ci_low", "ci_high",
                                       "rest_one_star_pct", "p_value", "flag_higher"])
