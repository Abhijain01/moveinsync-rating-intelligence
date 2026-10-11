# MoveInSync Rating Intelligence

Candidate case study: **why are MoveInSync's Play Store ratings lower than they should be, and what should we fix first?**
Employee app `com.moveinsync.ets`. Public data only. Free tools only. Reproducible.

**Start here:** [`docs/EXECUTIVE_RECOMMENDATION.md`](docs/EXECUTIVE_RECOMMENDATION.md) (2 pages) and [`docs/engineering_tickets.md`](docs/engineering_tickets.md) (ticket-level backlog).

## Headline findings
- Analysed all 24,314 public text reviews; the last 12 months hold 2,856 reviews, of which 846 are rated 1-3 stars.
- Largest controllable cluster: **app stability 17.7%** of low-star reviews (19.7% in the last six months). Sign-in/OTP is 12.4% for the year but 9.2% recently (forced logout fell, OTP is flat). About 18% of complaint reviews involve transport operations (routing, vehicles, drivers, helpdesk), which an app release will not fix.
- No aggregate deterioration in the last 12 months. "Not installed from Play Store" errors in July and August 2026 stand out even after scaling for review volume and correcting for multiple tests, and are flagged for investigation.
- Recommended first step: a 1-2 week data gate (Android vitals, OTP funnel), then stability and authentication fixes, plus restarting replies to reviews.
- **No star-lift promise**: monthly review data is too noisy to detect small effects (see `docs/phase6_measurement_plan.md`).

## Answer "How are our ratings?" in one command
```powershell
python -m rating_intel status data\processed\run_20261010T203205Z\reviews_clean.csv
```
Prints the last 90 days against the previous 90 with confidence intervals, whether the change is real, and the top complaint themes.

## What is in the repository
| Path | Purpose |
|---|---|
| `docs/EXECUTIVE_RECOMMENDATION.md` | The recommendation: what to fix, in what order, how we will know |
| `docs/engineering_tickets.md` | Tickets with evidence, scope, acceptance criteria, telemetry, guardrails |
| `docs/methodology.md` | How I got there, tools, validation, limits, assumptions |
| `docs/phase4_root_cause_register.md` | Root-cause hypotheses with competing explanations and the internal data that would decide each |
| `docs/phase5_backlog.md`, `docs/backlog_inputs.csv` | Scoring model and sensitivity test |
| `docs/phase6_measurement_plan.md` | Metrics, baselines, detectable effect, guardrails |
| `docs/phase3_findings.md`, `docs/phase2_findings.md`, `docs/baseline.md`, `docs/source_register.md` (S1-S21) | Evidence and sources |
| `rating_intel/` | Reusable package: clean, classify, trends, spikes, compare, status, optional local LLM layer |
| `scripts/` | Collection (`ingest.py`), research scripts for phases 1-5 |
| `tests/` | 85 automated tests |
| `reports/phase3/`, `reports/phase5/` | Result tables and evidence samples (public review excerpts, no reviewer names) |

## Pipeline
```
collect (scripts/ingest.py) -> clean -> classify (26-category rules, frozen) -> quantify + trends
   -> spike detection -> snapshot comparison -> report.md      (+ optional local-LLM labels, off by default)
```
Details of each stage, the optional AI layer and its safeguards: [`docs/pipeline.md`](docs/pipeline.md).

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
```

## Monthly runbook
```powershell
python scripts\ingest.py --out data\raw                      # about 3 minutes, needs internet to Google Play
.\scripts\run_all.ps1 -RawRun data\raw\run_<stamp> -Prev data\processed\run_<old stamp>\reviews_clean.csv
```
`run_all.ps1` cleans the snapshot, prints the status headline and writes `reports\analysis_run_<stamp>\report.md` (themes, monthly table, spikes, version flags, changes since the last snapshot, reproducibility hashes).

## Quality controls
- 85 automated tests (invalid ratings, empty text, duplicates, timezone edges, multi-label counting, statistics, spike rules, invalid or failing model output, retry behaviour, snapshot comparison, determinism, parity with the analysed snapshot). CI runs them on every push.
- Taxonomy hash check: changing a rule requires re-running the hand-labelled validation.
- Classifier on a frozen fresh test: precision 0.76, recall 0.65, F1 0.70. Counts are approximate (under-counting by roughly 14% in aggregate, with individual categories over- or under-counted).

## Limits
Public reviews are a self-selected sample and show symptoms, not causes. Hand labels used for validation were produced by an AI assistant, not an independent human (a 30-row human re-label is recommended). Root causes are hypotheses until internal telemetry is read. See `docs/methodology.md`.

## Ethics
Do not use this work to solicit or steer ratings, hide negative reviews, or write replies that ask for a re-rating. Reviewer names are not collected.

## License
MIT. See `LICENSE`.
