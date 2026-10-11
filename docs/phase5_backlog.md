# Phase 5: Prioritization model and engineering backlog (revised 2026-10-11 after independent review)

Tags: **[F]** observed fact, **[Q]** quantitative finding, **[I]** inference, **[H]** hypothesis, **[R]** recommendation.

## 1. Recommendation in one paragraph [R]
Start with a **one-to-two-week instrumentation gate (B0)**, then build **B1 (stability resilience)**. B1 is the only item that stays in the top 3 in more than half of the sensitivity trials. After B1, the next tier is **statistically a tie**: B3 (authentication clarity), B8 (skippable rating), B4 (tracking honesty) and B6 (booking explanations) each land in the top 3 in 32-45% of trials. I put **B3 first among them by judgement, not by score**, because it blocks use of the app, includes a safety-relevant case, and its OTP part is stable over time; B8 is done in parallel because it is the cheapest. Install error (B2) and no-show (B5) get short diagnosis spikes. **No rating lift is promised.**

## 2. Scoring model (inputs: `docs/backlog_inputs.csv`; code: `scripts/prioritize.py`)
`Score = Reach% x Severity x Confidence x Controllability / Effort`

| Factor | Source | Meaning |
|---|---|---|
| Reach % | **Measured** | Share of the 1-3 star pool with at least one of the item's categories (union, no double counting), taken from the **recent half of the window** (from 2026-04-10, n = 466) so that a burst that has faded does not inflate an item. The full-year reach is shown beside it. Approximate: classifier precision is about 0.76 and recall about 0.65. |
| Severity 1-3 | Judgement | 3 blocks use of the service, 2 degrades it, 1 annoyance. |
| Confidence 1-3 | Judgement | 3 cause evidenced, 2 symptom clear and cause open, 1 weak or not yet investigated. |
| Controllability 1-3 | Judgement | 3 the app team alone, 2 needs another team, a vendor or a client, 1 mostly outside the app. |
| Effort 1-3 | **Analyst guess** | S/M/L; Engineering must replace it. |

**Sensitivity test (5,000 trials).** Each judgement factor moves by -1, 0 or +1 (kept within 1-3), and each item's measured reach is multiplied by a random factor between 0.7 and 1.8 (precision below 1 can shrink a count; recall as low as 0.2-0.6 on small categories can enlarge it). The rank of every item is recorded.

## 3. Result [Q]
| Rank | ID | Item | Reach % recent half | Reach % full year | Score | Median rank | Rank range | % of trials in top 3 |
|---|---|---|---|---|---|---|---|---|
| 1 | B1 | Stability resilience | 19.7 | 17.7 | 118.2 | 2 | 1-12 | 79 |
| 2 | B8 | Skippable trip rating, consent once | 5.4 | 5.4 | 64.8 | 4 | 1-12 | 39 |
| 3 | B3 | Authentication clarity | 9.2 | 12.4 | 55.2 | 4 | 1-12 | 45 |
| 4 | B4 | Tracking honesty | 10.3 | 10.5 | 41.2 | 5 | 1-12 | 35 |
| 5 | B6 | Booking rule explanations | 9.9 | 10.3 | 29.7 | 5 | 1-12 | 32 |
| 6 | B10 | Notifications, pickup-time changes | 4.5 | 3.9 | 27.0 | 7 | 1-12 | 13 |
| 7 | B7 | In-app helpdesk + driver contact | 8.2 | 7.3 | 21.9 | 8 | 1-12 | 13 |
| 8 | B13 | Boarding and safety-check flow | 5.2 | 5.0 | 20.8 | 8 | 1-12 | 11 |
| 9 | B2 | Install/launch error | 6.0 | 3.8 | 18.0 | 8 | 1-12 | 12 |
| 10 | B11 | UI/usability triage | 8.6 | 10.3 | 12.9 | 8 | 1-12 | 11 |
| 11 | B5 | No-show transparency | 2.1 | 2.5 | 12.6 | 11 | 1-12 | 3 |
| 12 | B9 | Operations (routing, vehicles) | 15.5 | 14.8 | 10.3 | 8 | 1-12 | 8 |

**How to read this honestly:**
- [Q] Only **B1** is robust (top 3 in 79% of trials). Every item has a rank range of 1-12 under the noise. **Do not defend any order below the first place.**
- [I] B8 ranks high because its effort is guessed as small; its reach is 5.4% and its effect on Play ratings is unmeasurable. It is a cheap usability fix, not a rating lever.
- [I] **B3**: forced-logout complaints fell from 10.3% to 3.9% of the pool between halves while OTP complaints stayed flat (6.6% to 5.6%), so its recent reach (9.2%) is lower than the full-year 12.4%. That drop is why B3 is no longer a clear second.
- [I] **B9** (operations) has the highest reach after B1 (15.5% recent) but scores last because the app team cannot control it. It is a customer-success matter, not a mobile ticket.
- [I] The multiplicative formula undervalues rare but severe problems (B2, B5, B13); that is why they get diagnosis spikes or small tickets.
- [I] B6 (booking) is the step the case calls most important. It is deferred to after B0 because its count is the least reliable (classifier recall 0.25 on booking failure in the frozen test, so its reach is probably higher) and because the mix of client-configured rules and genuine defects is unknown. Its first step (explain every rejection with the rule) can start before B0 completes if Product wants it.
- B10, B11 and B13 were not investigated at register depth; their confidence is 1.

