# Engineering tickets (ready to copy into Jira or Linear)

Each ticket states the evidence, scope, testable acceptance criteria, telemetry, open questions and what would stop it. Review IDs are Google Play review IDs from the public corpus, so every claim can be opened and checked (`reports/phase3/evidence_2025-10-10.csv` and `docs/phase4_root_cause_register.md`). Effort is the analyst's guess and must be replaced by the team. Anything that depends on the code base is marked **Confirm in code**.

Ordering and rationale: `docs/phase5_backlog.md`.

---
## B0. Instrumentation and data gate (start day 1; target 1-2 weeks, effort to confirm)
**Problem.** Public reviews show symptoms only. Causes of B1 to B5 are unknown.
**Do.**
1. Export Play Console Android vitals: user-perceived crash rate and ANR rate by app version and device model, for the last 90 days, against Google's bad-behaviour thresholds (1.09% crash, 0.47% ANR of daily active users; 8% for any single device model).
2. Build an OTP funnel: requested, sent, provider-delivered, entered, verified, by channel (SMS, WhatsApp, other), provider and client company, per day.
3. Log the exact text and code path of the "not installed from Play Store" style error (**Confirm in code** whether it comes from an installer-source, licence or integrity check).
4. Log driver location ping gaps (device time vs server receive time) and the ETA shown at 15, 10 and 5 minutes before actual arrival.
5. Record each no-show event: who marked it (system or driver), timestamp, GPS distance of the employee from pickup, QR/OTP events, and any later reversal.
6. Instrument the self-booking funnel: attempt, validation, request submitted, booking created, confirmation displayed; correlation ID, failure reason, latency, client policy and app version. Distinguish technical failure from a valid policy rejection. Product + Backend + Mobile own it.
7. Safety lead and Mobile assess credible SOS/boarding failures the same day they are discovered; preserve evidence, reproduce if possible and record mitigation/escalation. Public review IDs cannot identify a client or trip by themselves.
**Acceptance.** For each of B1 to B6 a one-page note with the number and the decision it supports. A dashboard or saved query exists for every metric so it can be re-read monthly.
**Guardrail.** No personal data beyond what the product already stores.

---
## B1. Stability resilience (est. M)
**Evidence.** 150 of 846 low-star reviews (17.7%). Examples: `fcc2d2dc-7c99-4de7-adb0-21d43f8445a2` (works on mobile data but not on office Wi-Fi), `93f3c4e5-dc0d-4543-8568-16c9b40c9216` (keeps loading on good internet), `2b0213c8-2dfe-4116-aecc-a27929059916` (shows "no network" while stable), `4cffdcf2-c19c-4563-b399-0812472c79fd` ("Something went wrong" after login).
**Scope (mitigates the network and loading modes whichever backend cause wins; does not address the "will not open" and crash modes, 18% and 13% of this cluster, which need B0 crash logs and vitals).**
- Set explicit timeouts on every call that blocks the home or trip screen (**Confirm in code** which calls block).
- Cache the last-known trip and show it with its age while a refresh runs.
- Replace endless spinners with an error that names the failing step and offers Retry.
- Do not require a network call at every cold start where cached data is enough.
**Out of scope.** Backend latency work until B0 shows it is the cause.
**Acceptance (Given/When/Then).**
- Given airplane mode or a blocked API domain, when the app opens, then the cached trip shows with "updated hh:mm" within 3 seconds, or a clear error with Retry; never a blank screen.
- Given a call that hangs, then the timeout fires and the UI leaves the loading state.
- Given a cancelled trip on the server, then a cached trip is marked stale and not shown as active.
**Telemetry.** Cold-start p50/p95; share of sessions that end on a loading state; crash-free users; ANR rate.
**Guardrails.** No increase in stale-data errors; crash-free users do not fall.
**Tests.** Network-emulation suite (slow, offline, blocked domain, DNS failure); cold start with an expired token; launch on the newest Android release in the device farm.

