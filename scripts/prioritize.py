r"""Phase 5: transparent prioritisation with sensitivity analysis.

Usage (project root):
  python scripts\prioritize.py data\processed\run_<stamp>\reviews_clean.csv --since 2025-10-10 --inputs docs\backlog_inputs.csv --out reports\phase5

Score = reach_pct * severity * confidence * controllability / effort
  reach_pct       MEASURED: % of the complaint pool (1-3 star reviews) with >=1 of the item's categories (union, no double
                  count), taken from the RECENT half of the window (from --split-date) so that a burst that has faded does not
                  inflate an item. The full-window reach is shown alongside. Counts are approximate (precision ~0.76, recall ~0.65).
  severity        JUDGEMENT 1-3: 3 blocks use of the service, 2 degrades it, 1 annoyance.
  confidence      JUDGEMENT 1-3: 3 cause evidenced, 2 symptom clear/cause open, 1 weak or not yet investigated.
  controllability JUDGEMENT 1-3: 3 the app team can fix alone, 2 needs another team/client, 1 mostly outside the app.
  effort          JUDGEMENT 1-3 (S/M/L). Rough guess by the analyst; Engineering must replace it.
Sensitivity: each judgement factor is perturbed by -1/0/+1 (clipped to 1..3) independently for N trials, AND the
measured reach is multiplied by a random factor in [0.7, 1.8] per item, reflecting classifier error (precision 0.76 can
shrink a count; recall as low as 0.2-0.6 on small categories can enlarge it). We report each item's rank range and how
often it lands in the top 3.
"""
import argparse, random, sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classify  # noqa: E402

FACTORS = ["severity", "confidence", "controllability", "effort"]


def score(reach, s, c, k, e):
    return reach * s * c * k / e


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("csv"); p.add_argument("--since", default="2025-10-10")
    p.add_argument("--inputs", default="docs/backlog_inputs.csv"); p.add_argument("--out", default="reports/phase5")
    p.add_argument("--split-date", default=None, help="start of the recent half (default: window start + 182 days)")
    p.add_argument("--reach-noise", nargs=2, type=float, default=[0.7, 1.8])
    p.add_argument("--trials", type=int, default=5000); p.add_argument("--seed", type=int, default=7)
    a = p.parse_args(argv)
    raw = pd.read_csv(a.csv, encoding="utf-8-sig")
    pool = classify.classify_frame(raw[(raw["date_ist"] >= a.since) & (raw["score"] <= 3)])
    n = len(pool)
    split = a.split_date or (pd.to_datetime(a.since) + pd.Timedelta(days=182)).strftime("%Y-%m-%d")
    recent = pool[pool["date_ist"] >= split]
    inp = pd.read_csv(a.inputs)
    full, rec = [], []
    for cats in inp["categories"]:
        cols = cats.split(";")
        full.append(100 * (pool[cols].sum(axis=1) > 0).sum() / n)
        rec.append(100 * (recent[cols].sum(axis=1) > 0).sum() / len(recent) if len(recent) else 0.0)
    inp["reach_full_pct"] = [round(r, 1) for r in full]
    inp["reach_pct"] = [round(r, 1) for r in rec]
    inp["score"] = [round(score(r, s, c, k, e), 1) for r, s, c, k, e in
                    zip(inp.reach_pct, inp.severity, inp.confidence, inp.controllability, inp.effort)]
    inp["rank"] = inp["score"].rank(ascending=False, method="min").astype(int)
    rng = random.Random(a.seed)
    ranks = {i: [] for i in inp["id"]}
    for _ in range(a.trials):
        sc = {}
        for _, r in inp.iterrows():
            v = [min(3, max(1, int(r[f]) + rng.choice([-1, 0, 1]))) for f in FACTORS]
            sc[r["id"]] = score(r.reach_pct * rng.uniform(*a.reach_noise), *v)
        order = sorted(sc, key=lambda x: -sc[x])
        for pos, i in enumerate(order, 1):
            ranks[i].append(pos)
    inp["rank_min"] = [min(ranks[i]) for i in inp["id"]]
    inp["rank_max"] = [max(ranks[i]) for i in inp["id"]]
    inp["median_rank"] = [sorted(ranks[i])[len(ranks[i]) // 2] for i in inp["id"]]
    inp["pct_top3"] = [round(100 * sum(1 for x in ranks[i] if x <= 3) / a.trials) for i in inp["id"]]
    inp = inp.sort_values("rank")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    inp.to_csv(out / "backlog_scored.csv", index=False)
    L = [f"# Phase 5 scored backlog (pool n={n}; recent half from {split}, n={len(recent)}; {a.trials} sensitivity trials; reach noise x{a.reach_noise[0]}-{a.reach_noise[1]})\n",
         "| Rank | ID | Item | Reach % recent | Reach % full year | Sev | Conf | Ctrl | Effort | Score | Median rank | Rank range | % in top 3 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in inp.iterrows():
        L.append(f"| {r['rank']} | {r['id']} | {r['title']} | {r.reach_pct} | {r.reach_full_pct} | {r.severity} | {r.confidence} | {r.controllability} | {r.effort} | {r.score} | {r.median_rank} | {r.rank_min}-{r.rank_max} | {r.pct_top3} |")
    (out / "backlog_scored.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
