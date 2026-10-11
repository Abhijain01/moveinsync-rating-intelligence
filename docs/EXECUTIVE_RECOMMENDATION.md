# Raising MoveInSync's Play Store rating: what to fix, and what to do first

*Prepared by Abhishek Jain for the MoveInSync Forward Deployed Engineer case study. Employee app `com.moveinsync.ets`. Public sources only, collected 2026-10-10 to 2026-10-12. Revised after an independent review of the first draft.*

## 1. Bottom line
1. **Start with measurement, then fix stability.** The largest complaint cluster the app team can act on is *app stability* (17.7% of low-star reviews; 19.7% in the last six months). Spend the first one to two weeks on a data gate (ticket B0): Android vitals, the OTP funnel, the install-error source, location gaps and no-show events. Public reviews show symptoms, not causes.
2. **Build in this order:** B1 stability resilience (the only item that stays in the top 3 in most sensitivity trials), then a tier that is statistically tied: B3 authentication clarity, B8 skippable trip rating, B4 tracking honesty, B6 booking explanations. Add two-day diagnosis spikes for the install error (B2) and no-show handling (B5). Ticket-level specs: `docs/engineering_tickets.md`.
3. **Restart replies to low-star reviews now.** Developers replied to 97.8% of reviews in 2023, 4.3% in 2025 and 0.8% in 2026 so far (2 of 224 low-star reviews in the last 90 days). Replies that give a fix or a contact are low-cost and low-risk; their effect on ratings cannot be measured from public data, so they are not counted as a lever.
4. **About 18% of complaint reviews involve transport operations** (routing, vehicles and drivers, helpdesk; 12.6% purely operational). Hand the pure operations part to Customer Success per client; an app release will not fix it. Helpdesk reachability and driver contact are partly app features and are in the backlog (B7).
5. **No star target is promised.** Public data cannot support one (section 5). Judge each fix by the failure it targets, and read complaint rates quarterly.
6. **"How are our ratings?" is a command:** `python -m rating_intel status <snapshot>`.

## 2. What the evidence shows
Sources: all 24,314 public Play text reviews (2014-2026), the Play listing, MoveInSync's Help Center and Android documentation (`docs/source_register.md`). Analysis window 2025-10-10 to 2026-10-09: **2,856 reviews; 846 rated 1-3 stars** (the complaint pool). Counts come from a rule classifier that is approximate (precision 0.76, recall 0.65).

**Premise check.** The listing shows 4.6 stars (4.6377) from 114,855 ratings, 85.5% of them five-star. That is high in absolute terms, so "lower than it should be" probably refers to recent reviews, a higher internal target or other apps. Within the 4.6, one-star ratings (6.4% of ratings) account for **70.5% of the shortfall from 5.0**. Text reviews are a self-selected sample and look far worse (24% one-star).

| Cluster (pool = 846) | Reviews | Share, full year | Share, last six months | Who can fix it | Evidence |
|---|---|---|---|---|---|
| App stability: crash, will not open, endless loading | 150 | 17.7% (CI 15.3-20.4) | 19.7% | App + backend | Symptom high, cause low |
| Forced logout (alone) | 57 | 6.7% | 3.9% (fell from 10.3%, bursts) | Auth, session policy | Symptom high, cause low |
| OTP not arriving (alone) | 51 | 6.0% | 5.6% (flat) | OTP vendors, provisioning, auth | Symptom high, cause medium-low |
| Sign-in, either of the two | 105 | 12.4% | 9.2% | as above | |
| Tracking and ETA | 89 | 10.5% | 10.3% | Backend + driver app + app | Medium |
| Booking failures, rules, cancel/edit, addresses | 87 | 10.3% | 9.9% | App + client policy | Low-medium; probably under-counted |
| Vehicle, driver, routing | 125 | 14.8% | 15.5% | Operations, vendors | Medium; outside the app |
| Helpdesk and driver contact | 62 | 7.3% | 8.2% | Product + Operations | Medium |
| Forced rating, consent prompts, broken feedback | 46 | 5.4% | 5.4% | App | Symptom high |
| Safety mentions and boarding verification (OTP, QR, seat-belt check) | 21 + 21 | 2.5% + 2.5% | | Mixed: conduct is operations, flow is app | Medium on flow items |
| No-show handling | 21 | 2.5% | 2.1% | Product + client policy | Severe, small |
| Install / launch error, with device compatibility | 32 (25 install-error rule hits, 17 strict) | 3.8% | 6.0% | App + Security | Emerging |

