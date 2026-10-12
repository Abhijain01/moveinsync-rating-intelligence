# Raising MoveInSync's Play Store rating: what to fix, and what to do first

*Prepared by Abhishek Jain for the MoveInSync Forward Deployed Engineer case study. Employee app `com.moveinsync.ets`. Public sources only, collected 2026-10-10 to 2026-10-12. Revised after an independent review of the first draft.*

## 1. Bottom line
1. **Start with measurement, then fix stability.** The largest complaint cluster the app team can act on is *app stability* (17.7% of low-star reviews; 19.7% in the last six months). Spend the first one to two weeks on a data gate (ticket B0): Android vitals, the OTP funnel, the install-error source, location gaps, no-show events and the self-booking funnel. Public reviews show symptoms, not causes.
2. **Build B1 first; investigate booking from day 1.** B1 stability resilience is the strongest measured engineering candidate. B3 authentication, B8 skippable feedback, B4 tracking and B6 booking have uncertain relative ranks. B6 gets immediate funnel instrumentation and defect reproduction because self-booking creates trips and the classifier misses booking complaints. Add two-day diagnosis spikes for install errors (B2) and no-shows (B5). Ticket-level specs: `docs/engineering_tickets.md`.
3. **Restart replies to low-star reviews now.** Developers replied to 97.8% of reviews in 2023, 4.3% in 2025 and 0.8% in 2026 so far (2 of 224 low-star reviews in the last 90 days). Replies that give a fix or a contact are low-cost and low-risk; their effect on ratings cannot be measured from public data, so they are not counted as a lever.
4. **About 18% of complaint reviews touch operations-related categories.** Start B9 as a joint FDE/Customer Success, Operations and Routing Engineering workstream: incident register by day 5, a 2-4 week pilot, and missed-pickup, on-time, detour and resolution metrics. The 12.6% "operations-only" figure describes taxonomy labels, not confirmed ownership. Routing software, client policies and vendor execution need separate diagnosis; a mobile-only release will not fix every cause.
5. **No star target is promised.** Public data cannot support one (section 5). Judge each fix by the failure it targets, and read complaint rates quarterly.
6. **Credible safety failures get same-day assessment** by a named Safety lead, with mitigation/escalation. Ordinary session expiry must not interrupt a trip, while explicit logout and security revocation remain effective.
7. **"How are our ratings?" is a command:** `python -m rating_intel status <snapshot>`.

## 2. What the evidence shows
Sources: 24,314 public Play text reviews returned by the English/India collection (2014-2026), the Play listing, MoveInSync's Help Center and Android documentation (`docs/source_register.md`). Analysis window 2025-10-10 to 2026-10-09: **2,856 reviews; 846 rated 1-3 stars** (the complaint pool). Counts come from a rule classifier that is approximate (precision 0.76, recall 0.65).

**Premise check.** The collection manifest records a Play listing score of 4.637723 (displayed as 4.6), 114,857 ratings and a histogram with 85.5% five-star ratings. The earlier probe recorded 114,855 ratings; those are two different fetches. Google says the displayed rating gives more weight to recent ratings and distinguishes it from the lifetime average (S22). A lifetime-histogram calculation attributes 70.5% of the unweighted shortfall from 5.0 to one-star ratings; it does not attribute the displayed rating. The reported 4.6 is high in absolute terms; the company's target or relevant peer benchmark is unknown. Text reviews are self-selected and have 24% one-star in the analysis window.

| Cluster (pool = 846) | Reviews | Share, full year | Share, last six months | Who can fix it | Evidence |
|---|---|---|---|---|---|
| App stability: crash, will not open, endless loading | 150 | 17.7% (CI 15.3-20.4) | 19.7% | App + backend | Symptom high, cause low |
| Forced logout (alone) | 57 | 6.7% | 3.9% (fell from 10.3%, bursts) | Auth, session policy | Symptom high, cause low |
| OTP not arriving (alone) | 51 | 6.0% | 5.6% (flat) | OTP vendors, provisioning, auth | Symptom high, cause medium-low |
| Sign-in, either of the two | 105 | 12.4% | 9.2% | as above | |
| Tracking and ETA | 89 | 10.5% | 10.3% | Backend + driver app + app | Medium |
| Booking failures, rules, cancel/edit, addresses | 87 | 10.3% | 9.9% | App + client policy | Low-medium; probably under-counted |
| Vehicle, driver, routing | 125 | 14.8% | 15.5% | Routing Engineering + Operations + client policy | Cause and boundary unconfirmed |
| Helpdesk and driver contact | 62 | 7.3% | 8.2% | Product + Operations | Medium |
| Forced rating, consent prompts, broken feedback | 46 | 5.4% | 5.4% | App | Symptom high |
| Safety mentions and boarding verification (OTP, QR, seat-belt check) | 21 + 21 | 2.5% + 2.5% | | Mixed: conduct is operations, flow is app | Medium on flow items |
| No-show handling | 21 | 2.5% | 2.1% | Product + client policy | Severe, small |
| Install / launch error, with device compatibility | 32 (25 install-error rule hits, 17 strict) | 3.8% | 6.0% | App + Security | Emerging |

