# Phase 6: Measurement plan (2026-10-11)

Tags: **[F]** observed fact, **[Q]** quantitative finding, **[I]** inference, **[H]** hypothesis, **[R]** recommendation.

## 1. The main design decision [R]
**Measure fixes with internal product telemetry. Use public reviews only as a slow, noisy secondary signal.** Section 2 shows why. A fix should be judged "worked" by the failure it targets (crash rate, OTP success), not by whether the Play star average moved.

## 2. What public reviews can and cannot detect [Q]
Baselines from the 2,856 text reviews in the window (2025-10-10 to 2026-10-09; computed by script from `reviews_clean.csv`):

| Metric | Value |
|---|---|
| Mean stars, text reviews | 3.83 (sd 1.71) |
| One-star share | 24.0% |
| Monthly one-star share, range | 19.3% (Jul 2026) to 31.1% (Jun 2026); sd 3.8 points |
| Reviews per month | about 160 to 290 (average about 240 over the window) |
| By quarter, mean stars | Q4-25 3.80, Q1-26 3.83, Q2-26 3.87, Q3-26 3.85 |
| By quarter, one-star share | 23.4%, 23.9%, 24.1%, 24.0% |

- [Q] **Detectable change is large.** With one month of reviews (n about 240) and one-star share near 24%, only a swing of about 11 points is detectable at 5% significance and 80% power. With a quarter (n about 714) it is about 6.3 points; with two quarters (n about 1,430) about 4.5 points. For mean stars the figures are about 0.44, 0.25 and 0.18 stars. Normal month-to-month movement (sd 3.8 points, above the 2.8 points that sampling alone would give at n = 240, so low-star reviews arrive in clumps) is already as large as many realistic fix effects.
- [I] A fix that removes, say, a 5-point slice of complaints would be **invisible in monthly star ratings** and barely visible quarterly. Reviews cannot validate individual releases.
- [R] **MoveInSync itself has a far larger sample.** Play Console reports all ratings (not only the 20.6% that carry text) by app version, country and date. That is the right primary source for "How are our ratings?" and for comparing a staged rollout with the previous version. Public data cannot provide it, so this plan uses text reviews only as the outside view.
- [F] The Play listing showed 4.6 stars from 114,855 ratings when checked in Phase 1; text reviews average 3.83. [I] The two differ because text reviews are a self-selected sample (the listing includes ratings without text); the cause is not verifiable from public data.
- [Q] **Arithmetic on the listing (S12).** The listing's score is 4.6377 over 114,855 ratings and is displayed as 4.6. If the display is the plain mean rounded to one decimal (not verified), it shows 4.7 at 4.65: that needs about **4,000 additional five-star ratings**, or about **350 one-star ratings becoming five-star** (4.8% of the 7,335 one-stars). A true 4.7 needs about 24,000 additional five-star ratings. The average moves slowly, but a displayed one-decimal change is not out of reach; whether it happens depends on the rating inflow, which public data does not show.
- [I] The all-time average is a poor measure of a release because it changes by about 0.000035 per one-star rating avoided. [R] Therefore the success criterion for the rating itself is **"no deterioration plus a sustained downward trend in specific complaint rates"**, not a target star value. No star-lift forecast is made.

## 3. Metric set

### 3.1 Primary: internal telemetry (decides success)
Targets are not invented here. Each target is set after the B0 baseline is read, as "improve against the baseline by an agreed margin, with a stated confidence interval". Where Google publishes a threshold it is used as the floor.

| Backlog item | Primary metric | Definition | Floor / reference |
|---|---|---|---|
| B1 Stability | Crash rate and ANR rate | User-perceived crashes and ANRs per daily active user, by version and device (Android vitals) | Google bad-behaviour thresholds: 1.09% crash, 0.47% ANR; 8% for one device model |
| B1 Stability | Cold-start time | p50 and p95 from tap to trip visible | Set from B0 baseline |
| B1 Stability | Blank-or-spinner sessions | Share of sessions ending with no trip data shown after the timeout | Set from B0 baseline |
| B3 Auth | OTP success | Verified within 2 minutes of the request, by channel and client | Set from B0 funnel |
| B3 Auth | Unrequested logouts | Session ends not initiated by the user, per active user per week; zero during an active trip | Zero during trips |
| B4 Tracking | Location staleness | Time since last driver ping at the moment the employee views the map; p95 | Set from B0 baseline |
| B4 Tracking | ETA error | Absolute error of the ETA shown at 15, 10, 5 minutes before actual arrival | Set from B0 baseline |
| B5 No-show | Disputed or reversed no-shows | Share of no-shows later reversed; share marked by driver vs system | Set from B0 baseline |
| B2 Install | Launch-block rate | Sessions blocked by the integrity or installer check, by version, device, work-profile | Aim for legitimate installs near zero blocked |
| B6 Booking | Rejection by reason | Booking attempts rejected, by rule code; duplicate-schedule rate | Set from B0 baseline |
| B8 Rating flow | Trip-detail access without rating | Share of trips where details are viewable without rating | 100% |
| B7 Support | Contact path usage | In-app helpdesk or driver-contact use; first-response time | Set with Operations |