Clusters overlap, so shares do not add up. "Share" is the share of the pool with at least one category in the cluster. Intervals cover sampling error only.

What else the data says:
- **70% of complaint reviews name a specific problem** (593 of 846); 19% say only "worst app".
- **App-side only 46.5%, operations only 12.6%, both 5.7%, no actionable category 29.9%.**
- **No aggregate deterioration:** one-star share 23.1% vs 24.8% between halves (p = 0.28); last 90 days vs the 90 before: mean 3.80 vs 3.83, one-star 25.0% vs 25.0%.
- **Install errors are rising.** Strict "not installed from Play Store" mentions: 1, 4, 7, 3 in Jun to Sep 2026 (2 in the first half of the window, 15 in the second; not significant on its own). After scaling for review volume and correcting for 230 month-theme tests, the install-error counts in **July (5 vs 0.35 expected) and August 2026 (9 vs 1.2 expected)** are still unusual; no other theme is. The rule over-counts slightly (25 vs 17 strict), so this is a prompt to investigate, not a measured rate.
- Version 12.19.0 (102 reviews) has 32.4% one-star vs 24.0% overall, about 2.0 standard errors, from roughly 28 versions compared, so **not evidence of a regression**. Two reviews cite Android 17 incompatibility; too few to conclude.
- **Safety:** 21 reviews mention safety, mostly driver conduct; the app-flow items are a seat-belt check covering the OTP, QR scanning blocked unless location accuracy is on, and a reviewer who could not reach SOS or driver details after being logged out. Read all safety reviews first each month.

