"""Score the rule-based classifier against hand labels on an audit sample.

Usage (from the project root):
  python scripts\\validate_classifier.py reports\\phase3\\audit2_sample.csv audit2_labels --out reports\\phase3\\validation_audit2.md

`labels_module` is a module in scripts/ exposing LABELS = {row_index: set(category_ids)}.
Row index = row position in the sample CSV (0-based). Metrics are per-category and micro-averaged over all
(review, category) decisions. Small categories (gold n < 10) are unstable and are flagged.
"""
import argparse
import importlib
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classify  # noqa: E402
from taxonomy import CATEGORIES  # noqa: E402

CROSS = {c["id"] for c in CATEGORIES if c["nature"] == "cross-cutting"}


def score(sample_df, labels):
    pred = classify.classify_frame(sample_df)
    ids = [c["id"] for c in CATEGORIES]
    rows = []
    for cid in ids:
        tp = fp = fn = 0
        for i in range(len(pred)):
            p = bool(pred.loc[i, cid])
            g = cid in labels[i]
            tp += p and g
            fp += p and not g
            fn += (not p) and g
        rows.append({"category": cid, "tp": int(tp), "fp": int(fp), "fn": int(fn),
                     "gold_n": int(tp + fn), "pred_n": int(tp + fp),
                     "precision": round(tp / (tp + fp), 2) if tp + fp else None,
                     "recall": round(tp / (tp + fn), 2) if tp + fn else None})
    t = pd.DataFrame(rows)
    TP, FP, FN = t.tp.sum(), t.fp.sum(), t.fn.sum()
    micro = {"precision": TP / (TP + FP), "recall": TP / (TP + FN), "f1": 2 * TP / (2 * TP + FP + FN),
             "tp": int(TP), "fp": int(FP), "fn": int(FN)}
    gold_act = [bool(labels[i] - CROSS) for i in range(len(pred))]
    pred_act = pred["actionable"].tolist()
    tp = sum(g and p for g, p in zip(gold_act, pred_act))
    fp = sum((not g) and p for g, p in zip(gold_act, pred_act))
    fn = sum(g and not p for g, p in zip(gold_act, pred_act))
    act = {"gold": sum(gold_act), "pred": sum(pred_act),
           "precision": tp / (tp + fp) if tp + fp else float("nan"),
           "recall": tp / (tp + fn) if tp + fn else float("nan")}
    return t, micro, act


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sample_csv")
    p.add_argument("labels_module")
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    labels = importlib.import_module(a.labels_module).LABELS
    df = pd.read_csv(a.sample_csv, encoding="utf-8-sig")
    t, micro, act = score(df, labels)
    L = [f"# Classifier validation: {Path(a.sample_csv).name} (n={len(df)})\n",
         f"- Micro precision **{micro['precision']:.2f}**, recall **{micro['recall']:.2f}**, F1 **{micro['f1']:.2f}** "
         f"(tp={micro['tp']}, fp={micro['fp']}, fn={micro['fn']})",
         f"- 'Has an actionable category' flag: gold {act['gold']}, predicted {act['pred']}, "
         f"precision {act['precision']:.2f}, recall {act['recall']:.2f}\n",
         "| Category | gold n | predicted n | TP | FP | FN | Precision | Recall | Note |", "|---|---|---|---|---|---|---|---|---|"]
    for _, r in t.sort_values("gold_n", ascending=False).iterrows():
        note = "gold n < 10: unstable" if r.gold_n < 10 else ""
        L.append(f"| {r.category} | {r.gold_n} | {r.pred_n} | {r.tp} | {r.fp} | {r.fn} | {r.precision} | {r.recall} | {note} |")
    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())