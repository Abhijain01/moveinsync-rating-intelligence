"""Deterministic multi-label complaint classifier (no API, no model, fully reproducible).

Usage:  python -m rating_intel.classify data\\processed\\run_<stamp>\\reviews_clean.csv --since 2025-10-10
Output: <same folder>/classified_<since>.csv with one 0/1 column per category plus:
        labels (pipe-joined), n_labels, actionable (bool), generic_negative_only (bool), evidence_<id> (matched text)

Definitions
- A review is *actionable* if it matches at least one category other than the cross-cutting tags
  (SAFETY, UPDATE_REGRESSION, WORKPLACE_FEATURE), which only annotate.
- A review is *generic_negative_only* if it has generic negative sentiment ("worst app") but no category.
- Categories are multi-label: category counts overlap, so they must never be summed into a total.
"""
import argparse
import re
import sys
from pathlib import Path

import pandas as pd

try:  # package import (python -m rating_intel)
    from .taxonomy import CATEGORIES, GENERIC_NEGATIVE, PRAISE
except ImportError:  # direct script use
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from taxonomy import CATEGORIES, GENERIC_NEGATIVE, PRAISE  # noqa: E402

CROSS = {c["id"] for c in CATEGORIES if c["nature"] == "cross-cutting"}


def compile_patterns(patterns):
    out = []
    for p in patterns:
        if isinstance(p, tuple):
            out.append(("all", [re.compile(x, re.I | re.S) for x in p[1]]))
        else:
            out.append(("any", [re.compile(p, re.I | re.S)]))
    return out


COMPILED = {c["id"]: compile_patterns(c["patterns"]) for c in CATEGORIES}
PRAISE_COMPILED = {c["id"]: compile_patterns(c["patterns"]) for c in PRAISE}
GENERIC = re.compile(GENERIC_NEGATIVE, re.I)


def match_rules(text, compiled):
    """Return the first matched snippet for a compiled rule list, or None. Pure function."""
    for kind, regs in compiled:
        if kind == "any":
            m = regs[0].search(text)
            if m:
                return m.group(0)[:60]
        else:
            ms = [r.search(text) for r in regs]
            if all(ms):
                first = next((m for m in ms if m.group(0)), ms[0])
                return first.group(0)[:60]
    return None


def classify_text(text):
    """Return dict category_id -> evidence snippet for every category that matches."""
    if not isinstance(text, str) or not text.strip():
        return {}
    hits = {}
    for cid, compiled in COMPILED.items():
        ev = match_rules(text, compiled)
        if ev is not None:
            hits[cid] = ev
    return hits


def classify_frame(df):
    df = df.copy().reset_index(drop=True)
    ids = [c["id"] for c in CATEGORIES]
    if df.empty:  # keep the full column set so downstream code never hits a KeyError
        extra = {**{cid: 0 for cid in ids}, **{f"evidence_{cid}": "" for cid in ids},
                 "labels": "", "n_labels": 0, "actionable": False, "generic_negative_only": False}
        for col, val in extra.items():
            df[col] = pd.Series(dtype=type(val))
        return df
    rows = []
    for t in df["text_norm"].fillna(""):
        hits = classify_text(t)
        row = {cid: int(cid in hits) for cid in ids}
        row.update({f"evidence_{cid}": hits.get(cid, "") for cid in ids})
        core = [c for c in hits if c not in CROSS]
        row["labels"] = "|".join(hits)
        row["n_labels"] = len(hits)
        row["actionable"] = bool(core)
        row["generic_negative_only"] = (not core) and bool(GENERIC.search(t))
        rows.append(row)
    return pd.concat([df, pd.DataFrame(rows)], axis=1)


def praise_frame(df):
    df = df.copy().reset_index(drop=True)
    for pid, comp in PRAISE_COMPILED.items():
        df[f"praise_{pid}"] = [int(match_rules(t, comp) is not None) if isinstance(t, str) else 0 for t in df["text_norm"]]
    return df


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--since", default="2025-10-10", help="IST date, inclusive")
    p.add_argument("--max-score", type=int, default=3, help="classify reviews with score <= this")
    args = p.parse_args(argv)
    df = pd.read_csv(args.csv, encoding="utf-8-sig")
    df = df[(df["date_ist"] >= args.since) & (df["score"] <= args.max_score)]
    out = classify_frame(df)
    path = Path(args.csv).with_name(f"classified_{args.since}.csv")
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"classified {len(out)} reviews -> {path}")
    print(f"actionable: {int(out['actionable'].sum())}, generic-negative only: {int(out['generic_negative_only'].sum())}, "
          f"no signal: {int((~out['actionable'] & ~out['generic_negative_only']).sum())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
