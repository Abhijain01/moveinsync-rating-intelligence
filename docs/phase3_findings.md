# Phase 3 Findings: complaint structure (2026-10-11)

Tags: **[F]** observed fact, **[Q]** quantitative finding, **[I]** inference, **[H]** hypothesis requiring validation.

## 1. Scope and denominators
- Window: 2025-10-10 to 2026-10-09 (IST). 2,856 text reviews. **POOL** = 1-3 star reviews = **846** (1-star 686, 2-star 86, 3-star 74). **NEG** = 1-2 star = 772. 4-5 star = 2,010. [F]
- Categories are multi-label: counts overlap and are never summed. Every percentage below names its denominator. [F]
- Data are self-selected text reviews, one review per reviewer opinion; several reviews can describe one incident and the corpus cannot show that. [F]

## 2. Method (reproducible, no paid API)
1. Read 502 development reviews (60% hash split of POOL, by review_id) and derived 26 categories from what people actually wrote (`scripts/taxonomy.py`).
2. Deterministic regex classifier (`scripts/classify.py`), multi-label, evidence snippet stored per hit.
3. Validation by hand-labelling, in two rounds:
   - Round 1: 120 held-out reviews labelled blind, scored, rules improved from the errors. This sample is now **tuned** and its score is optimistic.
   - Round 2: fresh 100 reviews from the 224 not yet read, labelled blind **before** scoring, rules frozen (taxonomy hash `e3799ec1be70c4ee`). This is the honest test.
4. **Caveat:** all hand labels were produced by Claude, not by an independent human, and the rules were also written by Claude. Labelling is judgement-based (some reviews are genuinely ambiguous). Agreement with a human labeller is unmeasured. Recommended: you re-label 30 rows of `reports/phase3/audit2_sample.csv` and compare (Section 7).

| Test | n | Micro precision | Micro recall | Micro F1 | "Has actionable category" precision / recall |
|---|---|---|---|---|---|
| Round 1 before tuning (frozen v1) | 120 | 0.73 | 0.64 | 0.68 | 1.00 / 0.75 |
| Round 1 after tuning (optimistic) | 120 | 0.79 | 0.98 | 0.87 | 0.99 / 1.00 |
| **Round 2, fresh, frozen rules** | **100** | **0.76** | **0.65** | **0.70** | **1.00 / 0.79** |

[Q] Reading: about one in four predicted labels is wrong (precision 0.76) and about a third of true labels are missed (recall 0.65), so in aggregate the rules under-count by roughly 14%, **but a given category can be over- or under-counted** (the install-error rule over-counts: 25 hits, 17 strict). Treat every count as approximate. The Wilson intervals below cover sampling error only, not classifier error. Categories with gold n < 10 in the test (most of them) have unstable per-category precision/recall; per-category tables are in `validation_audit2_frozen_test.md`. Weakest in the fresh test: ADDRESS_LOCATION_MGMT (recall 0.17), BOOKING_FAILURE (0.25), UPDATE_REGRESSION (0.33), FEATURE_REQUEST (0.40). Rankings of small categories should not be trusted to adjacent ranks.

## 3. What reviewers complain about (POOL n = 846; full table in `themes_2025-10-10.md`)
[Q] 593 (70.1%) have at least one actionable category; 162 (19.1%) are generic negative only ("worst app"); 91 (10.8%) have neither.

| Rank | Theme | n | % of POOL (95% CI) | Nature |
|---|---|---|---|---|
| 1 | Crashes, not opening, slow/endless loading, generic "not working" (CRASH_LOAD_PERF) | 150 | 17.7% (15.3-20.4) | technical |
| 2 | Vehicle/driver/vendor/transport-team conduct (VEHICLE_DRIVER_OPS) | 70 | 8.3% (6.6-10.3) | operational |
| 2 | Routing, clubbing, allocation (ROUTING_ALLOCATION) | 70 | 8.3% (6.6-10.3) | operational |
| 4 | Live tracking / GPS location (TRACKING_LOCATION) | 61 | 7.2% (5.7-9.2) | technical |
| 5 | UI / usability (UI_UX) | 59 | 7.0% (5.4-8.9) | usability |
| 6 | Forced logout / re-login (LOGIN_SESSION) | 57 | 6.7% (5.2-8.6) | technical |
| 7 | OTP not received / cannot sign in (ACCESS_OTP) | 51 | 6.0% (4.6-7.8) | technical |
| 8 | Helpdesk unreachable (SUPPORT_HELPDESK) | 46 | 5.4% (4.1-7.2) | operational |
| 9 | Booking failures (BOOKING_FAILURE) | 43 | 5.1% (3.8-6.8) | mixed |
| 9 | ETA / pickup time wrong or changing (ETA_PICKUP_TIME) | 43 | 5.1% (3.8-6.8) | mixed |

Share of the **686 one-star** reviews (denominator = one-star): stability (crash/install/device) 17.8%; authentication (login or OTP) 12.2%; operations (vehicle/driver, routing, support) 21.1%; tracking or ETA 10.3%; no-show 2.6%. [Q]
[I] There is no single dominant cause. The largest identifiable single cluster is app stability/performance, but it is heterogeneous: of its 150 hits, 65% name a specific failure mode (will not open 18%, slow/loading 27%, crash 13%, errors/server down 11%, hang 4%; overlapping) and 37% say only "not working/buggy".

