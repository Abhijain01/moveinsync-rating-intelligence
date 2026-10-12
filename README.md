# MoveInSync Rating Intelligence

Prepared by **Abhishek Jain** for the Forward Deployed Engineer case study.

**Recommendation:** start stability diagnosis and resilience work; investigate self-booking immediately; run an owned commute-reliability workstream across Product and Operations; assess credible safety failures the same day. Measure confirmed failures before promising a star-rating improvement.

Start with [the executive recommendation](docs/EXECUTIVE_RECOMMENDATION.md), then [the implementation tickets](docs/engineering_tickets.md). [The short submission note](docs/SUBMISSION_NOTE.md) explains the method and tools.

## Findings
- English/India collection returned **24,314 reviews**. The analyzed year (2025-10-10 to 2026-10-09) contains **2,856 reviews**, including **846 rated 1-3 stars**. This is a scoped collection, not a verified census of public reviews.
- App stability is the largest single reported controllable cluster: **150 low-star reviews, 17.7%** (19.7% in the recent half). Sign-in/OTP union: 105, 12.4% for the year and 9.2% recently. Counts are approximate.
- Booking-related union: 87, 10.3%. The booking classifier misses complaints (frozen-test recall 0.25, only four gold examples); instrument the booking funnel and reproduce defects from day 1 rather than postponing it.
- About 18% of low-star reviews touch operations-related labels. Cause and ownership remain unconfirmed; route software, client policy, fleet capacity and vendor execution require joint diagnosis.
- No statistically detectable deterioration in the analyzed text-review windows. July/August install-error rule counts are unusual after volume scaling and multiple-test correction; investigate rather than assert a confirmed incident.
- Google gives recent ratings more weight; public data cannot predict the ratings needed to reach 4.7. No rating lift is promised.

## Run the included snapshot offline

Python 3.9 or newer. Run these commands from the project root after downloading or cloning the complete corrected project:

```bash
python -m pip install -r requirements.txt
python scripts/demo.py
python -m pytest -ra
```

Package installation requires network access once. The demo and tests use the **included original snapshot** and do not contact Google Play. Tested result: **85 passed, zero skipped** on 2026-10-12. The earlier public checkout ran 69 and skipped 16 because its snapshot was absent; these files are now whitelisted in `.gitignore`. GitHub will reflect this correction only after the updated files are committed.

The demo prints the latest 90 days against the previous 90 and regenerates [the full report](reports/analysis_run_20261010T203205Z/report.md): themes, monthly rates, spikes, version flags and reproducibility hashes.

Equivalent explicit commands:

```bash
python -m rating_intel status data/processed/run_20261010T203205Z/reviews_clean.csv --manifest data/raw/run_20261010T203205Z/manifest.json
python -m rating_intel analyze data/processed/run_20261010T203205Z/reviews_clean.csv --since 2025-10-10 --split-date 2026-04-10 --manifest data/raw/run_20261010T203205Z/manifest.json --out reports/analysis_run_20261010T203205Z
```

## Evidence and implementation

| Path | Purpose |
|---|---|
| `docs/EXECUTIVE_RECOMMENDATION.md` | Decision, sequence, first five days, limits |
| `docs/engineering_tickets.md` | B0-B13 specs, owners, acceptance, metrics and guardrails |
| `docs/methodology.md`, `docs/SUBMISSION_NOTE.md` | Method, AI disclosure and form-field note |
| `docs/phase4_root_cause_register.md` | Symptoms, competing explanations and discriminating evidence |
| `docs/phase5_backlog.md`, `docs/backlog_inputs.csv` | Historical score model, sensitivity and investigation overrides |
| `docs/phase6_measurement_plan.md` | Product, booking, operations and rating measurements |
| `docs/source_register.md`, `docs/baseline.md`, `docs/phase2_findings.md`, `docs/phase3_findings.md` | Public sources and evidence context |
| `data/raw/run_20261010T203205Z/` | Original review JSONL and collection manifest |
| `data/processed/run_20261010T203205Z/` | Original cleaned CSV and data-quality report |
| `reports/analysis_run_20261010T203205Z/` | Reproduced report and machine-readable outputs |
| `reports/phase3/`, `reports/phase5/` | Classifier audits, examples and prioritization results |
| `rating_intel/`, `scripts/`, `tests/` | Reusable tool, collector, offline demo and 85 tests |
| `docs/CORRECTIONS_AND_VALIDATION.md` | Corrections, validation results and publishing instructions |

## Refresh when the question returns

```bash
python scripts/ingest.py --out data/raw
python -m rating_intel clean data/raw/run_<new_stamp>
python -m rating_intel status data/processed/run_<new_stamp>/reviews_clean.csv --manifest data/raw/run_<new_stamp>/manifest.json
python -m rating_intel analyze data/processed/run_<new_stamp>/reviews_clean.csv --prev data/processed/run_20261010T203205Z/reviews_clean.csv --manifest data/raw/run_<new_stamp>/manifest.json --out reports/analysis_run_<new_stamp>
```

Fresh collection requires access to Google Play. Windows users can use `scripts/run_all.ps1` after collection. Newly collected snapshots remain ignored by default; the original submission snapshot is included explicitly.

Read `docs/pipeline.md` for stage behavior. Optional local Ollama labeling is off by default, has only been checked with a fake provider, and never changes the counted rule labels.

## Quality, limits and data handling

Frozen 100-review AI-labeled test: precision 0.76, recall 0.65, F1 0.70. A completed 30-review human spot check gave human-vs-AI F1 0.84 and human-vs-rule F1 0.67. Thirteen labels used AI-assisted category mapping, so the spot check was not fully blind or independent. Intervals exclude classifier error; small-category rankings are uncertain.

Reviews are self-selected, may reflect multiple complaints about one incident, and cannot establish a client's identity or a technical root cause. English/India scope is untested against other languages. Feed and listing counts differ. Listing values changed slightly between the probe and collection; each source keeps its own dated values.

Reviewer-name and profile-image fields are excluded from the shared evidence; the supplied probe was sanitized to remove them. Original public review text and review IDs remain for traceability and may contain details users wrote themselves. Virtual environments, caches, Git internals, private `.env` files and serialized pagination checkpoints are excluded.

No selective rating solicitation, incentives, rating gates or requests for higher ratings. Help users with replies and verify fixes through product telemetry.

MIT license. See `LICENSE`.
