"""End-to-end analysis of one cleaned snapshot: classify, quantify, trend, flag, compare, report."""
import datetime as dt
import hashlib
import json
import platform
from pathlib import Path

import pandas as pd

from . import __version__
from .classify import classify_frame
from .compare import compare_snapshots, new_review_score_mix
from .llm import hybrid_label
from .stats import wilson
from .status import headline
from .taxonomy import CATEGORIES
from .trends import detect_theme_spikes, half_split_table, monthly_summary, theme_counts_by_month, version_flags

REQUIRED_COLUMNS = ["review_id", "score", "date_ist", "month_ist", "text_norm", "has_reply", "version_known", "app_version"]
CROSS = {c["id"] for c in CATEGORIES if c["nature"] == "cross-cutting"}
META = {c["id"]: c for c in CATEGORIES}
IDS = [c["id"] for c in CATEGORIES]


def sha256_of(path, n=16):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def load_clean(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} is not a cleaned snapshot; missing columns: {missing}. Run the 'clean' step first.")
    if "text_norm" in df:
        df["text_norm"] = df["text_norm"].fillna("")
    return df


def default_window(df):
    last = pd.to_datetime(df["date_ist"].max())
    since = (last - pd.Timedelta(days=364)).strftime("%Y-%m-%d")
    mid = (pd.to_datetime(since) + pd.Timedelta(days=182)).strftime("%Y-%m-%d")
    return since, mid


def theme_table(pool, window, split_date):
    n_pool, n_all = len(pool), len(window)
    hs = half_split_table(pool, IDS, split_date).set_index("category")
    rows = []
    for cid in IDS:
        k = int(pool[cid].sum())
        lo, hi = wilson(k, n_pool)
        rows.append({
            "category": cid, "label": META[cid]["label"], "nature": META[cid]["nature"],
            "n_pool": k, "pct_pool": round(100 * k / n_pool, 1) if n_pool else None,
            "ci_low": round(100 * lo, 1) if n_pool else None, "ci_high": round(100 * hi, 1) if n_pool else None,
            "per_1000_reviews": round(1000 * k / n_all, 1) if n_all else None,
            "pct_h1": hs.loc[cid, "pct_h1"], "pct_h2": hs.loc[cid, "pct_h2"],
            "p_value": hs.loc[cid, "p_value"], "passes_bonferroni": bool(hs.loc[cid, "passes_bonferroni"]),
        })
    return pd.DataFrame(rows).sort_values("n_pool", ascending=False).reset_index(drop=True)


