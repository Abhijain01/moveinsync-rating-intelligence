"""Phase 3 theme analysis: counts, shares, star mix, halves comparison, app-vs-operations split.

Usage:  python scripts\\analyze_themes.py data\\processed\\run_<stamp>\\reviews_clean.csv --since 2025-10-10
Output (next to the CSV): themes_<since>.csv, themes_<since>.md, evidence_<since>.csv

Denominators (always stated):
  POOL     = reviews in the window rated 1-3 stars (the complaint pool).
  NEG      = reviews in the window rated 1-2 stars.
Category counts are multi-label and overlap; they are never summed into a total.
"Share" columns use Wilson 95% intervals. Counts are *detected* counts from a rule-based classifier whose
held-out recall is below 1 (see docs/phase3_findings.md), so they are best read as lower bounds.
"""
import argparse
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classify  # noqa: E402
from taxonomy import CATEGORIES  # noqa: E402

CROSS = {c["id"] for c in CATEGORIES if c["nature"] == "cross-cutting"}
APP_NATURES = {"technical", "usability", "policy"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def fmt_ci(k, n):
    lo, hi = wilson(k, n)
    return f"{100 * k / n:.1f}% ({100 * lo:.1f}-{100 * hi:.1f})" if n else "n/a"


def theme_table(c, since, split_date):
    ids = [x["id"] for x in CATEGORIES]
    meta = {x["id"]: x for x in CATEGORIES}
    pool = c
    neg = c[c["score"] <= 2]
    h1 = c[c["date_ist"] < split_date]
    h2 = c[c["date_ist"] >= split_date]
    rows = []
    for cid in ids:
        sub = pool[pool[cid] == 1]
        n = len(sub)
        one = int((sub["score"] == 1).sum())
        rows.append({
            "id": cid, "label": meta[cid]["label"], "family": meta[cid]["family"], "nature": meta[cid]["nature"],
            "n_pool": n, "share_pool": fmt_ci(n, len(pool)),
            "n_neg": int((neg[cid] == 1).sum()), "share_neg": fmt_ci(int((neg[cid] == 1).sum()), len(neg)),
            "n_1star": one, "pct_of_theme_that_is_1star": f"{100 * one / n:.0f}%" if n else "n/a",
            "n_h1": int((h1[cid] == 1).sum()), "pool_h1": len(h1),
            "n_h2": int((h2[cid] == 1).sum()), "pool_h2": len(h2),
            "pct_h1": round(100 * (h1[cid] == 1).mean(), 1) if len(h1) else None,
            "pct_h2": round(100 * (h2[cid] == 1).mean(), 1) if len(h2) else None,
            "example_review_ids": ";".join(sub.sort_values("word_count", ascending=False)["review_id"].head(3)),
        })
    t = pd.DataFrame(rows).sort_values("n_pool", ascending=False).reset_index(drop=True)
    return t


def split_summary(c):
    """App-controlled vs operations-controlled, using each review's labels. Mutually exclusive buckets."""
    nature = {x["id"]: x["nature"] for x in CATEGORIES}
    ids = [x["id"] for x in CATEGORIES if x["id"] not in CROSS]

    def bucket(row):
        ns = {nature[i] for i in ids if row[i] == 1}
        if not ns:
            return "no actionable category"
        has_app = bool(ns & APP_NATURES)
        has_ops = "operational" in ns
        has_mixed = "mixed" in ns
        if has_app and has_ops:
            return "app + operations"
        if has_app:
            return "app-side only (technical/usability/policy)"
        if has_ops:
            return "operations only"
        return "mixed-nature only"
    return c.apply(bucket, axis=1).value_counts()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--since", default="2025-10-10")
    p.add_argument("--split-date", default="2026-04-10", help="date separating halves H1 (before) and H2 (from)")
    args = p.parse_args(argv)

    raw = pd.read_csv(args.csv, encoding="utf-8-sig")
    win = raw[raw["date_ist"] >= args.since]
    pool = classify.classify_frame(win[win["score"] <= 3])
    praise = classify.praise_frame(win[win["score"] >= 4])

    t = theme_table(pool, args.since, args.split_date)
    out_dir = Path(args.csv).parent
    t.to_csv(out_dir / f"themes_{args.since}.csv", index=False, encoding="utf-8-sig")

    # evidence table: 3 traceable examples per category (longest texts, lowest stars first)
    ev = []
    for cid in [x["id"] for x in CATEGORIES]:
        sub = pool[pool[cid] == 1].sort_values(["score", "word_count"], ascending=[True, False]).head(3)
        for _, r in sub.iterrows():
            ev.append({"category": cid, "review_id": r["review_id"], "date_ist": r["date_ist"], "stars": r["score"],
                       "app_version": r["app_version"], "evidence_match": r[f"evidence_{cid}"], "text": r["text_norm"][:400]})
    pd.DataFrame(ev).to_csv(out_dir / f"evidence_{args.since}.csv", index=False, encoding="utf-8-sig")

    n_pool, n_neg = len(pool), int((pool["score"] <= 2).sum())
    L = [f"# Theme analysis, window {args.since} to {win['date_ist'].max()}\n",
         f"- Window reviews: {len(win)}; POOL (1-3 stars): **{n_pool}**; NEG (1-2 stars): **{n_neg}**; 4-5 stars: {len(praise)}",
         f"- H1 = {args.since}..{args.split_date} (pool {int((pool['date_ist'] < args.split_date).sum())}), "
         f"H2 = {args.split_date}.. (pool {int((pool['date_ist'] >= args.split_date).sum())})",
         f"- Reviews with at least one actionable category: {int(pool['actionable'].sum())} ({100 * pool['actionable'].mean():.1f}% of POOL); "
         f"generic negative only: {int(pool['generic_negative_only'].sum())} ({100 * pool['generic_negative_only'].mean():.1f}%); "
         f"neither: {int((~pool['actionable'] & ~pool['generic_negative_only']).sum())}\n",
         "## Categories (multi-label; counts overlap, do not sum)\n",
         "| Category | Nature | n (POOL) | Share of POOL (95% CI) | n (1-2 star) | % of theme that is 1-star | H1 % | H2 % |",
         "|---|---|---|---|---|---|---|---|"]
    for _, r in t.iterrows():
        L.append(f"| {r['id']} | {r['nature']} | {r['n_pool']} | {r['share_pool']} | {r['n_neg']} | {r['pct_of_theme_that_is_1star']} | {r['pct_h1']} | {r['pct_h2']} |")
    L.append("\n## App-side vs operations-side split (mutually exclusive buckets; denominator = POOL)\n")
    sp = split_summary(pool)
    for k, v in sp.items():
        L.append(f"- {k}: {v} ({100 * v / n_pool:.1f}%)")
    L.append("\n## What 4-5 star reviewers praise (keyword themes; denominator = 4-5 star reviews, not mutually exclusive)\n")
    for col in [c for c in praise.columns if c.startswith("praise_")]:
        k = int(praise[col].sum())
        L.append(f"- {col[7:]}: {k} ({100 * k / len(praise):.1f}%)")
    (out_dir / f"themes_{args.since}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())