## 3. What to do, in order
| Order | Ticket | What | Why | Owner |
|---|---|---|---|---|
| 0 | B0 | Android vitals by version and device; OTP funnel; install-error source; location gaps and ETA error; no-show events; Play Console ratings by version | Replaces guesses with numbers; decides causes | Mobile + Backend + Data |
| 1 | B1 | Timeouts, last-known-trip cache with its age, visible error with Retry | Largest cluster; mitigates the loading and network modes whichever backend cause wins. Crash and "will not open" need B0 | Mobile + Backend |
| 2 | B3 | Distinct "not registered or no subscription" vs "OTP delayed"; resend with channel switch; no logout during an active trip | Blocks use; includes a safety-relevant case; OTP complaints are stable | Auth + Mobile |
| Parallel | B8 | Make trip rating skippable; show consent once | 17 forced-rating and 18 consent reviews; cheapest change | Mobile + Product |
| Parallel | B2, B5 | Two-day diagnosis spikes: install-error source; no-show events | Severe, rising or documented-but-surprising behaviour, few reviews | Mobile + Security; Product |
| Now | B12 | Reply to 1-3 star reviews with help, never with a request to re-rate | Reply drought | Support / Product |
| After B0 | B4, B6, B10, B13 | Honest tracking; explain every booking rejection with its rule; pickup-time-change notices; boarding-flow fixes | Causes needed first (B6's explanation messages can start earlier) | Backend + Mobile |
| Hand off | B9, B7 | Operations evidence to Customer Success; scope in-app helpdesk and masked driver contact | Outside the app team | CS + Operations |

**How robust is the order?** Scoring is reach (measured, recent half) x severity x confidence x controllability / effort, with 5,000 sensitivity trials that also vary the measured reach by 0.7x-1.8x to reflect classifier error (`docs/phase5_backlog.md`). **B1 is in the top 3 in 79% of trials. B3 (45%), B8 (39%), B4 (35%) and B6 (32%) are a tie.** I put B3 next by judgement, not by score. Self-booking, the step the case calls most important, is deferred because its count is the least reliable (recall 0.25 on booking failure), not because it matters less.

## 4. How we will know it worked
- **Primary:** internal telemetry: crash and ANR rate against Google's thresholds (1.09% and 0.47% overall, 8% per phone model), OTP verified within 2 minutes, stale-location rate, reversed no-shows. Targets are set from the B0 baseline.
- **Release method:** Play staged rollout, compare old and new versions on the same days, fixed decision rule, guardrails (crash-free users, active-trip completion, no weakening of OTP security).
- **For "How are our ratings?":** Play Console ratings by version, country and date (all ratings, about five times the sample of text reviews). Public text reviews are the outside view only.
- **Secondary:** complaints per 1,000 reviews by theme, read quarterly. Baseline: stability 52.5, tracking 21.4, login 20.0, OTP 17.9.

## 5. What I will not promise
- **Reviews cannot validate a release.** Monthly one-star share varies with a standard deviation of 3.8 points (more than sampling alone would give), and with about 240 reviews a month only a swing of about 11 points is detectable (about 6 points per quarter).
- **The headline rating moves slowly, but a displayed change is possible.** The listing's mean is 4.6377 and displays as 4.6. If the display is the plain mean rounded to one decimal (unverified), it would show 4.7 after about 4,000 extra five-star ratings, or about 350 one-star ratings turning into five-star. How fast that happens depends on rating inflow, which public data does not show.
- **I do not recommend** asking only happy users to rate, incentives, or hiding negative reviews. They are dishonest and risk Google policy action. Google's in-app review guidance says not to ask opinion questions before the prompt.

## 6. Assumptions and limits
- Scope is the employee app (driver, Field and Partner apps excluded).
- Reviews are a self-selected sample, do not identify employer, city or vendor, and show symptoms, not causes. Collection used `lang=en, country=in`; I did not test other languages. The listing histogram and the review feed are not fully in sync (for example, more 2-star text reviews than 2-star ratings), so coverage is indicative only.
- The classifier is approximate. **The hand labels used to test it were produced by an AI assistant, not an independent human**; a 30-row human re-label is recommended (`docs/methodology.md`).
- Help Center and Android documentation were read from public pages (S13-S21); a documented feature may not ship or work as documented, and a single article's silence is not proof of absence. I have not seen the product, code or telemetry; effort estimates are guesses.

## 7. First five working days
- **Day 1:** pull Android vitals and the OTP log; find the install-error string in code; start replying to 1-3 star reviews.
- **Day 2:** Product and Operations review no-show events; confirm the Play Console ratings view.
- **Day 3:** decide the B1 design from the vitals; scope B8.
- **Day 4:** start B8; write B1 and B3 tickets with real estimates.
- **Day 5:** confirm B0 baselines; agree targets and guardrails; run `python -m rating_intel analyze` on a fresh snapshot to start the monthly record.

## 8. Questions for customers and the transport desk (week 1)
1. When employees say "the app is not working", which screen and which network (office Wi-Fi, mobile data)?
2. How many sign-in failures reach your desk, and are the affected numbers subscribed and registered with MoveInSync?
3. What are your booking cut-off and schedule-limit settings, and do employees know them?
4. How do you handle a no-show an employee disputes, and is approval-based restore switched on?
5. When a pickup time changes, who tells the employee, and how late before pickup?

## 9. Repeatability
One command per question: `python -m rating_intel status`, `analyze`, `compare`; `scripts/run_all.ps1` for the monthly refresh. 85 automated tests (including tests that recompute the numbers quoted here); every report carries the hashes needed to reproduce it. Repository, method and limits: `README.md`, `docs/methodology.md`.
