# Baseline Note (Phase 1) - dated 2026-10-11

## Scope decision
In scope: Play app **MoveInSync, `com.moveinsync.ets`** (employee-facing). Out of scope: Driver Partner (`com.moveinsync.driver.dco`), Field app (`field.moveinsync.ets`), Partner Lite, Workplace kiosk, Driver Book.

## Observed facts (source S1, single fetch)
- Rating 4.6; "1.15L reviews" (Indian notation, about 115,000, rounded by Google); 10L+ downloads; updated 8 Oct 2026.
- **Local probe, retrieved 2026-10-10 20:09 UTC (source S12):** title MoveInSync, package `com.moveinsync.ets`, score 4.6377, **114,855 ratings** (so the listing's "1.15L reviews" is the ratings count), **23,617 reviews with text** (20.6% of ratings), installs band 1,000,000+, version 12.19.0, listing updated 2026-10-08 16:48 UTC. This independently corroborates S1.
- **Lifetime star histogram (S12):** 1-star 7,335 (6.4%), 2-star 837 (0.7%), 3-star 1,230 (1.1%), 4-star 7,294 (6.4%), 5-star 98,153 (85.5%). Histogram sums to 114,849 (6 fewer than the ratings count; unexplained, immaterial). Negative (1-2 star) share 7.1%. 1-star outnumbers 2-star by 8.8 to 1: a polarised, J-shaped distribution.
- The listing describes one app covering commute **and** workplace features (desk booking, meeting rooms). Complaints may therefore concern non-commute features; the taxonomy needs a "workplace feature" label so they are not counted as commute failures.
- Data safety lists location among collected data types; the page flags "Shares location".

## What the three visible reviews show (anecdotes, not a sample)
Dates 29 Jun, 1 Jul, 7 Jul 2026. Themes: surprise no-show marking with a request for a check-in reminder after the vehicle passes the pickup point; confusion after a UI change that made shuttle booking two steps and a request to hide other vehicles; slow GPS, wrong pickup/drop timings, other users' live location not visible. These are hypotheses to test, not findings.

## Important caveats
1. **Premise check (inference):** an aggregate of 4.6 is high in absolute terms. "Lower than it should be" may refer to the recent trend, a different app (driver/field apps are lower but have tiny review counts), or a higher internal target. Phase 2 must examine recent-window ratings, not only the all-time figure.
2. **Corroboration (resolved):** the page fetch figures were confirmed by the scraper's metadata call (score 4.6377, 114,855 ratings). Earlier page fetches of other URL variants returned the Field app page; that tool behaviour is not relied on.
3. **Histogram counts** are not visible on the listing page but are available from the scraper metadata (S12), recorded above.
4. **Recent text reviews look much more negative than lifetime ratings (quantitative, not yet interpretable):** in the newest 400 text reviews (2026-08-20 to 2026-10-09 IST) 1-star is 26.3% and 5-star 66.0%, against 6.4% and 85.5% lifetime. These are different populations (text reviews vs all ratings), so this is a lead, not a finding. Phase 2 compares 1-star share over time within text reviews.
5. **Version and timestamp semantics:** the scraper maps `appVersion` and `reviewCreatedVersion` to the same field (so they are one variable), and builds timestamps in the machine's local time; ingestion converts to UTC and analysis uses IST dates.
6. The Help Center confirms a no-show process exists (driver-marked with a code, or system-marked when no sign-in by trip end; S6) and an enforcement guide (S17) with warnings, a 30-minute alternate-transport filter, logout-trip cancellation after a login no-show and an optional approval-based restore request (off by default). Neither article describes a grace period at the pickup point or a way to contest a mistaken mark. Whether the complaint is about the rule, the communication of it, or a defect is a **hypothesis**.

## Journey map: app-controlled vs operations-controlled
| Step | Primarily app/platform | Primarily operations/external |
|------|------------------------|-------------------------------|
| 1 Onboarding/access | Login, OTP, registration from office records | Employee data supplied by the client company |
| 2 Shift/roster | Display of shift | Roster data from client HR/transport desk |
| 3 Self-booking | Booking UI, validation, confirmation | Client policy limits and cut-offs |
| 4 Vehicle assignment/routing | Routing engine output shown in app | Fleet supply, vendor availability |
| 5 Pickup-time communication | Notification delivery, ETA display | ETA accuracy depends on routing and driver |
| 6 Live tracking | Map, GPS ingestion, refresh | Driver device, network, driver behaviour |
| 7 OTP/driver verification/boarding | OTP flow, check-in | Driver conduct |
| 8 Trip completion | Trip-state transitions, no-show logic | Driver actions |
| 9 Incident/support | In-app reporting, status | Ops team and transport desk resolution |

## Why the rating alone cannot give the root cause
It is a single aggregate across versions, features, client companies and years; it hides recency, theme, version, and whether the failure is software or operations. Review text, dates and versions (Phase 2-3) are needed, and internal telemetry is needed to confirm causes.

## Data-access finding
- Workspace shell cannot reach play.google.com; the listing page exposes only about three reviews to a page fetch. Collection runs on the user's machine.
- **Probe result (S12):** google-play-scraper 1.2.7 works against the live listing. 400 newest reviews returned with 0 duplicate ids, 0 empty texts, version present on 88.8%, developer replies on 2 of 400 (0.5%), thumbs-up above zero on 6 of 400 (1.5%), so helpful-votes are too sparse to use for prioritisation.
- **Library caveat (verified in source):** the scraper swallows request errors and returns an empty or short page with no continuation token, indistinguishable from the end of data. Ingestion therefore retries short pages and reports completeness against the listing's 23,617 text-review count.
