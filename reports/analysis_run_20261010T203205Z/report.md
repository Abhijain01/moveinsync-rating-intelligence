# Rating Intelligence report (2025-10-10 to 2026-10-09)

## 0. How are our Play Store ratings?
- Play listing when the snapshot was taken (2026-10-10): 4.6 stars from 114,857 ratings. Google weights recent ratings; this listing score is not a lifetime arithmetic mean and is not directly comparable with the text reviews below.
- Last 90 days to 2026-10-09: 721 text reviews, mean 3.8 stars (95% CI 3.68-3.93), one-star 25.0% (CI 21.9-28.3), 4-5 star 68.9%.
- Previous 90 days: 817 reviews, mean 3.83, one-star 25.0%.
- Change: mean stars -0.03 (p=0.73), one-star share +0.0 points (p=1.00): no statistically distinguishable change.
- Most frequent complaint themes in the last period (1-3 star reviews, overlapping): Crashes, blank screen, not opening, slow or endless loading 45; Cab late/not provided, driver conduct, vendor / transport-team failures 22; Routing, clubbing, sequence and cab allocation 21.
- Safety-related mentions in the same period: 6 (read these first).
- Public text reviews are a self-selected sample; use internal telemetry to judge a release.

## 1. Scope and denominators
- Reviews in window: **2856**; one-star share 24.0%; mean stars 3.834.
- Complaint pool (1-3 stars): **846**; of which 1-2 stars: 772.
- In the pool: 593 have an actionable category, 162 are generic negative only, 91 neither.
- Halves for trend tests: before vs from 2026-04-10.
- Categories overlap (multi-label): never add their counts together.

## 2. Complaint themes (share of the 1-3 star pool, Wilson 95% interval; per-1,000 uses all window reviews)
| category | nature | n_pool | pct_pool | ci_low | ci_high | per_1000_reviews | pct_h1 | pct_h2 | p_value | passes_bonferroni |
|---|---|---|---|---|---|---|---|---|---|---|
| CRASH_LOAD_PERF | technical | 150 | 17.7 | 15.3 | 20.4 | 52.5 | 15.3 | 19.7 | 0.08973 | False |
| VEHICLE_DRIVER_OPS | operational | 70 | 8.3 | 6.6 | 10.3 | 24.5 | 7.6 | 8.8 | 0.54007 | False |
| ROUTING_ALLOCATION | operational | 70 | 8.3 | 6.6 | 10.3 | 24.5 | 7.9 | 8.6 | 0.71749 | False |
| TRACKING_LOCATION | technical | 61 | 7.2 | 5.7 | 9.2 | 21.4 | 6.8 | 7.5 | 0.70842 | False |
| UI_UX | usability | 59 | 7.0 | 5.4 | 8.9 | 20.7 | 8.2 | 6.0 | 0.22215 | False |
| LOGIN_SESSION | technical | 57 | 6.7 | 5.2 | 8.6 | 20.0 | 10.3 | 3.9 | 0.00022 | True |
| ACCESS_OTP | technical | 51 | 6.0 | 4.6 | 7.8 | 17.9 | 6.6 | 5.6 | 0.54346 | False |
| SUPPORT_HELPDESK | operational | 46 | 5.4 | 4.1 | 7.2 | 16.1 | 4.2 | 6.4 | 0.1553 | False |
| BOOKING_FAILURE | mixed | 43 | 5.1 | 3.8 | 6.8 | 15.1 | 5.8 | 4.5 | 0.39805 | False |
| ETA_PICKUP_TIME | mixed | 43 | 5.1 | 3.8 | 6.8 | 15.1 | 4.7 | 5.4 | 0.67914 | False |
| FEATURE_REQUEST | usability | 33 | 3.9 | 2.8 | 5.4 | 11.6 | 5.0 | 3.0 | 0.13588 | False |
| NOTIFICATIONS | technical | 33 | 3.9 | 2.8 | 5.4 | 11.6 | 3.2 | 4.5 | 0.3136 | False |
| UPDATE_REGRESSION | cross-cutting | 32 | 3.8 | 2.7 | 5.3 | 11.2 | 3.2 | 4.3 | 0.38981 | False |
| INSTALL_ERROR | technical | 25 | 3.0 | 2.0 | 4.3 | 8.8 | 1.1 | 4.5 | 0.00317 | False |
| CANCEL_EDIT | mixed | 23 | 2.7 | 1.8 | 4.0 | 8.1 | 1.8 | 3.4 | 0.15686 | False |
| SAFETY | cross-cutting | 21 | 2.5 | 1.6 | 3.8 | 7.4 | 2.1 | 2.8 | 0.52448 | False |
| BOARDING_QR_OTP | technical | 21 | 2.5 | 1.6 | 3.8 | 7.4 | 2.6 | 2.4 | 0.80099 | False |
| NO_SHOW | mixed | 21 | 2.5 | 1.6 | 3.8 | 7.4 | 2.9 | 2.1 | 0.48623 | False |
| DRIVER_CONTACT | usability | 20 | 2.4 | 1.5 | 3.6 | 7.0 | 2.6 | 2.1 | 0.64374 | False |
| BOOKING_RULES | policy | 18 | 2.1 | 1.4 | 3.3 | 6.3 | 2.4 | 1.9 | 0.66123 | False |
| PERMISSIONS_CONSENT | policy | 18 | 2.1 | 1.4 | 3.3 | 6.3 | 2.6 | 1.7 | 0.35904 | False |
| FORCED_RATING | usability | 17 | 2.0 | 1.3 | 3.2 | 6.0 | 2.1 | 1.9 | 0.85768 | False |
| ADDRESS_LOCATION_MGMT | mixed | 16 | 1.9 | 1.2 | 3.1 | 5.6 | 2.4 | 1.5 | 0.35753 | False |
| FEEDBACK_FLOW_BROKEN | technical | 13 | 1.5 | 0.9 | 2.6 | 4.6 | 0.8 | 2.1 | 0.11061 | False |
| DEVICE_COMPAT | technical | 8 | 0.9 | 0.5 | 1.9 | 2.8 | 0.0 | 1.7 | 0.01028 | False |
| WORKPLACE_FEATURE | cross-cutting | 8 | 0.9 | 0.5 | 1.9 | 2.8 | 0.3 | 1.5 | 0.06401 | False |