---
## B3. Authentication clarity and sessions (est. M)
**Evidence.** Forced logout 57 reviews (fell from 10.3% to 3.9% of the pool between halves, arrives in bursts) and OTP 51 (flat, 6.6% to 5.6%); union 105, 12.4% of the year and 9.2% of the last six months. `6855f79d-f54e-4ce7-9a7f-213677cec9d1` (logged out every 5-10 minutes and cannot reach SOS/driver details), `3e16be2c-e24e-4ef1-a5e4-c0f8ba9aad24` (OTP after 15 minutes), `57cbaf15-e6aa-4fb5-bb89-07737777a6de` (no OTP on any channel, about 50 attempts), `3e3d8c85-29ba-4636-bb62-ecaf17ffb6c9` (no message whether the number is registered).
**Scope.**
- Show distinct states: "number not registered / not assigned to a company" vs "OTP sent, may be delayed" vs "too many attempts, try after hh:mm".
- Resend with a visible cooldown and a switch of channel.
- Refresh ordinary session expiry before it interrupts an active trip. Explicit user logout, account revocation and security termination still take effect. Keep an approved emergency-contact path available after authentication loss; do not expose private trip details without authorization.
**Out of scope.** Changing OTP security strength without Security's approval.
**Acceptance.**
- Given an unregistered number, then the message says so and names the next step (contact your transport desk).
- Given an active trip and ordinary token expiry, refresh without interrupting authorized trip access. Given a revoked account or token, enforce revocation and offer the approved emergency-contact path without disclosing protected trip data.
- Given the OTP is delayed beyond the stated time, then Resend and Switch channel are offered.
**Telemetry.** OTP verified within 2 minutes; unrequested logouts per active user per week; rate-limit lockouts.
**Guardrails.** Account-takeover and OTP-abuse indicators must not worsen; Security reviews any session-length change.
**Open questions.** Who owns each OTP provider? Is session length set per client company?

---
## B8. Skippable trip rating and consent shown once (est. S)
**Evidence.** Forced rating 17, consent and permission prompts 18, broken feedback flow 13. `f9fce9fe-8115-4a30-8d09-d8bdac76837d` (forced rating after every ride), `323f395e-0632-4d4c-9174-5df4d7828680` (trip details blocked until the previous ride is reviewed), `7f43a5e3-e153-46e1-ad4c-fbd83ca2e3f7` (feedback not accepted until 5 stars), `cbd1a2d1-080c-4b9f-a54e-eb42ce163cc4` (policy accepted 500 times).
**Scope.** Trip rating is optional with a visible Skip; trip details never wait for a rating; consent shown once per policy version; ask for a permission only when its feature is used.
**Hard rule.** Do not route users to the Play Store, do not use the Play in-app review prompt as a gate, and do not steer toward 5 stars. This ticket removes friction only.
**Acceptance.** Trip details open with the rating skipped; a rating of any value is accepted with or without comment; consent does not reappear until the policy version changes.
**Telemetry.** Share of trips where details open without rating; consent re-prompts per user.

---
## B2. Install and launch error: diagnosis spike (est. S, 2 days)
**Evidence.** Strict-phrase hits: 2 in the first half of the window, 15 in the second (not significant on its own, uncorrected p = 0.0055); monthly strict hits Jun 1, Jul 4, Aug 7, Sep 3. The pipeline's spike detector flags install-error counts in July (5 vs 0.35 expected) and August 2026 (9 vs 1.2 expected) as unusual even after scaling for volume and correcting for multiple tests. `341feb49-ec55-4cca-b783-64699751ab75` (error after 48 hours), `3e08397b-6e7b-4b3e-8146-4a7c1f1c690f` (auto-update then no launch), `c349d5f4-65c1-444a-aa69-670da8eebaeb` (reinstalled 10 times in 3 weeks); Android 17 reports `bd2d3dd2-2098-443e-8594-cd31210aa22b`, `7781ccc3-e390-49cb-b574-fb3213c2e74a`.
**Do.** Find where the error string is raised (**Confirm in code**). If it is an installer-source, licence or integrity check, read its verdict distribution by version, device, work-profile flag and installer package. Check crash reports on Android 17.
**Fix direction if confirmed.** Fail soft: allow with a server-side flag and a retry instead of a hard block; get Security's agreement first.
**Stop condition.** If the check is not in the app, close the ticket and link the evidence.
**Acceptance.** A written finding with the numbers and a decision (fix, monitor or close).