Clusters overlap, so shares do not add up. "Share" is the share of the pool with at least one category in the cluster. Intervals cover sampling error only.

What else the data says:
- **70% of complaint reviews name a specific problem** (593 of 846); 19% say only "worst app".
- **App-side only 46.5%, operations only 12.6%, both 5.7%, no actionable category 29.9%.**
- **No statistically detectable deterioration in the analyzed text-review windows:** one-star share 23.1% vs 24.8% between halves (p = 0.28); last 90 days vs the 90 before: mean 3.80 vs 3.83, one-star 25.0% vs 25.0%.
- **Install errors are rising.** Strict "not installed from Play Store" mentions: 1, 4, 7, 3 in Jun to Sep 2026 (2 in the first half of the window, 15 in the second; not significant on its own). After scaling for review volume and correcting for 230 month-theme tests, the install-error counts in **July (5 vs 0.35 expected) and August 2026 (9 vs 1.2 expected)** are still unusual; no other theme is. The rule over-counts slightly (25 vs 17 strict), so this is a prompt to investigate, not a measured rate.
- Version 12.19.0 (102 reviews) has 32.4% one-star vs 24.0% overall, about 2.0 standard errors, from roughly 28 versions compared, so **not evidence of a regression**. Two reviews cite Android 17 incompatibility; too few to conclude.
- **Safety:** 21 reviews mention safety, mostly driver conduct; the app-flow items are a seat-belt check covering the OTP, QR scanning blocked unless location accuracy is on, and a reviewer who could not reach SOS or driver details after being logged out. Assess credible safety failures the same day they are discovered; monthly review is supplementary.

## 3. What to do, in order
| Order | Ticket | What | Why | Owner |
|---|---|---|---|---|
| 0 | B0 | Vitals, OTP, install source, location, no-show and **booking funnel** | Data gate begins day 1; confirm causes | Mobile + Backend + Data + Product |
| 1 | B1 | Timeouts, last-known-trip cache with its age, visible error with Retry | Largest cluster; mitigates the loading and network modes whichever backend cause wins. Crash and "will not open" need B0 | Mobile + Backend |
| 2 | B3 | Clear auth states; resend/channel switch; refresh ordinary session expiry during trips | Access failures plus safety-relevant symptom; preserve revocation | Auth + Mobile + Security |
| Parallel | B8 | Make trip rating skippable; show consent once | 17 forced-rating and 18 consent reviews; cheapest change | Mobile + Product |
| Parallel | B2, B5 | Two-day diagnosis spikes: install-error source; no-show events | Severe, rising or documented-but-surprising behaviour, few reviews | Mobile + Security; Product |
| Now | B12 | Reply to 1-3 star reviews with help, never with a request to re-rate | Reply drought | Support / Product |
| After diagnosis | B4, B10, B13 | Honest tracking, pickup notices and boarding fixes; **B13 safety assessment starts immediately** | Confirm causes before wider implementation | Backend + Mobile + Safety |
| Day 1 | B6, B9, B7 | Investigate booking failures; owned commute-reliability pilot; scope helpdesk/contact | Core journey plus cross-team ownership | Product + FDE/CS + Routing Engineering + Operations |

**How robust is the order?** The existing scoring model uses recent measured reach x severity x confidence x controllability / effort with 5,000 sensitivity trials. B1 reaches the top 3 in 79% of trials; B3 45%, B8 39%, B4 35%, B6 32%. These are model outcomes under chosen perturbations, not probabilities of true priority or a formal statistical tie. Keep the measured scores unchanged; override investigation timing for self-booking, cross-team commute failures and safety. Booking recall 0.25 is based on four gold examples and cannot justify postponement. Ranking an app-team queue is not ranking all company actions.