## 4. Backlog
Ticket-level specs (evidence, scope, acceptance criteria, telemetry, guardrails): `docs/engineering_tickets.md`.

### B0. Instrumentation and data gate (not scored; do first; guess S, 1-2 weeks)
Android vitals by version and device against Google's thresholds (1.09% crash, 0.47% ANR of daily active users; 8% for one device model); OTP funnel by channel, provider and client; the install-error string and its source; location ping gaps and ETA error; no-show events. Done when each of R1-R5 has a number that confirms or rejects its leading hypothesis. Also pull **Play Console ratings by version and date**: as the owner MoveInSync sees all ratings, a sample about five times larger than the text reviews, and it should be the primary answer to "How are our ratings?".

### B1. Stability resilience (rank 1; guess M)
150 reviews, 17.7% of the pool (19.7% in the recent half). **Scope: mitigate the network and loading modes** (timeouts, last-known-trip cache with its age, visible error with Retry). This helps whichever backend cause is behind slow loading or "no network" complaints. It does **not** address the "will not open" (18% of the cluster) or crash (13%) modes, which need B0 (crash logs and vitals). Controllability is scored 2 because the backend is involved.

### B3. Authentication clarity (guess M)
Forced logout 57 and OTP 51 (union 105; 9.2% recent, 12.4% full year). Distinct messages for "not registered or no subscription" and "OTP delayed"; resend with channel switch; silent session refresh; no logout during an active trip. The SOS acceptance criterion rests on a single review and should be checked with the team.

### B8. Skippable trip rating, consent shown once (guess S)
Forced rating 17, consent 18, broken feedback flow 13. **Hard rule:** do not route users to the Play Store, do not use the Play in-app review prompt as a gate, do not steer toward 5 stars.

### B4, B6, B10, B7, B13, B11 (ranks 4-10)
- **B4 Tracking honesty:** "last updated hh:mm", stale pin state, smoothed ETA. Needs B0 item 4 to find the cause (driver app, ingestion or ETA model).
- **B6 Booking:** show the rule behind every rejection; fix wrong-date, duplicate and disabled-button defects separately.
- **B10 Notifications and pickup-time-change communication:** 33 notification reviews, plus pickup-time-change complaints inside the ETA category.
- **B7 In-app helpdesk and masked driver contact:** the Help Center article on the communication interface describes admin-to-user messaging only and does not mention employee-to-driver contact; 20 reviews ask for it. The article's silence does not prove the product has no such feature, so treat as a gap to confirm.
- **B13 Boarding and safety-check flow:** boarding-verification complaints (21) and safety mentions (21): seat-belt check covering the OTP, QR scan blocked by location accuracy, QR scan not clearing a no-show.
- **B11 UI/usability:** triage 59 UI reviews and 33 feature requests with Design.

### B5. No-show handling: diagnosis spike (rank 11; guess S to M)
21 reviews, all rated 1-2 stars. The Help Center no-show enforcement guide documents the rules: configurable warning and enforcement thresholds, a 30-minute alternate-transport filter, cancellation of the logout trip after a login no-show, email and in-app notifications, and an **optional approval-based restore request raised from the app (off by default)**. It describes no way to contest a no-show that was recorded in error. Spike: measure how many no-shows carry a QR or OTP event or were later reversed (B0 item 5), then decide.

### B2. Install and launch error: diagnosis spike (rank 9; guess S)
Strict-phrase mentions by month: Jun 1, Jul 4, Aug 7, Sep 3. The rule-based count for July and August 2026 is also **statistically unusual after normalising for volume and correcting for multiple tests** (`spikes.csv`). Spike: find where the error string comes from (**Confirm in code**), read any integrity-check verdicts, test on Android 17. Close the ticket if the check is not in the app.

### B12. Reply to low-star reviews (not scored; start now)
Developers replied to 97.8% of reviews in 2023, 4.3% in 2025 and 0.8% in 2026 to date (all reviews; 2 of 224 low-star reviews in the last 90 days). Replies name a fix, a workaround or where to get help, never ask for a re-rating and are not sent to only some star levels. Effect on ratings is unmeasurable from public data.

### B9. Operations (not an engineering ticket)
Routing 70 and vehicle/driver 70 reviews. Hand the evidence to Customer Success per client.

## 5. Sequence [R]
1. **Weeks 1-2:** B0 gate in parallel with B8 and the B2 and B5 diagnosis spikes; B12 starts at once.
2. **Weeks 2-6:** B1 build (network and loading modes first), B3 design and build, informed by B0.
3. **After B0 confirms causes:** B4, B6 (the B6 explanation messages can start earlier), B13.
4. **Hand off:** B9 to account owners; scope B7 with Operations.
Revisit the order after B1 and B3 with real effort estimates and B0 data.

## 6. Ethics and limits
- No item involves asking for ratings, selective prompting or hiding negative reviews.
- Reach comes from a self-selected sample and an approximate classifier; severity, confidence, controllability and effort are judgements.
- The model ranks **what to look at first**, not expected star gain.
- Reproduce: `python scripts\prioritize.py data\processed\run_20261010T203205Z\reviews_clean.csv --since 2025-10-10 --out reports\phase5`
