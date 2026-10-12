# How I got there: method, tools and limits

## Process (one phase at a time, each checked before the next)
| Phase | What I did | Output |
|---|---|---|
| 1 Baseline | Verified the exact app (`com.moveinsync.ets`, employee-facing), kept driver, Field and Partner apps out of scope, read the Help Center, tested data access | `docs/baseline.md`, `docs/source_register.md` |
| 2 Collection | Pulled the public Play text reviews returned with lang=en, country=in with `google-play-scraper` (122 pages, 24,314 rows, 2014-2026), immutable raw snapshot, retries and resume, cleaned and deduplicated, data-quality report | `scripts/ingest.py`, `scripts/clean.py`, `docs/phase2_findings.md` |
| 3 Complaint structure | Read 502 development reviews, derived 26 categories from what people wrote, built a rule classifier, validated on hand-labelled reviews (a tuned sample, then a fresh frozen test) | `docs/phase3_findings.md`, `reports/phase3/` |
| 4 Root causes | For each cluster: symptom, impact, evidence, competing explanations, system boundary, internal data that would decide, fix, test | `docs/phase4_root_cause_register.md` |
| 5 Prioritisation | Transparent score (reach x severity x confidence x controllability / effort) with 5,000 sensitivity trials | `docs/phase5_backlog.md`, `scripts/prioritize.py` |
| 6 Measurement | Baselines, detectable-effect analysis, metric definitions, guardrails | `docs/phase6_measurement_plan.md` |
| 7 Reusable tool | `rating_intel` package, CLI, 85 tests | `rating_intel/`, `tests/` |
| 8 Submission | Executive recommendation and ticket-level backlog | `docs/EXECUTIVE_RECOMMENDATION.md`, `docs/engineering_tickets.md` |

## Tools
- **Free and open source:** Python, pandas, google-play-scraper 1.2.7, pytest, regular expressions. No paid API is used or needed.
- **Optional:** a local Ollama model for extra labels (off by default; validated with a fake provider only).
- **AI assistants:** Claude helped the original planning, research, coding, tests and validation labels. ChatGPT/Codex reviewed and corrected the submission, verified the supplied snapshot, and packaged the offline demo. AI involvement does not make the validation independent.

## What was validated, and how
- **Data quality and coverage:** the supplied manifest and quality report confirm 24,314 raw and clean rows, no duplicate IDs and no rejected rows. The feed exceeds the metadata text-review count (23,617) by 697; coverage is not a verified census. Collection was lang=en, country=in. Review IDs provide traceability.
- **Classifier:** Round 1 (120 reviews) was used to improve the rules, so its score (F1 0.87) is optimistic. Round 2 (100 fresh reviews, rules frozen, labelled before scoring) gave **precision 0.76, recall 0.65, F1 0.70**. Counts are therefore approximate (about 14% under-counted in aggregate, individual categories either way), and categories with fewer than 10 test examples are unstable.
- **Statistics:** Wilson intervals, two-proportion z-tests with a multiple-testing line (p < 0.002 for 26 categories), Poisson spike bounds, sensitivity analysis on the ranking.
- **Code:** 85 tests passed with zero skips on the supplied original snapshot on 2026-10-12, including Phase 3 parity and headline claims. The prior public checkout ran 69 tests and skipped 16 due to absent data. Taxonomy hash remains frozen.
- **Independent review:** after the first full draft an independent reviewer, given only the documents and code and not the data, attacked the submission. It found, and I fixed or corrected: a volume artifact in my spike detection (a 'June 2026 cluster' that disappears once counts are scaled by review volume), rating arithmetic that used the rounded 4.6 instead of 4.6377, an over-weighted login burst in the prioritisation (now scored on the recent half and with reach noise in the sensitivity test), missing coverage of safety, boarding and pickup-time changes, Help Center claims that were not in the source register (re-read and cited as S13-S18), and several code edge cases (empty windows, one-word model evidence, rounding before a p-value).
- **Corrections I made along the way:** an install-error rule that over-counted (25 hits vs 17 strict) so the strict count is used in the findings; classifier rules that over-matched ("management", "apartment complex") and were tightened; three numeric slips in Phase 3 notes; a bug in the snapshot comparison caught by tests.

## Honest limits
1. **The hand labels were made by the AI assistant, not an independent human; a first human check has now been done on 30 of them.** On 30 reviews (fixed random sample, `scripts/human_audit.py`, results in `reports/phase3/human_agreement.md`) I labelled the reviews without seeing the AI labels. Human vs AI labels: F1 0.84, Cohen kappa 0.84, exact match 73%. Human vs rule classifier: F1 0.67, kappa 0.66, exact 60% (AI vs classifier on the same 30: F1 0.75). So the AI labels broadly hold up, and the classifier's quality against a human (F1 0.67) is close to the frozen-test figure (0.70). Caveats: 30 reviews is a small sample (wide margin of error); I wrote my own category names first, and for 13 of the 30 reviews I then matched them to the official ids from a table suggested by the AI assistant, confirming or changing each, so those 13 are not fully blind; the AI also had written the category list. This is a spot check, not a full independent audit.
2. Public reviews are a self-selected sample; they show symptoms, not causes, and cannot identify the employer, city or vendor.
3. I have not seen MoveInSync's code, telemetry or customers. Every root cause is a hypothesis with a named test; effort estimates are guesses.
4. Help Center articles were read from public pages; whether a documented feature ships and works reliably is unverified.
5. The model-assisted labelling layer has not been measured against a real model.
6. No star-rating lift is forecast. Section 5 of the recommendation explains why.

## Assumptions
- "Our Play Store ratings" means the employee app listing.
- The last 12 months (2025-10-10 to 2026-10-09) represent current behaviour.
- Reviewer names are neither needed nor stored.

## Submission correction (2026-10-12)
The original archive supplied the raw/clean snapshot and manifest, enabling all 85 tests to run without skips. Rating-lift arithmetic was removed using Google's rating definition (S22); booking investigation starts day 1; B9 has joint owners, deadlines and pilot metrics; safety assessment is immediate on discovery; human-audit disclosures are synchronized. The taxonomy and complaint counts were not changed. Reviewer-name/image fields were removed from the probe before sharing. Original text and IDs remain.

## Reproduce
```powershell
pip install -r requirements.txt
python -m pytest
python -m rating_intel status data\processed\run_20261010T203205Z\reviews_clean.csv
python scripts\demo.py
```
Fresh data: `scripts\run_all.ps1` (see README).