## 4. How we will know it worked
- **Primary:** internal telemetry: crash and ANR rate against Google's thresholds (1.09% and 0.47% overall, 8% per phone model), OTP verified within 2 minutes, stale-location rate, reversed no-shows, booking success after policy validation, and B9 missed-pickup/on-time/detour/resolution metrics. Targets are set from the B0 baseline.
- **Release method:** Play staged rollout, same-day comparisons adjusted for device/client/update differences (randomized where feasible), fixed decision rule, guardrails (crash-free users, active-trip completion, no weakening of OTP security).
- **For "How are our ratings?":** Play Console ratings by version, country and date (all ratings, about five times the sample of text reviews). Public text reviews are the outside view only.
- **Secondary:** complaints per 1,000 reviews by theme, read quarterly. Baseline: stability 52.5, tracking 21.4, login 20.0, OTP 17.9.

## 5. What I will not promise
- **Reviews cannot validate a release.** Monthly one-star share varies with a standard deviation of 3.8 points (more than sampling alone would give), and with about 240 reviews a month only a swing of about 11 points is detectable (about 6 points per quarter).
- **The displayed rating is not a lifetime arithmetic mean.** Google weights recent ratings (S22). Public data does not reveal enough about the weighting or future inflow to estimate how many new or changed ratings would produce 4.7. Track the actual Play Console rating alongside recent rating distributions; no lift is forecast.
- **I do not recommend** asking only happy users to rate, incentives, or hiding negative reviews. They are dishonest and risk Google policy action. Google's in-app review guidance says not to ask opinion questions before the prompt.

## 6. Assumptions and limits
- Scope is the employee app (driver, Field and Partner apps excluded).
- Reviews are a self-selected sample, do not identify employer, city or vendor, and show symptoms, not causes. Collection used `lang=en, country=in`; I did not test other languages. The listing histogram and the review feed are not fully in sync (for example, more 2-star text reviews than 2-star ratings), so coverage is indicative only.
- The classifier is approximate. The original validation labels were AI-produced. A completed 30-review human spot check gave human-vs-AI F1 0.84 and human-vs-rule F1 0.67; 13 labels involved AI-assisted mapping to category IDs, so the check was not fully blind or independent. See `docs/methodology.md` and `reports/phase3/human_agreement.md`.
- Help Center and Android documentation were read from public pages (S13-S21); a documented feature may not ship or work as documented, and a single article's silence is not proof of absence. I have not seen the product, code or telemetry; effort estimates are guesses.

## 7. First five working days
- **Day 1:** pull vitals/OTP logs; instrument booking attempts through confirmation; find the install-error source; name the B9 coordinator and Safety lead; assess credible SOS/boarding failures; start helpful replies.
- **Day 2:** reproduce wrong-date, duplicate and disabled-booking reports; review no-show events; split B9 incidents into software, policy and vendor causes; confirm Play Console rating views.
- **Day 3:** decide the B1 design from the vitals; scope B8.
- **Day 4:** start B8; write B1 and B3 tickets with real estimates.
- **Day 5:** publish B0 baselines including booking; publish B9 incident owners/actions/dates; agree targets and guardrails; run the bundled snapshot demo to establish the repeatable record.

## 8. Questions for customers and the transport desk (week 1)
1. When employees say "the app is not working", which screen and which network (office Wi-Fi, mobile data)?
2. How many sign-in failures reach your desk, and are the affected numbers subscribed and registered with MoveInSync?
3. What are your booking cut-off and schedule-limit settings, and do employees know them?
4. How do you handle a no-show an employee disputes, and is approval-based restore switched on?
5. When a pickup time changes, who tells the employee, and how late before pickup?

## 9. Repeatability
One command per question: `python -m rating_intel status`, `analyze`, `compare`; `scripts/run_all.ps1` for the monthly refresh. 85 automated tests passed with zero skips on the supplied snapshot (including tests that recompute the numbers quoted here); use `python scripts/demo.py` for offline reproduction; every report carries the hashes needed to reproduce it. Repository, method and limits: `README.md`, `docs/methodology.md`.