`passes_bonferroni` is true when the H1-vs-H2 difference has p < 0.05 divided by the number of categories tested.

## 3. Monthly volume and one-star share
| month_ist | reviews | one_star | one_star_pct | mean_stars | reply_rate_pct |
|---|---|---|---|---|---|
| 2025-10 | 222 | 50 | 22.5 | 3.838 | 7.7 |
| 2025-11 | 160 | 42 | 26.2 | 3.688 | 16.2 |
| 2025-12 | 196 | 43 | 21.9 | 3.837 | 9.2 |
| 2026-01 | 211 | 49 | 23.2 | 3.768 | 4.3 |
| 2026-02 | 207 | 57 | 27.5 | 3.739 | 0.0 |
| 2026-03 | 197 | 41 | 20.8 | 3.98 | 1.0 |
| 2026-04 | 292 | 61 | 20.9 | 4.034 | 0.3 |
| 2026-05 | 247 | 50 | 20.2 | 4.016 | 0.4 |
| 2026-06 | 273 | 85 | 31.1 | 3.56 | 0.7 |
| 2026-07 | 285 | 55 | 19.3 | 4.014 | 0.4 |
| 2026-08 | 242 | 69 | 28.5 | 3.653 | 0.4 |
| 2026-09 | 245 | 61 | 24.9 | 3.845 | 0.4 |
| 2026-10 | 79 | 23 | 29.1 | 3.696 | 1.3 |

## 4. Theme spikes (count above the trailing rate scaled to that month's complaint volume; prompts to read the reviews, not proof of an incident)
| month_ist | category | count | expected | upper_bound | p_value | strong |
|---|---|---|---|---|---|---|
| 2026-07 | INSTALL_ERROR | 5 | 0.35 | 2 | 3.18e-05 | True |
| 2026-08 | INSTALL_ERROR | 9 | 1.23 | 4 | 6.08e-06 | True |

230 month-category pairs were tested at alpha 0.01; up to about 2.3 flags can appear by chance alone (an upper estimate, since the count >= 5 rule removes some). `strong` = also passes a Bonferroni correction over all pairs tested. Read the reviews before concluding anything.

## 5. Versions with a higher one-star share than the rest (versions with at least 50 reviews, Bonferroni-corrected)
No version stands out after correction.

## 7. Limits
- Counts come from a deterministic rule classifier with precision about 0.76 and recall about 0.65 on a frozen hand-labelled test (Phase 3); treat counts as approximate: in aggregate they under-count by about 14%, but individual categories can be over- or under-counted, and the intervals cover sampling error only.
- Public text reviews are a self-selected sample; they do not represent all users and cannot show causes.
- Reviews do not identify employer, city or vendor.
- Model-assisted labels: not used. They never enter the counts above.

## 8. Reproducibility
- Tool 1.0.0, taxonomy sha256 prefix `e3799ec1be70c4ee`, input sha256 prefix `f1bddcf2e73a6570`, Python 3.9.1, pandas 2.3.3, run at 2026-10-12T17:40:44+00:00.
