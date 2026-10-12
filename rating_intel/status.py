"""The recurring question: "How are our Play Store ratings?" answered in a few honest lines."""
import json
import math
from pathlib import Path

import pandas as pd

from .classify import classify_frame
from .stats import two_prop_z, wilson
from .taxonomy import CATEGORIES

CROSS = {c["id"] for c in CATEGORIES if c["nature"] == "cross-cutting"}
LABEL = {c["id"]: c["label"] for c in CATEGORIES}


def _period(df, start, end):
    return df[(df["date_ist"] >= start) & (df["date_ist"] <= end)]


def _summ(d):
    n = len(d)
    if n == 0:
        return {"n": 0, "mean": None, "mean_ci": None, "one_pct": None, "one_ci": None, "pos_pct": None}
    mean = float(d["score"].mean())
    sd = float(d["score"].std(ddof=1)) if n > 1 else 0.0
    h = 1.96 * sd / math.sqrt(n) if n > 1 else float("nan")
    lo, hi = wilson(int((d["score"] == 1).sum()), n)
    return {"n": n, "mean": round(mean, 2), "mean_ci": (round(mean - h, 2), round(mean + h, 2)),
            "one_pct": round(100 * (d["score"] == 1).mean(), 1), "one_ci": (round(100 * lo, 1), round(100 * hi, 1)),
            "pos_pct": round(100 * (d["score"] >= 4).mean(), 1)}


def read_listing(manifest_path):
    """Listing metadata captured at collection time (rating, ratings count). None if unavailable."""
    try:
        m = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    lst = m.get("listing_at_start") or {}
    if not lst.get("score"):
        return None
    return {"score": lst.get("score"), "ratings": lst.get("ratings"), "text_reviews": lst.get("reviews"),
            "version": lst.get("version"), "captured": (m.get("started_utc") or "")[:10]}


def headline(df, days=90, manifest_path=None, top_n=3):
    """Compare the latest `days` days of reviews with the `days` before them. Returns a dict with a `lines` list."""
    asof = pd.to_datetime(df["date_ist"].max())
    cur_start = (asof - pd.Timedelta(days=days - 1)).strftime("%Y-%m-%d")
    prev_start = (asof - pd.Timedelta(days=2 * days - 1)).strftime("%Y-%m-%d")
    prev_end = (asof - pd.Timedelta(days=days)).strftime("%Y-%m-%d")
    cur, prev = _period(df, cur_start, asof.strftime("%Y-%m-%d")), _period(df, prev_start, prev_end)
    sc, sp = _summ(cur), _summ(prev)
    z1p = 1.0
    if sc["n"] and sp["n"]:
        _, z1p = two_prop_z(int((cur["score"] == 1).sum()), sc["n"], int((prev["score"] == 1).sum()), sp["n"])
    se = math.sqrt(cur["score"].var(ddof=1) / len(cur) + prev["score"].var(ddof=1) / len(prev)) if len(cur) > 1 and len(prev) > 1 else float("nan")
    dmean = (float(cur["score"].mean()) - float(prev["score"].mean())) if sc["n"] and sp["n"] else None
    mean_p = math.erfc(abs(dmean / se) / math.sqrt(2)) if dmean is not None and se and not math.isnan(se) and se > 0 else 1.0

    pool = classify_frame(cur[cur["score"] <= 3])
    ids = [c["id"] for c in CATEGORIES if c["id"] not in CROSS]
    tops = sorted(((cid, int(pool[cid].sum())) for cid in ids), key=lambda x: -x[1])[:top_n] if len(pool) else []

    L = []
    listing = read_listing(manifest_path) if manifest_path else None
    if listing:
        L.append(f"Play listing when the snapshot was taken ({listing['captured']}): {listing['score']:.1f} stars from {listing['ratings']:,} ratings. "
                 "Google weights recent ratings; this listing score is not a lifetime arithmetic mean and is not directly comparable with the text reviews below.")
    if sc["n"]:
        L.append(f"Last {days} days to {asof.date()}: {sc['n']} text reviews, mean {sc['mean']} stars (95% CI {sc['mean_ci'][0]}-{sc['mean_ci'][1]}), "
                 f"one-star {sc['one_pct']}% (CI {sc['one_ci'][0]}-{sc['one_ci'][1]}), 4-5 star {sc['pos_pct']}%.")
    if sp["n"]:
        L.append(f"Previous {days} days: {sp['n']} reviews, mean {sp['mean']}, one-star {sp['one_pct']}%.")
    if dmean is not None:
        verdict = "no statistically distinguishable change" if (mean_p >= 0.05 and z1p >= 0.05) else "a statistically detectable change"
        L.append(f"Change: mean stars {dmean:+.2f} (p={mean_p:.2f}), one-star share {sc['one_pct'] - sp['one_pct']:+.1f} points (p={z1p:.2f}): {verdict}.")
    if tops:
        L.append("Most frequent complaint themes in the last period (1-3 star reviews, overlapping): " +
                 "; ".join(f"{LABEL[c]} {n}" for c, n in tops if n) + ".")
    if len(pool) and int(pool["SAFETY"].sum()):
        L.append(f"Safety-related mentions in the same period: {int(pool['SAFETY'].sum())} (read these first).")
    L.append("Public text reviews are a self-selected sample; use internal telemetry to judge a release.")
    return {"asof": str(asof.date()), "current": sc, "previous": sp, "mean_change": dmean,
            "mean_p": mean_p, "one_star_p": z1p, "listing": listing, "top_themes": tops, "lines": L}
