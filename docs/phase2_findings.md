# Phase 2 Findings: collection, data quality, sampling decision (2026-10-11)

Source: run `run_20261010T203205Z` (google-play-scraper 1.2.7, lang=en, country=in, newest-first, retrieved 2026-10-10 20:32-20:37 UTC). Analysis file: `reviews_clean.csv` (uploaded by user).

## Collection (observed facts)
- The supplied original manifest and data-quality report confirm ingest status complete, stop reason token_exhausted, 122 pages, **24,314 raw and clean rows**, **24,314 unique review IDs**, no rejected rows and no duplicate IDs. Token exhaustion is not proof of a census; collection used lang=en, country=in.
- Listing text-review count at probe time was 23,617, so collected rows exceed it by 697 (+2.9%). Not explained by duplicates. **Hypothesis:** the listing count is lagged or defined differently. Unresolved; do not infer complete source coverage.
- Date range 2014-03-14 to 2026-10-09 (IST). Version known for 92.3% of rows (stable at about 90% in every year). Empty text: 1 row. Writing system: 99.5% Latin letters (Hinglish in Latin script is not separable at this stage), 3 Indic-script rows.
- Reviewer names are not stored.

## Population structure (quantitative)
- Star mix of all 24,314 text reviews: 1-star 6,352 (26.1%), 2-star 1,165, 3-star 1,089, 4-star 2,794, 5-star 12,914 (53.1%).
- Text reviews as a share of lifetime ratings per star (listing histogram): 1-star 86.6%, 3-star 88.5%, 4-star 38.3%, 5-star 13.2%. **2-star shows 139.2% (1,165 text reviews vs 837 histogram ratings)**, which is impossible if both count the same thing. Unresolved data anomaly; possible explanations (rating edits, differently scoped histogram) are hypotheses. Treat the percentages as approximate.
- Quantitative: collected text reviews equal 86.6% of the listing's lifetime 1-star count (6,352 vs 7,335), 88.5% of 3-star, 38.3% of 4-star and 13.2% of 5-star, but **139% of 2-star (1,165 vs 837)**, which is impossible if both sources count the same ratings. The listing histogram and the review feed are therefore not in sync (cause unknown), and these ratios are only indicative. The corpus is not a census of anything; it is a self-selected sample weighted toward low stars. Collection used `lang=en, country=in`; reviews in Indic scripts are only 3 of 24,314, which is plausible for a workforce that writes in English or Latin-script Hinglish but is untested against `lang=hi`.
- Collection-histogram arithmetic (unweighted, not the displayed rating): shortfall from a perfect 5.0 is 41,600 star-points; **one-star ratings account for 70.5%** (29,336). This motivates reading severe complaints but cannot quantify their contribution to Google's recent-weighted displayed rating (S22).
- Text length: median 4 words overall; 5-star median 2 words, 1-star median 11 words; 19.3% of 1-star reviews have fewer than 4 words (low information).

## Trend (quantitative; text reviews only)
- 1-star share by year since 2018 sits between 20% and 31%. 2026 to date: 2,278 reviews, 1-star 24.2%, mean 3.84, the highest yearly mean since 2021 (3.94). Monthly 1-star share over the last 24 months ranges 19.3% to 33.1%.
- **Inference:** the newest-400 sample earlier showed 26.3% 1-star; this is within the normal range, not a recent deterioration. No sustained decline is visible in the public text reviews.
- Lead only: version 12.19.0 (first reviewed 2026-09-21, n=102) has a 1-star share of 32.4% (mean 3.58), against 24.0% for the last 12 months. About 2.0 standard errors above baseline, and about 28 versions were compared, so this is not evidence of a regression. To be tested in Phase 3 with review text.
- Volume is steady at roughly 160-300 text reviews per month in the last two years. 2019 is an outlier year (6,052 reviews, 25% of the corpus); pre-2018 reviews have much lower means (2.1-2.6).

## Developer replies (observed)
- Replies on 9,802 of 24,314 reviews (40.3%) over all time, but by year: 2022 86.6%, 2023 97.8%, 2024 36.8%, **2025 4.3% (125 of 2,923), 2026 to date 0.8% (19 of 2,278)**.
- Historically 1-star and 2-star reviews were answered more often (about 54-55%) than 4-5 star (33-34%). Frequent reply texts are templates (5-star thanks, "reach out to your transport facility manager", "share booking details by email").
- Whether replies change ratings cannot be measured from public data (later star edits are not visible). **Hypothesis requiring validation.**

## Sampling decision
- Primary window for complaint analysis: **last 12 months, 2025-10-10 to 2026-10-09, n = 2,856** (1-star 686 = 24.0%; 2-star 86; 3-star 74; 4-star 179; 5-star 1,831). Chosen because the app and its releases change, and recent complaints are what Engineering can act on; large enough for taxonomy building (772 reviews at 1-2 stars).
- Secondary window: 2022-01-01 onward (n = 12,601) for baselines and reply-rate history. Earlier years are used only as context.
- Rule: percentages are reported with their denominators; a theme with fewer than 30 reviews gets no trend claim. If a theme is too thin in 12 months, widen to 24 months and say so.
- Limits: text reviewers are self-selected; a single incident can generate many reviews; the corpus cannot show which company's employees wrote a review.
