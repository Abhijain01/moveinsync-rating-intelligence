# Pipeline reference

| Stage | Code | Behaviour |
|---|---|---|
| Collect | `scripts/ingest.py` | Newest-first pull in pages of 200 with retries for short pages (the scraper hides request errors), immutable `reviews.jsonl`, `manifest.json`, resumable via `--resume`. Reviewer names are not stored. |
| Clean | `rating_intel/clean.py` | Rejects missing id, invalid star (not an integer 1-5), invalid or future date; deduplicates on `review_id` keeping the latest retrieval; converts UTC to IST; flags empty and repeated text without dropping it. |
| Classify | `rating_intel/classify.py`, `taxonomy.py` | Deterministic multi-label regex rules with an evidence snippet per hit. Cross-cutting tags (SAFETY, UPDATE_REGRESSION, WORKPLACE_FEATURE) annotate but do not make a review "actionable". |
| Optional AI | `rating_intel/llm.py` | Off by default. Local Ollama only (`.env.example`). Asked only about reviews the rules left unlabelled. Answers must be JSON with known category ids and an evidence quote that occurs in the review; invalid or failed calls are retried with backoff, then dropped. Labels are stored in separate columns and never enter the counts. Paid providers are deliberately not implemented. |
| Quantify | `rating_intel/pipeline.py`, `stats.py` | Share of the 1-3 star pool with Wilson 95% intervals; complaints per 1,000 reviews; first-half vs second-half z-tests with a Bonferroni flag. |
| Spikes | `rating_intel/trends.py` | Expected count = the theme's trailing rate (up to 6 prior months, at least 3) times the month's complaint volume; flagged when the count is at least 5 and Poisson P(X >= count) < 0.01; `strong` when it also passes a Bonferroni correction over all pairs tested. The report prints how many flags chance alone could produce. |
| Versions | `rating_intel/trends.py` | One-star share of each version (at least 50 reviews) against all other reviews, Bonferroni over versions tested. |
| Compare | `rating_intel/compare.py` | New, missing, edited and re-scored reviews, and replies added, between two snapshots; warns if the new snapshot is partial. |
| Status | `rating_intel/status.py` | Last N days vs previous N days with intervals and a plain verdict; Play listing score from the manifest when given. |

## Outputs of `analyze`
`report.md`, `themes.csv`, `monthly.csv`, `spikes.csv`, `version_flags.csv`, `classified_pool.csv`, `new_reviews.csv` (with `--prev`), `run_info.json` (input hash, taxonomy hash, window, library versions).

## Exit behaviour
A cleaned-snapshot check raises a clear error if columns are missing; `analyze` refuses empty windows; model failures never stop the run.

## Included submission snapshot
The original raw JSONL, manifest, cleaned CSV and quality report are included under `run_20261010T203205Z`. `python scripts/demo.py` regenerates the canonical report with explicit window 2025-10-10 to 2026-10-09 and split 2026-04-10, without Google network access. The manifest's score is a captured listing value, not a lifetime arithmetic average; keep it distinct from text-review means. The exact snapshot is whitelisted in `.gitignore`; future runs stay ignored.

The supplied probe contained reviewer name/image fields, which have been removed from the shared copy. The main raw/clean review snapshot already excluded those fields. No change was made to the classifier or original cleaned CSV.
