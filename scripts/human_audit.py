r"""Independent human check of the classifier labels (about 20 minutes).

Step 1 - make the blank sheet and the category guide:
    python scripts\human_audit.py make
  -> reports\phase3\human_audit_sheet.csv   (30 reviews, text only, NO machine labels shown)
  -> reports\phase3\category_guide.md       (the 26 category ids with their meaning)

Step 2 - open the sheet in Excel (or VS Code), fill the `labels` column for every row, save as CSV.
  Put one or more category ids separated by | , for example  ACCESS_OTP|LOGIN_SESSION
  Put NONE if no category applies. Do not open scripts\audit2_labels.py or any validation file first.

Step 3 - compare:
    python scripts\human_audit.py score reports\phase3\human_audit_sheet.csv
  -> prints and writes reports\phase3\human_agreement.md
     (human vs the AI hand labels, and human vs the rule classifier)
"""
import argparse
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rating_intel.classify import classify_frame  # noqa: E402
from rating_intel.taxonomy import CATEGORIES  # noqa: E402

SAMPLE = ROOT / "reports" / "phase3" / "audit2_sample.csv"
SHEET = ROOT / "reports" / "phase3" / "human_audit_sheet.csv"
GUIDE = ROOT / "reports" / "phase3" / "category_guide.md"
OUT = ROOT / "reports" / "phase3" / "human_agreement.md"
IDS = [c["id"] for c in CATEGORIES]
N_ROWS, SEED = 30, 11


def make():
    df = pd.read_csv(SAMPLE, encoding="utf-8-sig")
    rows = sorted(random.Random(SEED).sample(range(len(df)), N_ROWS))
    sheet = pd.DataFrame({"row_index": rows, "stars": df.loc[rows, "score"].to_numpy(),
                          "text": df.loc[rows, "text_norm"].to_numpy(), "labels": ""})
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.to_csv(SHEET, index=False, encoding="utf-8-sig")
    lines = ["# Category guide", "", "Write the ids in the `labels` column, separated by `|`, or `NONE`.", "",
             "| id | meaning |", "|---|---|"]
    lines += [f"| {c['id']} | {c['label']} |" for c in CATEGORIES]
    lines += ["", "A review can have several categories. Label what the reviewer complains about, not how angry they are.",
              "Generic complaints such as 'worst app' with no specific problem are NONE."]
    GUIDE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {SHEET}\nWrote {GUIDE}\nFill the 'labels' column, save, then run: python scripts\\human_audit.py score {SHEET}")


def parse_labels(cell):
    s = "" if pd.isna(cell) else str(cell).strip()
    if s == "":
        return None  # not filled
    if s.upper() == "NONE":
        return set()
    return {x.strip().upper() for x in s.replace(",", "|").replace(";", "|").split("|") if x.strip()}


def agreement(a_sets, b_sets):
    """Agreement between two labellings of the same reviews over all (review, category) decisions."""
    tp = fp = fn = tn = 0
    for a, b in zip(a_sets, b_sets):
        for cid in IDS:
            x, y = cid in a, cid in b
            tp += x and y
            fp += (not x) and y
            fn += x and (not y)
            tn += (not x) and (not y)
    n = tp + fp + fn + tn
    po = (tp + tn) / n
    pe = ((tp + fn) * (tp + fp) + (fn + tn) * (fp + tn)) / (n * n)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 1.0
    exact = sum(a == b for a, b in zip(a_sets, b_sets)) / len(a_sets)
    return {"tp": tp, "fp": fp, "fn": fn, "f1": f1, "kappa": kappa, "exact": exact}


def score(path):
    sheet = pd.read_csv(path, encoding="utf-8-sig")
    human, problems = [], []
    for i, r in sheet.iterrows():
        lab = parse_labels(r["labels"])
        if lab is None:
            problems.append(f"row {i + 2}: labels column is empty")
            continue
        bad = sorted(lab - set(IDS))
        if bad:
            problems.append(f"row {i + 2}: unknown id(s) {bad}")
        human.append(lab)
    if problems:
        print("Fix these first:\n  " + "\n  ".join(problems[:20]))
        return 1
    import audit2_labels
    claude = [set(audit2_labels.LABELS[int(i)]) for i in sheet["row_index"]]
    frame = pd.DataFrame({"text_norm": sheet["text"], "score": sheet["stars"]})
    pred = classify_frame(frame)
    rules = [{cid for cid in IDS if pred.loc[k, cid] == 1} for k in range(len(pred))]
    hc, hr = agreement(human, claude), agreement(human, rules)
    cr = agreement(claude, rules)

    def row(name, m):
        return f"| {name} | {m['f1']:.2f} | {m['kappa']:.2f} | {m['exact']:.0%} | {m['tp']} | {m['fp']} | {m['fn']} |"
    L = [f"# Human agreement check (n={len(human)} reviews, 26 categories)", "",
         "F1 and kappa are over all review-category decisions; exact = the whole label set is identical.", "",
         "| Pair | F1 | Cohen kappa | Exact match | both | only 2nd | only 1st |", "|---|---|---|---|---|---|---|",
         row("Human vs AI hand labels", hc), row("Human vs rule classifier", hr), row("AI hand labels vs rule classifier (same 30)", cr), "",
         "Reading: kappa above about 0.6 is substantial agreement. If human vs AI hand labels is much lower than that, "
         "treat the Phase 3 validation numbers as optimistic. If human vs classifier is close to AI vs classifier, "
         "the classifier's measured quality holds up under an independent labeller.", "",
         "Small sample: with 30 reviews every figure has a wide margin of error."]
    text = "\n".join(L) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(text)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("make")
    s = sub.add_parser("score")
    s.add_argument("sheet")
    a = p.parse_args(argv)
    return make() if a.cmd == "make" else score(a.sheet)


if __name__ == "__main__":
    sys.exit(main() or 0)