def md_table(df, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(r[c]) else str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def run_analysis(clean_csv, out_dir, since=None, split_date=None, prev_csv=None, provider=None, sleep=None, manifest_path=None):
    """Run the full analysis and write outputs. Returns a summary dict (also written to run_info.json)."""
    df = load_clean(clean_csv)
    if df.empty:
        raise ValueError("Cleaned snapshot has no rows.")
    d_since, d_split = default_window(df)
    since, split_date = since or d_since, split_date or d_split
    window = df[df["date_ist"] >= since].copy()
    if window.empty:
        raise ValueError(f"No reviews on or after {since}.")
    pool_raw = window[window["score"] <= 3]
    pool = classify_frame(pool_raw)
    n_pool, n_neg = len(pool), int((pool["score"] <= 2).sum())

    # Optional model-assisted labels for reviews the rules left unlabelled (kept in separate columns).
    llm_info = {"enabled": provider is not None, "attempted": 0, "labelled": 0, "fallback": 0}
    pool["llm_labels"], pool["llm_source"] = "", "rules"
    if provider is not None:
        kw = {"sleep": sleep} if sleep else {}
        for i, r in pool.iterrows():
            res = hybrid_label(r["text_norm"], bool(r["labels"]), provider, **kw)
            if res["source"] == "rules":
                continue
            llm_info["attempted"] += 1
            pool.at[i, "llm_source"] = res["source"]
            pool.at[i, "llm_labels"] = "|".join(res["labels"])
        llm_info["labelled"] = int((pool["llm_labels"] != "").sum())
        llm_info["fallback"] = int((pool["llm_source"] == "rules_fallback").sum())

    themes = theme_table(pool, window, split_date)
    monthly = monthly_summary(window)
    counts = theme_counts_by_month(pool, [c for c in IDS if c not in CROSS])
    totals = pool.groupby("month_ist").size()
    spikes = detect_theme_spikes(counts, totals=totals)
    vflags = version_flags(window)

    actionable = int(pool["actionable"].sum())
    generic = int(pool["generic_negative_only"].sum())

    compare = None
    if prev_csv:
        prev = load_clean(prev_csv)
        compare = compare_snapshots(prev, df)

    head = headline(df, manifest_path=manifest_path)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    themes.to_csv(out / "themes.csv", index=False, encoding="utf-8-sig")
    monthly.to_csv(out / "monthly.csv", index=False, encoding="utf-8-sig")
    spikes.to_csv(out / "spikes.csv", index=False, encoding="utf-8-sig")
    vflags.to_csv(out / "version_flags.csv", index=False, encoding="utf-8-sig")
    keep = ["review_id", "date_ist", "score", "app_version", "text_norm", "labels", "actionable",
            "generic_negative_only", "llm_labels", "llm_source"]
    pool[keep].to_csv(out / "classified_pool.csv", index=False, encoding="utf-8-sig")
    if compare is not None:
        compare["new_reviews"].to_csv(out / "new_reviews.csv", index=False, encoding="utf-8-sig")

    info = {
        "tool_version": __version__,
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "input_csv": str(clean_csv), "input_sha256_16": sha256_of(clean_csv),
        "previous_csv": str(prev_csv) if prev_csv else None,
        "taxonomy_sha256_16": sha256_of(Path(__file__).with_name("taxonomy.py")),
        "window_since": since, "window_until": str(window["date_ist"].max()), "split_date": split_date,
        "window_reviews": len(window), "pool_1to3": n_pool, "neg_1to2": n_neg,
        "one_star_share_pct": round(100 * (window["score"] == 1).mean(), 1),
        "mean_stars": round(float(window["score"].mean()), 3),
        "actionable": actionable, "generic_negative_only": generic,
        "no_signal": n_pool - actionable - generic if n_pool else 0,
        "n_spikes": len(spikes), "spike_tests": spikes.attrs.get("n_tests", 0), "spike_alpha": spikes.attrs.get("alpha", 0.01), "n_version_flags": int(vflags["flag_higher"].sum()) if len(vflags) else 0,
        "headline": {k: v for k, v in head.items() if k != "lines"}, "headline_lines": head["lines"],
        "llm": llm_info, "python": platform.python_version(), "pandas": pd.__version__,
    }
    (out / "run_info.json").write_text(json.dumps(info, indent=2, default=str), encoding="utf-8")
    (out / "report.md").write_text(render_report(info, themes, monthly, spikes, vflags, compare), encoding="utf-8")
    info["out_dir"] = str(out)
    return info


def render_report(info, themes, monthly, spikes, vflags, compare):
    L = [f"# Rating Intelligence report ({info['window_since']} to {info['window_until']})\n",
         "## 0. How are our Play Store ratings?",
         *[f"- {x}" for x in info["headline_lines"]], "",
         "## 1. Scope and denominators",
         f"- Reviews in window: **{info['window_reviews']}**; one-star share {info['one_star_share_pct']}%; mean stars {info['mean_stars']}.",
         f"- Complaint pool (1-3 stars): **{info['pool_1to3']}**; of which 1-2 stars: {info['neg_1to2']}.",
         f"- In the pool: {info['actionable']} have an actionable category, {info['generic_negative_only']} are generic negative only, {info['no_signal']} neither.",
         f"- Halves for trend tests: before vs from {info['split_date']}.",
         "- Categories overlap (multi-label): never add their counts together.\n",
         "## 2. Complaint themes (share of the 1-3 star pool, Wilson 95% interval; per-1,000 uses all window reviews)",
         md_table(themes, ["category", "nature", "n_pool", "pct_pool", "ci_low", "ci_high", "per_1000_reviews", "pct_h1", "pct_h2", "p_value", "passes_bonferroni"]),
         "\n`passes_bonferroni` is true when the H1-vs-H2 difference has p < 0.05 divided by the number of categories tested.\n",
         "## 3. Monthly volume and one-star share",
         md_table(monthly, ["month_ist", "reviews", "one_star", "one_star_pct", "mean_stars", "reply_rate_pct"]), "",
         "## 4. Theme spikes (count above the trailing rate scaled to that month's complaint volume; prompts to read the reviews, not proof of an incident)"]
    L.append(md_table(spikes, ["month_ist", "category", "count", "expected", "upper_bound", "p_value", "strong"]) if len(spikes) else "No theme exceeded the count predicted by its trailing rate (Poisson 99%, count >= 5).")
    L.append(f"\n{info['spike_tests']} month-category pairs were tested at alpha {info['spike_alpha']}; up to about {info['spike_tests'] * info['spike_alpha']:.1f} flags can appear by chance alone (an upper estimate, since the count >= 5 rule removes some). `strong` = also passes a Bonferroni correction over all pairs tested. Read the reviews before concluding anything.")
    L += ["", "## 5. Versions with a higher one-star share than the rest (versions with at least 50 reviews, Bonferroni-corrected)"]
    flagged = vflags[vflags["flag_higher"]] if len(vflags) else vflags
    L.append(md_table(flagged, ["app_version", "reviews", "one_star_pct", "ci_low", "ci_high", "rest_one_star_pct", "p_value"]) if len(flagged) else "No version stands out after correction.")
    if compare is not None:
        L += ["", "## 6. Change since the previous snapshot",
              f"- Rows: {compare['old_rows']} -> {compare['new_rows']}; new reviews: {compare['n_new']}; missing in new: {compare['n_missing_in_new']}; "
              f"edited: {compare['n_edited']}; re-scored: {compare['n_rescored']}; replies added: {compare['n_reply_added']}.",
              f"- Star mix of new reviews: {new_review_score_mix(compare['new_reviews'])}"]
        if compare["new_snapshot_may_be_partial"]:
            L.append("- WARNING: the new snapshot starts later than the old one; 'missing' counts are not reliable.")
    L += ["", "## 7. Limits",
          "- Counts come from a deterministic rule classifier with precision about 0.76 and recall about 0.65 on a frozen hand-labelled test (Phase 3); treat counts as approximate: in aggregate they under-count by about 14%, but individual categories can be over- or under-counted, and the intervals cover sampling error only.",
          "- Public text reviews are a self-selected sample; they do not represent all users and cannot show causes.",
          "- Reviews do not identify employer, city or vendor.",
          f"- Model-assisted labels: {'enabled; attempted ' + str(info['llm']['attempted']) + ', labelled ' + str(info['llm']['labelled']) + ', fell back to rules ' + str(info['llm']['fallback']) if info['llm']['enabled'] else 'not used'}. They never enter the counts above.",
          "", "## 8. Reproducibility",
          f"- Tool {info['tool_version']}, taxonomy sha256 prefix `{info['taxonomy_sha256_16']}`, input sha256 prefix `{info['input_sha256_16']}`, Python {info['python']}, pandas {info['pandas']}, run at {info['run_utc']}.\n"]
    return "\n".join(L)