---
## B5. No-show handling: diagnosis spike, then fix (est. S to M)
**Evidence.** 21 reviews, 86% one-star. `0b1041ae-ce09-4947-b5f9-744e9014a639` (logout trip auto-cancelled after a login no-show), `697e4173-bc7e-42a3-b56d-75a9db00a95f` (QR scanned but still marked no-show), `3c7c35b4-2246-4782-9a47-79a9470db2bb` (stale banner a year later), `5427eb1d-476f-4f56-b70a-79a90e2a9135` (marked no-show 500 m away). The Help Center (S6, S17) documents system and driver marking, configurable warning and enforcement thresholds, a 30-minute alternate-transport filter, cancellation of the logout trip after a login no-show, and an optional approval-based restore request (off by default); it describes no way to contest a no-show recorded in error.
**Do.** From B0 item 5, measure how many no-shows have a QR or OTP event, were marked by the driver, or were reversed.
**Scope if confirmed.** Check that the warning before the logout trip is cancelled reaches the user in time (the guide says notifications exist; the auto-cancel itself is documented behaviour); show who marked the no-show and when; add a way to contest a mistaken mark; clear stale banners when state changes. Penalty rules belong to each client.
**Acceptance.** A trip with a recorded QR scan never ends as no-show; a cancelled trip clears its flags.

---
## B4. Tracking honesty (est. M; after B0 item 4)
**Evidence.** Tracking 61 and ETA 43 reviews (union 89). `5d14e08b-ceb3-4849-8e3b-2b94f6f06a07` (location stuck 30 minutes), `ccba873d-c5c1-4c86-808d-d0b5885f1113` (location one or two hours old), `79708a81-7362-4207-be30-f7817b66eb16` (ETA jumps from 5 to 30 minutes).
**Scope.** Show "last updated hh:mm"; grey out a pin older than a set limit; smooth ETA changes; alert operations when a vehicle goes silent. The cause may sit in the driver app or ingestion.
**Acceptance.** A pin older than the limit is visibly stale; the displayed ETA does not rise and fall more than a set amount between refreshes.

---
## B6. Self-booking: investigate day 1, explain rejections and fix confirmed defects (est. M)
**Evidence.** Booking failure 43, rules 18, cancel/edit 23, address 16 (probably under-counted). `621969c8-9e70-4e8c-80db-def46b641121` (Book now disabled), `0b11d7d5-f655-4951-855e-710761f2552e` (wrong dates created), `b0d942c2-6bbe-4c1d-a158-9167965eda3d` (duplicate schedule), `aadeb072-3a5b-43d9-a4a5-c8459716cc9b` (8-hour cut-off).
**Owner and first-week work.** Product + Backend + Mobile. Days 1-2: instrument the B0 booking funnel and reproduce disabled booking, wrong-date and duplicate-schedule reports. By day 5: publish outcomes by failure reason/client policy and decide each confirmed defect. Manually inspect booking/address-related complaints and a fresh sample of unclassified low-star reviews; recall 0.25 is based on only four gold booking examples and does not justify postponing investigation.
**Scope.** Every rejection shows its reason and next step; client-policy rejections show the configured limit. Fix confirmed wrong-date, duplicate and disabled-button defects separately. Do not override client policy without the client's agreement.
**Acceptance.** Each funnel attempt reaches a recorded terminal outcome (confirmed booking, valid policy rejection or technical failure), linked by correlation ID. No rejection without a safe reason and next step shown; retries cannot create duplicate schedules; dates follow the client's timezone across midnight. Confirmed defects have reproducible before/after tests.
**Telemetry.** Technical booking-success rate = confirmed bookings / attempts passing policy validation; policy-rejection rate by reason; confirmation p95; duplicate rate. Define abandoned attempts and timeout thresholds before rollout.
**Guardrails.** No increased duplicate trips, unauthorized bookings or policy bypass. Targets set from B0.

---
## B12. Reply to low-star reviews (no engineering; start now)
**Evidence.** 30 of 846 low-star reviews have a reply in the window; 2 of 224 in the last 90 days. Reply rate for all reviews: 97.8% in 2023, 4.3% in 2025, 0.8% in 2026 so far.
**Do.** Triage rule: sign-in or OTP, install, tracking, no-show, other. Each reply names a fix, a workaround or where to get help.
**Hard rule.** Never ask for a re-rating, never offer anything for one, never reply only to some stars.
**Measure.** Reply rate and time to reply. Effect on ratings is not measurable from public data.