**App-side vs operations-side** (mutually exclusive buckets, denominator POOL = 846) [Q]: app-side only 46.5%; operations only 12.6%; both 5.7%; mixed-nature only 5.3%; no actionable category 29.9%. [I] Most actionable complaints point at software, but about one in five one-star reviews is mainly about transport operations, which an app change cannot fix directly.

## 4. Trends in the window (H1 = 2025-10-10..2026-04-09, n=380; H2 = 2026-04-10.., n=466)
- [Q] **No aggregate deterioration.** One-star share of all reviews: 23.1% (H1) vs 24.8% (H2), p = 0.28; mean stars 3.84 vs 3.83. 26-category tests: p < 0.002 is the multiple-testing line.
- [Q] **Login/session complaints fell:** 10.3% -> 3.9% of POOL (p = 0.0002, passes the correction). They come in bursts, not as one regression: 20.9% of the POOL in Oct 2025, 19.8% in Jun 2025, 11.1% in Feb 2026, 1-5% each month since Mar 2026 (corpus Apr 2025 onward). Between 10 Oct and 14 Nov 2025, 16 of the 19 versioned login hits are version 12.6. [H] A server/session policy change, not an app release, may explain the bursts; public data cannot separate these.
- [Q] **"Not installed from Play Store" errors are emerging.** Strict phrasing: 2 hits in H1, 15 in H2 (0.5% -> 3.2% of POOL, uncorrected p = 0.0055, **does not pass** the 0.002 correction). Monthly strict hits: Jun 1, Jul 4, Aug 7, Sep 3 (+ the first 9 days of Oct not split out). Spread across versions 12.15-12.19 and 11.0.2 (not one bad build). Reviewers describe error after 2-3 days, uninstall/reinstall every few days, "10 times in 3 weeks". The category rule overcounts (25 hits, only 17 with the strict phrasing); I use the strict count here. [H] An installer-source or signature/integrity check on the client, or an auto-update interaction, is a candidate cause; unverifiable from public data.
- [Q] Stability/performance moved 15.3% -> 19.7% (p = 0.09, not significant).
- [Q] Two reviews explicitly cite Android 17 (12.18.1 on 16 Sep: "not compatible with Android 17"; 12.19.0 on 29 Sep: Pixel 8 on Android 17, app opens and closes), and a third on the same day reports the app stopped working on a OnePlus 12. Eight reviews in the window name a device or OS, 7 of them since July. [H] A compatibility gap on the newest Android release; n is too small to conclude.
- [Q] Version 12.19.0 (first reviewed 2026-09-21): 102 reviews, one-star share 32.4% vs 24.0% for the 12 months. About 2.0 standard errors above the 12-month baseline, picked out of about 28 versions compared, so **not evidence of a regression** (a deviation this size is expected by chance somewhere). UPDATE_REGRESSION language ("after the update") is 3.8% of POOL overall. [H] Test again with a larger 12.19.x sample.

## 5. What is notably absent or counterintuitive (supported by the data)
1. [Q] The review stream does not show the app getting worse. The 2026 mean (3.84) is the highest since 2021.
2. [Q] The loudest historical complaint (forced re-login) has largely faded, while a smaller, more severe-sounding failure (cannot open the app after days) has appeared. Complaint volume is a poor proxy for severity here.
3. [Q] Developer replies have nearly disappeared: 30 of 846 POOL reviews have a reply in the window and 2 of 224 in the last 90 days (replies went to 97.8% of all reviews in 2023, 4.3% in 2025 and 0.8% in 2026 to date). Effect on ratings is **not measurable** from public data. [H]
4. [Q] About 2% of POOL (17 reviews) complain of being forced to rate trips, and one reviewer says the app did not accept feedback until a 5-star was given. [H] A rate-to-continue flow may distort ratings and may conflict with store policy; check against the Google Play policy text (not verified here). Any fix must not push users toward 5 stars.
5. [Q] Praise (4-5 star, n = 2,010) is mostly generic; ease of use 14.7%, service/drivers/support 7.8%, tracking/ETA 4.0%, punctuality 1.6% (keyword themes, overlapping).

## 6. Limits and what remains uncertain
- Recall about 0.65: some themes are under-counted, especially address/nodal-point management, booking failures and feature requests.
- Hand labels are LLM-produced; inter-rater agreement with a human is unmeasured.
- Reviews do not identify the employer or city; operations complaints are a mixture of different vendors and sites. No claim can be made about which client's service is worse.
- "Why" claims (root causes) require internal telemetry (crash logs, auth/session logs, no-show events, ETA vs actual). Phase 4 states which logs would decide each.
- Window-edge: the 12-month window begins in the middle of a login-complaint burst (Oct 2025); H1 vs H2 login comparison is sensitive to that.
- A few reviews are about the driver app (one clearly says so); misattributed reviews exist but are rare.

## 7. Optional: independent check (about 20 minutes)
Open `reports/phase3/audit2_sample.csv`, label 30 rows yourself using the category names in `scripts/taxonomy.py`, and compare with `scripts/audit2_labels.py`. Large disagreement means the numbers above should be treated more cautiously.

## 8. Reproduction
```
python scripts\classify.py data\processed\run_20261010T203205Z\reviews_clean.csv --since 2025-10-10
python scripts\analyze_themes.py data\processed\run_20261010T203205Z\reviews_clean.csv --since 2025-10-10
python scripts\validate_classifier.py reports\phase3\audit2_sample.csv audit2_labels
```
