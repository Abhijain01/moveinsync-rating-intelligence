# How I got there: method, tools and limits

## Process (one phase at a time, each checked before the next)
| Phase | What I did | Output |
|---|---|---|
| 1 Baseline | Verified the exact app (`com.moveinsync.ets`, employee-facing), kept driver, Field and Partner apps out of scope, read the Help Center, tested data access | `docs/baseline.md`, `docs/source_register.md` |
| 2 Collection | Pulled all public Play text reviews with `google-play-scraper` (122 pages, 24,314 rows, 2014-2026), immutable raw snapshot, retries and resume, cleaned and deduplicated, data-quality report | `scripts/ingest.py`, `scripts/clean.py`, `docs/phase2_findings.md` |
| 3 Complaint structure | Read 502 development reviews, derived 26 categories from what people wrote, built a rule classifier, validated on hand-labelled reviews (a tuned sample, then a fresh frozen test) | `docs/phase3_findings.md`, `reports/phase3/` |
| 4 Root causes | For each cluster: symptom, impact, evidence, competing explanations, system boundary, internal data that would decide, fix, test | `docs/phase4_root_cause_register.md` |
| 5 Prioritisation | Transparent score (reach x severity x confidence x controllability / effort) with 5,000 sensitivity trials | `docs/phase5_backlog.md`, `scripts/prioritize.py` |
| 6 Measurement | Baselines, detectable-effect analysis, metric definitions, guardrails | `docs/phase6_measurement_plan.md` |
| 7 Reusable tool | `rating_intel` package, CLI, 85 tests | `rating_intel/`, `tests/` |
| 8 Submission | Executive recommendation and ticket-level backlog | `docs/EXECUTIVE_RECOMMENDATION.md`, `docs/engineering_tickets.md` |

## Tools
- **Free and open source:** Python, pandas, google-play-scraper 1.2.7, pytest, regular expressions. No paid API is used or needed.
- **Optional:** a local Ollama model for extra labels (off by default; validated with a fake provider only).
- **AI assistant (Claude):** helped plan the work, research public sources, write code and tests, and hand-label review samples. Disclosed below because it affects how far the validation can be trusted.

## What was validated, and how
- **Data completeness:** 24,314 clean rows against the listing's reported text-review count; duplicates and rejects reported. Review IDs make every claim traceable.
- **Classifier:** Round 1 (120 reviews) was used to improve the rules, so its score (F1 0.87) is optimistic. Round 2 (100 fresh reviews, rules frozen, labelled before scoring) gave **precision 0.76, recall 0.65, F1 0.70**. Counts are therefore approximate (about 14% under-counted in aggregate, individual categories either way), and categories with fewer than 10 test examples are unstable.
- **Statistics:** Wilson intervals, two-proportion z-tests with a multiple-testing line (p < 0.002 for 26 categories), Poisson spike bounds, sensitivity analysis on the ranking.
- **Code:** 85 automated tests including parity with the Phase 3 numbers; taxonomy hash check.
- **Independent review:** after the first full draft an independent reviewer, given only the documents and code and not the data, attacked the submission. It found, and I fixed or corrected: a volume artifact in my spike detection (a 'June 2026 cluster' that disappears once counts are scaled by review volume), rating arithmetic that used the rounded 4.6 instead of 4.6377, an over-weighted login burst in the prioritisation (now scored on the recent half and with reach noise in the sensitivity test), missing coverage of safety, boarding and pickup-time changes, Help Center claims that were not in the source register (re-read and cited as S13-S18), and several code edge cases (empty windows, one-word model evidence, rounding before a p-value).
- **Corrections I made along the way:** an install-error rule that over-counted (25 hits vs 17 strict) so the strict count is used in the findings; classifier rules that over-matched ("management", "apartment complex") and were tightened; three numeric slips in Phase 3 notes; a bug in the snapshot comparison caught by tests.

## Honest limits
1. **The hand labels were made by the AI assistant, not an independent human.** Agreement with a human is unmeasured. A 30-row human re-label (about 20 minutes) is the next check: `reports/phase3/audit2_sample.csv` against `scripts/audit2_labels.py`.
2. Public reviews are a self-selected sample; they show symptoms, not causes, and cannot identify the employer, city or vendor.
3. I have not seen MoveInSync's code, telemetry or customers. Every root cause is a hypothesis with a named test; effort estimates are guesses.
4. Help Center articles were read from public pages; whether a documented feature ships and works reliably is unverified.
5. The model-assisted labelling layer has not been measured against a real model.
6. No star-rating lift is forecast. Section 5 of the recommendation explains why.

## Assumptions
- "Our Play Store ratings" means the employee app listing.
- The last 12 months (2025-10-10 to 2026-10-09) represent current behaviour.
- Reviewer names are neither needed nor stored.

## Reproduce
```powershell
pip install -r requirements.txt
python -m pytest
python -m rating_intel status data\processed\run_20261010T203205Z\reviews_clean.csv
python -m rating_intel analyze data\processed\run_20261010T203205Z\reviews_clean.csv --out reports\analysis_2026-10
```
Fresh data: `scripts\run_all.ps1` (see README).