---
## Cross-team workstreams
## B9. Commute reliability across Product and Operations (start day 1)
**Evidence.** Routing and vehicle/driver categories cover 125 low-star reviews (14.8%); the reviews do not identify client, city, vendor or a confirmed cause.
**Accountable owner.** FDE / Customer Success lead coordinates; Operations owns fleet and conduct; Product + Routing Engineering own planner behavior and route constraints. Name an individual at kickoff.
**Days 1-2.** Read evidence with the transport desk; select consenting pilot clients from internal incident records. Classify causes as routing software, client policy, fleet capacity, vendor execution, driver conduct or unresolved. Do not infer client identity from public review text.
**By day 5.** Produce an incident register with internal trip reference, cause/hypothesis, responsible team, next action, due date and escalation path. Reproduce routing defects using planned vs actual route/arrival data. Separate excessive detours from contractual pooling rules.
**Weeks 2-4.** Run an agreed pilot: address confirmed routing defects, late vehicle allocation or driver/vendor issues; review weekly with the transport desk and track closure.
**Acceptance.** Every pilot incident has an owner and due date; each confirmed cause has a corrective action and before/after metric. Safety incidents use immediate assessment, not this weekly cadence.
**Metrics.** Missed pickups per 1,000 scheduled pickups; on-time pickup share against client SLA; p95 planned-vs-actual trip duration; excess detour against agreed route constraints; median resolution time and repeat-incident rate. Set targets from the pilot baseline.
**Guardrails.** No worsening of safety, shift arrival, access or contractual requirements. Expand only if the pilot improves its agreed metric without guardrail regression.

## B7. Support and driver contact: scope with Operations
- **B7 In-app helpdesk and masked driver call:** scope with Operations; the Help Center's communication-interface article (S15) describes admin-to-user messages only and does not mention employee-to-driver contact (its silence does not prove there is none; confirm in the product). 20 reviews ask for driver contact.

---
## B10. Notifications and pickup-time changes (est. M; after B0)
**Evidence.** Notifications 33 reviews (3.9%); pickup-time complaints sit inside the ETA cluster. `ce4add6a-5cf6-4c6f-854d-bd4e29c1e07d` (pickup at 4:30 for a 6:00 shift), `fde3c41e-ceff-46a0-99d3-2b69c23e6ead` (pickup time changed in the middle of the night), `f5347b3d-f7ab-405d-a482-bae26ecd5368` (pickup times change constantly), `7e184ad5-066a-4d36-b7a0-73a0a56bf8a3` (asks for a check-in reminder when the vehicle passes the pickup point).
**Do.** Log every pickup-time change (how late before pickup, how often per trip) and notification send and delivery times.
**Scope if confirmed.** Notify every pickup-time change with the new time and the reason; add the check-in reminder as an option (the documented "Schedule reminder notification", S18, is a different feature; confirm in the product).
**Acceptance.** Every pickup-time change produces a notification within a set time; a late change shows its reason.

---
## B13. Boarding and safety-check flow (same-day assessment; remediation after diagnosis)
**Evidence.** Boarding verification 21 reviews and safety mentions 21 (many of the latter are driver conduct, which is operations). App-flow items: `e12ed49a-d376-4cf2-9cfd-45cae0162feb` (seat-belt check covers the OTP), `e67fc7c5-d776-4653-b0ae-478a12216067` (seat-belt option), `fd4e8200-294d-4877-b4f5-b1e12528ce8d` (QR scan blocked unless location accuracy is on), `008ae233-9d63-4c46-a472-957a59ab89ea` (cannot scan QR), `3dd690b4-b55f-433c-8a86-1497f0ef0439` (driver PIN does not work), `31f0d5ae-8046-43d7-9e34-8de9408e91a2` (no way to call in an emergency).
**Do.** Boarding funnel (OTP shown, seat-belt confirmed, boarded) with drop-off per step; QR scan failure rate by device and location-accuracy setting.
**Scope if confirmed.** The OTP stays visible whatever other prompt appears; location-accuracy requirements explain themselves and offer a fallback; SOS reachable on every screen.
**Acceptance.** On the boarding screen the OTP, seat-belt prompt and SOS are all visible without scrolling on the smallest supported screen.
**Rule.** Safety lead assesses credible SOS/boarding/driver-safety complaints the same day they are discovered. Record severity, response owner, reproduction evidence and mitigation or escalation. Product Support checks new reviews each working day; the monthly pipeline is supplementary and must not be the only safety channel. Do not wait for complaint-volume significance to act on a reproducible safety failure.
