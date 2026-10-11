"""Phase 2 cleaning: validate, normalise and deduplicate one raw run; write a data-quality report.

Usage:  python scripts\\clean.py data\\raw\\run_<stamp>
Output: data/processed/<run_id>/reviews_clean.csv, rejects.csv, data_quality.md
Original text is preserved in `text_original`; `text_norm` is a normalised copy for matching.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

IST = "Asia/Kolkata"
REQUIRED = ["review_id", "text_original", "score", "at_utc"]


def load_raw(jsonl_path):
    rows = []
    with Path(jsonl_path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def normalise_text(value):
    """NFKC, collapse whitespace, strip. Case is kept; matching code lowercases later."""
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def script_class(text):
    """Dominant writing system among letters: latin / indic / other / mixed / empty.
    Note: Hinglish written in Latin letters is classed 'latin'; real language ID is a later step."""
    latin = indic = other = 0
    for ch in text:
        if not ch.isalpha():
            continue
        cp = ord(ch)
        if cp < 0x250:
            latin += 1
        elif 0x0900 <= cp <= 0x0DFF:
            indic += 1
        else:
            other += 1
    total = latin + indic + other
    if total == 0:
        return "empty"
    for name, n in (("latin", latin), ("indic", indic), ("other", other)):
        if n / total >= 0.9:
            return name
    return "mixed"


def validate_and_clean(df, retrieved_cutoff=None):
    """Return (clean_df, rejects_df, counts). Reject reasons are mutually exclusive, in this order."""
    counts = {"raw_rows": len(df)}
    df = df.copy()
    for col in REQUIRED:
        if col not in df.columns:
            df[col] = None
    df["_at"] = pd.to_datetime(df["at_utc"], errors="coerce", utc=True)
    score_num = pd.to_numeric(df["score"], errors="coerce")
    df["_score_ok"] = score_num.notna() & score_num.between(1, 5) & (score_num == score_num.round())

    reason = pd.Series("", index=df.index)
    missing_id = df["review_id"].isna() | (df["review_id"].astype(str).str.strip() == "")
    reason[missing_id] = "missing_review_id"
    reason[(reason == "") & ~df["_score_ok"]] = "invalid_score"
    reason[(reason == "") & df["_at"].isna()] = "invalid_date"
    if retrieved_cutoff is not None:
        cutoff = pd.Timestamp(retrieved_cutoff) + pd.Timedelta(days=1)
        reason[(reason == "") & (df["_at"] > cutoff)] = "future_date"

    rejects = df[reason != ""].copy()
    rejects["reject_reason"] = reason[reason != ""]
    ok = df[reason == ""].copy()
    counts["rejected"] = len(rejects)
    counts["rejected_by_reason"] = rejects["reject_reason"].value_counts().to_dict()

    # Deduplicate on review_id; keep the most recently retrieved copy.
    ok = ok.sort_values(["retrieved_at_utc", "page_index"], kind="stable")
    before = len(ok)
    ok = ok.drop_duplicates("review_id", keep="last")
    counts["duplicate_review_id_dropped"] = before - len(ok)

    ok["score"] = pd.to_numeric(ok["score"]).astype(int)
    ok["text_norm"] = ok["text_original"].map(normalise_text)
    ok["empty_text"] = ok["text_norm"] == ""
    ok["script_class"] = ok["text_norm"].map(script_class)
    ok["word_count"] = ok["text_norm"].map(lambda s: len(s.split()))
    ok["char_len"] = ok["text_norm"].str.len()
    ok["at_utc"] = ok["_at"]
    local = ok["_at"].dt.tz_convert(IST)
    ok["date_ist"] = local.dt.strftime("%Y-%m-%d")
    ok["month_ist"] = local.dt.strftime("%Y-%m")
    ok["week_start_ist"] = (local.dt.tz_localize(None).dt.normalize()
                            - pd.to_timedelta(local.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")
    ok["has_reply"] = ok["reply_text"].fillna("").astype(str).str.strip() != ""
    ok["version_known"] = ok["app_version"].fillna("").astype(str).str.strip() != ""
    # Flag (do not drop) identical non-trivial texts: possible spam or copy-paste.
    key = ok["text_norm"].str.lower()
    sizes = key.map(key.value_counts())
    ok["text_dup_group_size"] = sizes.where(ok["char_len"] >= 15, 1).astype(int)

    cols = ["review_id", "source_ref", "score", "at_utc", "date_ist", "week_start_ist", "month_ist",
            "app_version", "version_known", "thumbs_up", "has_reply", "reply_text", "replied_at_utc",
            "text_original", "text_norm", "empty_text", "script_class", "word_count", "char_len",
            "text_dup_group_size", "page_index", "retrieved_at_utc"]
    clean = ok[[c for c in cols if c in ok.columns]].sort_values("at_utc", ascending=False)
    counts["clean_rows"] = len(clean)
    return clean.reset_index(drop=True), rejects.drop(columns=["_at", "_score_ok"], errors="ignore"), counts


def pct(n, d):
    return f"{100 * n / d:.1f}%" if d else "n/a"


def quality_report(clean, counts, manifest):
    n = len(clean)
    listing = manifest.get("listing_at_start") or {}
    exp_text, exp_ratings = listing.get("reviews"), listing.get("ratings")
    hist = listing.get("histogram")
    L = []
    L.append(f"# Data-quality report: {manifest.get('run_id')}\n")
    L.append(f"- Run status: **{manifest.get('status')}**, stop reason: `{manifest.get('stop_reason')}`, pages: {manifest.get('pages')}")
    L.append(f"- Scraper: google-play-scraper {manifest.get('environment', {}).get('google_play_scraper')}; "
             f"params: {json.dumps(manifest.get('params'))}")
    L.append(f"- Listing at start: rating {listing.get('score')}, ratings count {exp_ratings}, text-review count {exp_text}, app version {listing.get('version')}\n")
    L.append("## Completeness (observed)")
    L.append(f"- Raw rows: {counts['raw_rows']}; rejected: {counts['rejected']} {counts['rejected_by_reason']}; "
             f"duplicate review_id dropped: {counts['duplicate_review_id_dropped']}; **clean rows: {n}**")
    if exp_text:
        L.append(f"- Clean rows as a share of the listing's text-review count: **{pct(n, exp_text)}** "
                 f"({n} of {exp_text}). A low share means pagination stopped early or the listing count includes reviews the API does not return; it does not tell us which.")
    L.append("")
    if n:
        L.append("## Coverage")
        L.append(f"- Date range (IST): {clean['date_ist'].min()} to {clean['date_ist'].max()}")
        L.append(f"- Version known: {pct(int(clean['version_known'].sum()), n)}; developer reply present: {pct(int(clean['has_reply'].sum()), n)} "
                 f"({int(clean['has_reply'].sum())}); thumbs-up > 0: {pct(int((clean['thumbs_up'].fillna(0) > 0).sum()), n)}")
        L.append(f"- Empty text: {int(clean['empty_text'].sum())} ({pct(int(clean['empty_text'].sum()), n)}); median words: {clean['word_count'].median():.0f}; "
                 f"texts with fewer than 4 words: {pct(int((clean['word_count'] < 4).sum()), n)}")
        L.append(f"- Identical-text groups (>=15 chars): {int((clean['text_dup_group_size'] > 1).sum())} reviews belong to a repeated text\n")
        L.append("## Star distribution: collected text reviews vs listing lifetime ratings")
        L.append("The two columns are different populations (text reviews vs all ratings). Do not read the gap as a trend; use the time-sliced view below.\n")
        L.append("| Stars | Collected n | Collected % | Lifetime ratings n | Lifetime % |")
        L.append("|---|---|---|---|---|")
        tot_h = sum(hist) if hist else 0
        for s in (1, 2, 3, 4, 5):
            c = int((clean["score"] == s).sum())
            hn = hist[s - 1] if hist and len(hist) == 5 else None
            L.append(f"| {s} | {c} | {pct(c, n)} | {hn if hn is not None else 'n/a'} | {pct(hn, tot_h) if hn is not None else 'n/a'} |")
        L.append("\n## Reviews and 1-star share by month (IST)")
        L.append("| Month | Reviews | 1-star | 1-star % | Mean stars |")
        L.append("|---|---|---|---|---|")
        g = clean.groupby("month_ist").agg(n=("score", "size"), one=("score", lambda s: int((s == 1).sum())), mean=("score", "mean"))
        for m, r in g.sort_index().iterrows():
            L.append(f"| {m} | {int(r['n'])} | {int(r['one'])} | {pct(int(r['one']), int(r['n']))} | {r['mean']:.2f} |")
        L.append("\n## Writing systems")
        for k, v in clean["script_class"].value_counts().items():
            L.append(f"- {k}: {v} ({pct(int(v), n)})")
        L.append("\n## Top app versions (reviews)")
        vc = clean.loc[clean["version_known"], "app_version"].value_counts().head(10)
        for k, v in vc.items():
            L.append(f"- {k}: {v}")
    return "\n".join(L) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run_dir", help="raw run folder containing reviews.jsonl and manifest.json")
    p.add_argument("--out", default="data/processed")
    args = p.parse_args(argv)

    run_dir = Path(args.run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    raw = load_raw(run_dir / "reviews.jsonl")
    if raw.empty:
        print("No rows in reviews.jsonl", file=sys.stderr)
        return 1
    cutoff = raw["retrieved_at_utc"].max()
    clean, rejects, counts = validate_and_clean(raw, retrieved_cutoff=cutoff)

    out_dir = Path(args.out) / manifest.get("run_id", run_dir.name)
    out_dir.mkdir(parents=True, exist_ok=True)
    clean.to_csv(out_dir / "reviews_clean.csv", index=False, encoding="utf-8-sig")
    rejects.to_csv(out_dir / "rejects.csv", index=False, encoding="utf-8-sig")
    report = quality_report(clean, counts, manifest)
    (out_dir / "data_quality.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