### 3.2 Secondary: public review complaint rate (trend only)
**Definition.** For each theme, complaint reviews per 1,000 text reviews received in the period (all stars in the denominator, so a change in how many people write low-star reviews does not hide the signal). Computed by `classify.py` and `analyze_themes.py`, counts are approximate (precision about 0.76, recall about 0.65).

Baseline, window 2025-10-10 to 2026-10-09 (1-3 star reviews with the category, per 1,000 of all 2,856 text reviews):

| Theme | Per 1,000 reviews | Complaints |
|---|---|---|
| CRASH_LOAD_PERF | 52.5 | 150 |
| TRACKING_LOCATION | 21.4 | 61 |
| LOGIN_SESSION | 20.0 | 57 |
| ACCESS_OTP | 17.9 | 51 |
| SUPPORT_HELPDESK | 16.1 | 46 |
| ETA_PICKUP_TIME | 15.1 | 43 |
| BOOKING_FAILURE | 15.1 | 43 |
| INSTALL_ERROR (rule, incl. non-strict) | 8.8 | 25 |
| NO_SHOW | 7.4 | 21 |
| DRIVER_CONTACT | 7.0 | 20 |
| FORCED_RATING | 6.0 | 17 |

**Read quarterly, not monthly.** Per-month counts for most themes are in single digits, so month-to-month changes are noise. 1-3 star complaint reviews per month ranged 52 to 102 across all themes combined.

### 3.3 Context metrics (monitor, do not optimise)
- Mean stars and one-star share per quarter (table above).
- Reply rate to 1-3 star reviews: 30 of 846 in the window, 2 of 224 in the last 90 days.
- Review volume per month and per app version.
- Version share of reviews (version 12.6 holds 285 reviews, the most; reviewer-reported version is the version at review time).

## 4. Method for judging a release [R]
1. **Before:** record the primary metric baseline for at least two weeks (B0).
2. **Staged rollout:** release to a small share of users first (Play staged rollout) and compare the primary metric between old and new versions on the same days. Same-day comparison removes weekday and seasonal effects.
3. **Decision rule, fixed in advance:** the fix passes if the primary metric improves beyond the agreed margin **and** no guardrail below worsens beyond its tolerance. Otherwise hold the rollout.
4. **After:** watch the secondary complaint rate for two quarters. A drop is supportive; no drop is not, by itself, evidence of failure (Section 2).

## 5. Guardrails (must not worsen)
| Guardrail | Why |
|---|---|
| Crash-free users and ANR rate | Any new feature must not add instability |
| Stale-data errors (cached trip shown after cancellation) | B1 cache must not mislead |
| OTP abuse and account takeover indicators | B3 convenience must not weaken security |
| No-show false-positive rate | B5 changes must not hide real no-shows from clients |
| Active-trip completion rate | Fixes must not hurt the ride itself |
| Share of users reaching SOS | Safety path stays reachable |

## 6. Review-monitoring cadence
- **Monthly:** run the pipeline (Phase 7) on a fresh public snapshot; compare with the previous snapshot; list new reviews by theme with IDs.
- **Spike rule (implemented in `rating_intel/trends.py`):** expected count = the theme's trailing rate (up to 6 prior months, at least 3) times this month's complaint volume, so a month with more reviews in every category is not flagged for volume alone; flag when the count is at least 5 and P(X >= count) < 0.01 under Poisson; mark `strong` when it also survives a Bonferroni correction over all month-category pairs tested. The report states how many flags chance alone could produce. A version is flagged when its one-star share is higher than all other reviews in the window (p < 0.05 divided by the number of versions tested, at least 50 reviews); this compares a version with other *periods*, so it confounds version with time and is a prompt to look closer, not proof.
- **Quarterly:** report complaint rate per 1,000 reviews with 95% intervals; do not narrate changes inside the interval.
- **Re-validate the classifier** each quarter on 100 fresh hand-labelled reviews, labelled by a person; retire the rules if F1 drops below the Phase 3 level (0.70).
- **Taxonomy drift:** list the most frequent unclassified low-star phrases each month to catch new complaint types.

## 7. Ethics for the measurement loop
- Do not solicit reviews selectively, do not gate the Play review prompt on a good experience, do not offer incentives, and do not ask users to change a rating.
- Replying to reviews is for helping the user (what to try, who to contact), not for requesting a different rating.
- Do not drop negative reviews from the denominators. Report 1-3 star complaint counts together with the full-review base.

## 8. What would change this plan
- If B0 shows telemetry is not available for a metric, replace it with a client-side event and state the new definition.
- If review volume rises materially, the detectable change shrinks (about 1 over the square root of n); revisit Section 2.
- If an independent human audit disagrees with the Phase 3 labels, widen every complaint-rate interval accordingly.
