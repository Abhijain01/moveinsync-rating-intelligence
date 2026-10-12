# Phase 4: Root-cause hypothesis register (2026-10-11)

Tags: **[F]** observed fact, **[Q]** quantitative finding, **[I]** inference, **[H]** hypothesis needing validation, **[R]** recommendation.

**Read this first.** Public reviews show *symptoms*. They cannot show *causes*. Every "cause" below is a hypothesis, ranked by how well public evidence supports it, together with the internal data that would confirm or kill it. Nothing here claims MoveInSync's internal state. Counts come from the Phase 3 rule classifier (precision about 0.76, recall about 0.65), so they are **approximate and can be over- or under-estimated**. Denominator for every share: POOL = 846 reviews rated 1-3 stars, window 2025-10-10 to 2026-10-09, unless stated.

Sources: Phase 3 outputs (`reports/phase3/`), `docs/source_register.md` (S1-S21: Play listing, MoveInSync Help Center articles, Android developer documentation). Where a Help Center statement is used it is marked "documented". A review ID is given for every review-based claim so it can be opened and checked.

## How each entry is structured
Symptom, user impact, evidence (n, share, trend, review IDs), feature check, competing explanations, likely system boundary, discriminating evidence (internal), proposed fix, regression test, confidence.

**Feature check (four levels):** (1) documented, (2) shipped, (3) works reliably, (4) customers still complain. Public data can establish 1 (Help Center) and 4 (reviews). Levels 2 and 3 need the app and telemetry, so they stay **unverified** unless stated.

---

## R1. App will not open / endless loading / generic "not working" (CRASH_LOAD_PERF)
- **Symptom.** [Q] 150 of 846 (17.7%, CI 15.3-20.4); 136 of them are 1-2 star. Share H1 15.3% -> H2 19.7% (p = 0.09, not significant). 65% name a mode (slow/loading 27%, will not open 18%, crash 13%, server error 11%, hang 4%; overlapping); 37% say only "not working".
- **User impact.** [I] The employee cannot see or confirm a ride. For a shift commute this is the highest-cost failure.
- **Evidence (review IDs).** Works only on mobile data, not Airtel Wi-Fi: `fcc2d2dc-7c99-4de7-adb0-21d43f8445a2`. Keeps loading on good internet: `93f3c4e5-dc0d-4543-8568-16c9b40c9216`. "No network" though stable: `2b0213c8-2dfe-4116-aecc-a27929059916`. "Something went wrong" after official-ID login: `4cffdcf2-c19c-4563-b399-0812472c79fd`.
- **Feature check.** Level 4 only. [F] The Help Center article "Mobile App Issues" (S14, modified 14 May 2025) lists clearing the cache, updating and reinstalling as fixes for crashes and for an app that will not launch or is stuck loading, and switching between Wi-Fi and mobile data for network problems. [I] That suggests client-state and network-path problems are known to support teams; it is not evidence of their frequency.
- **Competing explanations.** (a) Backend latency/timeouts at peak times. (b) Client network handling (the Wi-Fi vs mobile-data review points at network path, proxy, DNS or captive-portal handling, or at corporate Wi-Fi blocking a domain). (c) Device/OS fragmentation, including Android 17 (R2). (d) Corrupt local state after update. (e) Server-side feature-flag/config failure per client.
- **System boundary.** Client app + API gateway + network path. Not separable from reviews.
- **Discriminating evidence (internal).** Android vitals crash rate and ANR rate by version and device against Google's bad-behaviour thresholds (1.09% crash, 0.47% ANR of daily active users; 8% on a single device model); cold-start time p50/p95; API error rate and p95 latency by endpoint and hour; failure rate by network type / ASN; share of sessions ending at a blank or spinner state.
- **Proposed fix.** Instrument first. Then: timeouts with cached last-known trip view, visible error state with retry, and a single-screen "connection diagnostics" message naming the failing call.
- **Regression test.** Throttled-network and blocked-domain emulation; cold start with expired token; launch on the current Android release in CI device farm.
- **Confidence.** High that this is the largest single *reported* cluster; **low** on cause until vitals are read.

## R2. Install / launch error "not installed from Play Store" and Android 17 (INSTALL_ERROR, DEVICE_COMPAT)
- **Symptom.** [Q] Strict phrasing: 17 hits (rule overcounts to 25); 2 in H1, 15 in H2 (0.5% -> 3.2% of POOL), uncorrected p = 0.0055, **does not pass** the multiple-testing line (0.002). Monthly strict hits Jun 1, Jul 4, Aug 7, Sep 3. DEVICE_COMPAT 8 hits, 7 of them since July.
- **User impact.** [I] Total loss of access, repeated every few days according to reviewers; some report reinstalling 10 times.
- **Evidence.** After 48 hours: `341feb49-ec55-4cca-b783-64699751ab75` (12.16.1). Auto-update then no launch: `3e08397b-6e7b-4b3e-8146-4a7c1f1c690f` (12.16.0). Reinstalled 10 times in 3 weeks: `c349d5f4-65c1-444a-aa69-670da8eebaeb`. Android 17: `bd2d3dd2-2098-443e-8594-cd31210aa22b` (12.18.1), `7781ccc3-e390-49cb-b574-fb3213c2e74a` (Pixel 8, 12.19.0).
- **Competing explanations.** (a) A client-side installer-source or licence check failing for legitimate Play installs (Google's Play Integrity "unlicensed" verdict and the GET_LICENSED dialog exist for exactly this kind of check; whether MoveInSync uses them is **unknown**). (b) Work-profile or managed-device installs reporting a different installer. (c) Interrupted or partial auto-update. (d) Signature/integrity mismatch after update. (e) Genuine side-loaded copies (some reports may be legitimate blocks).
- **System boundary.** Client integrity check + Play distribution. Spread across versions 12.15-12.19 and 11.0.2, so **not one bad build** [F].
- **Discriminating evidence.** The exact error string and its source in the code; verdict distribution of any integrity check by version, device, work-profile flag and installer package; correlation with auto-update timestamps; crash reports on Android 17 devices.
- **Proposed fix.** [R] If a client integrity check is the source: fail soft (allow, flag server-side) instead of hard-blocking, with a retry and a clear recovery message; do not remove the check without Security's agreement.
- **Regression test.** Install via Play on managed and unmanaged profile; update-interrupt test; launch on newest Android preview/stable images.
- **Confidence.** Medium that the problem is real and growing; **low** on cause.

## R3. Authentication: forced logout and OTP (LOGIN_SESSION, ACCESS_OTP)
- **Symptom.** [Q] LOGIN_SESSION 57 (6.7%), H1 10.3% -> H2 3.9% (p = 0.0002, passes correction). ACCESS_OTP 51 (6.0%), 88% of them one-star, 5.6% in H2, no clear trend. Monthly OTP hits spread over the year (peak Sep 2026: 8, dates 09-02 x3, 09-04, 09-09, 09-11, 09-15, 09-24), so **not a single outage day**. Last 60 days 10 of 152 pool reviews vs 7 of 177 in the prior 60 days (not significant). 15 OTP reviews name more than one delivery channel.
- **User impact.** [I] Cannot sign in at all, or is signed out repeatedly. One reviewer reports being logged out every 5-10 minutes and unable to reach SOS or driver details: **safety-relevant**.
- **Evidence.** Logout every 5-10 min: `6855f79d-f54e-4ce7-9a7f-213677cec9d1` (12.12.2). OTP after 15 min: `3e16be2c-e24e-4ef1-a5e4-c0f8ba9aad24`. No OTP on any channel, about 50 attempts: `57cbaf15-e6aa-4fb5-bb89-07737777a6de`. No message whether number is registered: `3e3d8c85-29ba-4636-bb62-ecaf17ffb6c9`. 30-minute wait: `1dd2a561-33a6-43c5-87cd-fda1cd5b87b2`.
- **Feature check.** Level 1: the Help Center login article (S13, modified 20 Nov 2024) lists three checks: mobile-app subscription not given, a different mobile number or email than the registered one, and an outdated app version; "Mobile App Issues" (S14) adds resend OTP, checking signal and waiting a few minutes. Level 4: yes.
- **Competing explanations.** (a) Subscription not given, or a different number or email than the registered one (the Help Center's own first checks; not an app defect, but the app gives no distinct message; see review `3e3d8c85...`). (b) SMS/WhatsApp provider failure or delay. (c) Rate limiting after retries locking the user out. (d) Per-client SSO or session TTL policy (login bursts in Oct 2025 were mostly version 12.6, 16 of 19 versioned hits, but not tied to a release). Multi-channel failure points at a shared upstream, not one provider **[I]**.
- **System boundary.** Auth service, OTP provider(s), tenant/employee provisioning, session management.
- **Discriminating evidence.** OTP funnel (requested -> sent -> provider-delivered -> entered -> verified) by channel, provider, client, hour; reasons for "not registered"; session TTL and refresh-failure logs; logout events not initiated by the user.
- **Proposed fix.** [R] Distinguish "number not registered / not assigned" from "OTP delayed" in the UI; resend with channel switch and a visible cooldown; silent refresh for ordinary expiry during an active trip while retaining explicit logout and security revocation; an approved emergency-contact fallback after auth loss.
- **Regression test.** Provider-failure simulation; token-expiry during active trip; unprovisioned-number path returns a distinct message.
- **Confidence.** High on symptom, medium-low on cause.

## R4. Tracking and ETA (TRACKING_LOCATION, ETA_PICKUP_TIME)
- **Symptom.** [Q] TRACKING 61 (7.2%), ETA 43 (5.1%); flat across halves (6.8 -> 7.5, 4.7 -> 5.4).
- **User impact.** [I] Employee cannot decide when to leave; leads to missed pickups and no-show marks (R5).
- **Evidence.** Location stuck 30 min: `5d14e08b-ceb3-4849-8e3b-2b94f6f06a07`. Location "one or two hours ago": `ccba873d-c5c1-4c86-808d-d0b5885f1113`. ETA jumps 5 to 30 min: `79708a81-7362-4207-be30-f7817b66eb16`. ETA rises then drops: `954a0c46-3994-4e41-8363-0fb86158bfce`. "Location is not updated until the driver is at your pickup point": `eec41d97-5ac6-4612-ad5d-625e9bbd6669`. Driver connectivity: `9eda9256-7bf8-4e8e-b04d-d48457555dc5`. Offline request: `c4682050-e84d-4490-a694-acd4b981b407`.
- **Competing explanations along the data path** (driver GPS capture -> upload -> server ingest -> ETA computation -> push or poll -> map render): (a) driver phone: battery optimisation kills background location, poor network; (b) ingestion delay or batching; (c) ETA algorithm (traffic model, re-routing); (d) employee app refresh interval/stale cache; (e) operations: driver app not used or trip started late.
- **System boundary.** The data path spans **driver app, backend and employee app**, plus connectivity and operations. The failed boundary is unconfirmed; an employee-app-only change may not address upstream causes.
- **Discriminating evidence.** Location ping gap distribution per trip; server receive-time minus device-time; ETA error vs actual arrival by distance bucket; app refresh interval; share of trips with stale-location flags.
- **Proposed fix.** [R] Show "last updated hh:mm" on the map and grey out stale pins; smooth ETA changes; alert operations when a vehicle goes silent. These are honesty improvements, not cosmetics: stale data presented as live is the core complaint.
- **Regression test.** Replay of recorded trips with injected 10-minute gaps; ETA monotonicity bounds.
- **Confidence.** Medium (clear complaint, several plausible owners).

## R5. No-show handling (NO_SHOW)
- **Symptom.** [Q] 21 reviews (2.5% of POOL), 86% 1-star; monthly counts 1, 3, 4, 3, 4, 2, 1, 3 with **no trend**. Small in count, high in anger.
- **User impact.** [I] Penalty or loss of a ride the employee believes they took or tried to take.
- **Evidence.** Auto-cancel of the logout trip after a login no-show: `0b1041ae-ce09-4947-b5f9-744e9014a639` (2026-09-17, 12.18.1). Check-in reminder suggestion: `7e184ad5-066a-4d36-b7a0-73a0a56bf8a3` (2026-06-29; shown on Play listing, 6 helpful votes). Marked no-show 500 m away in rain: `5427eb1d-476f-4f56-b70a-79a90e2a9135`. Stale banner a year later: `3c7c35b4-2246-4782-9a47-79a9470db2bb`. QR scanned but still no-show: `697e4173-bc7e-42a3-b56d-75a9db00a95f`. Cancellation not reflected: `3e61a75a-2689-4785-af03-4e07a5e52a1b`.
- **Feature check.** (1) Documented (S6, S17): the system marks a no-show if there is no sign-in by trip end; a driver can mark one with a code. The enforcement guide (S17) adds configurable warning and enforcement thresholds, a 30-minute alternate-transport filter, cancellation of the logout trip after a login no-show, email and in-app notifications, and **an optional approval-based restore request raised from the app, off by default**. [F] It describes **no way to contest a no-show that was recorded in error**, and no grace period at the pickup point beyond those filters. So the auto-cancelled logout trip in review `0b1041ae...` is documented behaviour; what the review objects to is surprise, not a defect. (4) Yes. A "reminder when the vehicle is about to pass your pickup" is **not** the documented schedule-reminder feature, so a gap remains **[I]**.
- **Competing explanations.** Policy set by the client (not the app) vs app defect (QR/state sync) vs driver behaviour (marking early) vs stale ETA (R4).
- **Discriminating evidence.** No-show events with timestamp, GPS distance, QR/OTP event, driver-marked vs system-marked; share later reversed; time between vehicle arrival and no-show mark.
- **Proposed fix.** [R] Make the warning before the return leg is cancelled impossible to miss (the guide says notifications exist; check whether they reach the user in time); show who marked the no-show and when; add a way to contest a mistaken mark, not only to restore access; clear stale banners on state change. Penalty thresholds belong to each client.
- **Regression test.** QR-scanned trips never end as no-show; cancelled trip clears its flags.
- **Confidence.** Medium; small n, consistent narratives.

## R6. Booking failures and rules (BOOKING_FAILURE, BOOKING_RULES, CANCEL_EDIT, ADDRESS_LOCATION_MGMT)
- **Symptom.** [Q] BOOKING_FAILURE 43 (5.1%), BOOKING_RULES 18 (2.1%), CANCEL_EDIT 23 (2.7%), ADDRESS 16 (1.9%). Recall for booking failure and address was low in the frozen test (0.25 and 0.17), so these are **probably under-counted**.
- **Evidence.** Book now disabled: `621969c8-9e70-4e8c-80db-def46b641121`. Schedules not listed: `daa27010-2c5f-4b85-8e31-a7d3b6a2acae`. Duplicate schedule: `b0d942c2-6bbe-4c1d-a158-9167965eda3d`. One day visible: `8dd20d1a-8c7b-4ece-a3ee-e2c6e31b9347`. Waitlisted cannot rebook: `6a1820a3-ce1c-45d1-8ff3-4134c0824acc`. 8-hour cutoff: `aadeb072-3a5b-43d9-a4a5-c8459716cc9b`. Wrong dates created: `0b11d7d5-f655-4951-855e-710761f2552e`.
- **Feature check.** (1) Documented: schedule limits, cutoffs, ad-hoc scheduling. These are client-configured rules.
- **Competing explanations.** Many complaints are a rule the user does not understand (cutoff, limit) with **no in-app explanation** [H]; a smaller set look like real defects (wrong dates, duplicates, disabled button) [H].
- **Discriminating evidence.** Day-1 booking funnel with attempt/validation/create/confirmation events, correlation IDs and outcomes by client rule; technical failures separate from valid policy rejection; confirmation latency and duplicate-schedule rate. A fresh manual booking/address audit is required because recall estimates are weak.
- **Proposed fix.** [R] Investigate booking from day 1, show each rejection reason and next step, and fix confirmed wrong-date, duplicate and disabled-button defects separately. Do not wait for the low classifier count to settle before investigating.
- **Regression test.** Date/timezone boundary tests; idempotent create.
- **Confidence.** Low-medium.

## R7. Cross-team routing, fleet and support failures (VEHICLE_DRIVER_OPS, ROUTING_ALLOCATION, SUPPORT_HELPDESK, DRIVER_CONTACT)
- **Symptom.** [Q] VEHICLE_DRIVER_OPS 70 (8.3%), ROUTING 70 (8.3%), SUPPORT 46 (5.4%, 98% one-star), DRIVER_CONTACT 20 (2.4%). Operations only 12.6% of POOL; app + operations 5.7%.
- **Evidence.** 2.5-hour route: `3aa862df-73eb-4868-a695-42158aaced5e`. Clubbing passengers from different states: `7476b129-f0da-458e-8f86-d77ba2f9a710`. IVR request: `490639b9-df47-4486-985c-170673cfe038`. Helpdesk always busy: `3668eb36-579b-4fbf-ad0e-14f9ddc75a97`. Pickup 4:30 for a 6:00 shift: `ce4add6a-5cf6-4c6f-854d-bd4e29c1e07d`. Pickup time changed mid-night: `fde3c41e-ceff-46a0-99d3-2b69c23e6ead`. Pickup times change constantly: `f5347b3d-f7ab-405d-a482-bae26ecd5368`. Chat box request: `c43e13cd-0b94-40a0-b3a2-d4c59b14f049`. No option to call driver or helpdesk: `31f0d5ae-8046-43d7-9e34-8de9408e91a2`.
- **Feature check.** (1) The "Communication interface" article (S15, modified 7 Apr 2025) describes one-way messages from site admins to app users (push notifications, pop-ups, banners) and does not mention drivers, chat or calls. ATLAS (S16) is described as a support chatbot that answers trip, location and scheduling questions and can raise a support ticket; the article does not say which roles use it. [I] The driver-contact requests (20 reviews) therefore point to a likely gap, but the silence of one article does not prove the product has no such feature; confirm in the product.
- **System boundary.** Routing can involve planner software, client policy or execution; vehicles and drivers also involve capacity and vendors. Review text alone cannot decide which boundary failed. Product, Routing Engineering and Operations share diagnosis.
- **Proposed fix.** [R] In-app helpdesk entry with expected response time; masked call/chat to the assigned driver; explain a pickup-time change and notify it. B9 is an owned cross-team workstream: internal incident register by day 5, weekly pilot review, missed-pickup/on-time/detour/resolution metrics, and escalation of confirmed planner defects to Routing Engineering.
- **Confidence.** Medium; ownership uncertain.

## R8. Forced rating, consent and permission prompts (FORCED_RATING, PERMISSIONS_CONSENT, FEEDBACK_FLOW_BROKEN)
- **Symptom.** [Q] FORCED_RATING 17 (2.0%), PERMISSIONS_CONSENT 18 (2.1%), FEEDBACK_FLOW_BROKEN 13 (1.5%, rising from 0.8 to 2.1%).
- **Evidence.** Forced rating after every ride: `f9fce9fe-8115-4a30-8d09-d8bdac76837d` (12.19.0). Trip details blocked until previous ride reviewed: `323f395e-0632-4d4c-9174-5df4d7828680`. Feedback not accepted until 5 stars: `7f43a5e3-e153-46e1-ad4c-fbd83ca2e3f7`. Skip option requested: `fc5d3394-94e1-497e-8dfa-c59291ae63db`. Microphone permission forced: `1f01f748-b40a-488d-914b-b3bcc99a2a6a`. Policy accepted 500 times: `cbd1a2d1-080c-4b9f-a54e-eb42ce163cc4`.
- **Interpretation.** [F] This is an *internal trip-rating screen*, not necessarily Google's in-app review flow. [I] Mandatory trip feedback may push frustrated users to write 1-star Play reviews: plausible, **unmeasurable** from public data. Google's in-app review guidance advises not to gate or pre-prompt reviews; whether MoveInSync's flow touches the Play review prompt is **unverified**.
- **Proposed fix.** [R] Make the in-app trip rating skippable, never block trip details behind it, and do not steer toward 5 stars. This is a usability fix, not rating optimisation; do not add any prompt that routes happy users to the Play Store.
- **Regression test.** Trip details reachable with rating skipped; consent shown once per version of the policy.
- **Confidence.** Medium on existence, low on rating effect.

## R9. Developer reply drought (context, not a fix)
[Q] 30 of 846 POOL reviews have a reply in the window and 2 of 224 in the last 90 days (all-time reply rate was 97.8% in 2023). [H] Replying might reduce repeat complaints or recover some ratings; effect **not measurable** from public data. Replying is cheap but must offer help, not ask for a re-rating.

---

---
## R10. Safety and boarding verification (SAFETY, BOARDING_QR_OTP)
- **Symptom.** [Q] SAFETY 21 reviews (2.5% of POOL, 86% one-star) and BOARDING_QR_OTP 21 (2.5%, 76% one-star); no trend (H1 vs H2 2.1 vs 2.8% and 2.6 vs 2.4%). Many safety mentions are about driver conduct (operations), but several are app-flow problems at the moment of boarding.
- **Evidence.** Seat-belt verification covers the OTP: `e12ed49a-d376-4cf2-9cfd-45cae0162feb` (2026-09-30, 12.11.2), `e67fc7c5-d776-4653-b0ae-478a12216067` (2025-10-27, 12.6). QR scan or booking blocked unless location accuracy is on: `fd4e8200-294d-4877-b4f5-b1e12528ce8d` (2026-07-15), `008ae233-9d63-4c46-a472-957a59ab89ea` (cannot scan QR, 2025-12-01). Driver PIN not working: `3dd690b4-b55f-433c-8a86-1497f0ef0439` (2026-06-08). No call option in an emergency: `31f0d5ae-8046-43d7-9e34-8de9408e91a2`. Logged out and unable to reach the SOS or driver details: `6855f79d-f54e-4ce7-9a7f-213677cec9d1`. Driver conduct (operations, not app): `c789c25d-4efe-4fd4-8986-de67be5beeba`, `59a4dbdd-06a6-4ed1-8a2c-38d2509bb604`, `0c2245c5-dd6f-43da-b799-e26b7b524e94`.
- **Feature check.** Boarding checks (OTP, seat-belt confirmation, QR) are described in the case brief as safety steps; I did not find an article describing their exact flow, so (1) is unverified. (4) Yes.
- **Competing explanations.** Intentional safety design with a poor screen layout; location accuracy used as a fraud or presence check that fails indoors or in basements; OTP and seat-belt prompts competing for the same screen.
- **System boundary.** Employee app boarding screens, driver app, backend verification.
- **Discriminating evidence.** Boarding funnel (OTP shown, seat-belt confirmed, boarded) with drop-off per step; QR scan failure rate by device and location accuracy setting.
- **Proposed fix.** [R] Never let one prompt cover another (OTP always visible); make location-accuracy requirements explain themselves and offer a fallback; keep SOS reachable on every screen. Assess credible safety failures the same day they are discovered, with a named Safety lead and mitigation/escalation; monthly monitoring supplements daily support triage.
- **Confidence.** Medium on the app-flow items; low on rates (n is small).

---
## R11. Notifications and pickup-time changes (NOTIFICATIONS, ETA_PICKUP_TIME)
- **Symptom.** [Q] NOTIFICATIONS 33 reviews (3.9%, 3.2% to 4.5% between halves, not significant). Pickup-time reviews sit inside the ETA cluster.
- **Evidence.** Pickup 4:30 for a 6:00 shift: `ce4add6a-5cf6-4c6f-854d-bd4e29c1e07d`. Pickup time changed in the middle of the night: `fde3c41e-ceff-46a0-99d3-2b69c23e6ead`. Pickup times change constantly: `f5347b3d-f7ab-405d-a482-bae26ecd5368`. Request for a check-in reminder when the vehicle passes the pickup point: `7e184ad5-066a-4d36-b7a0-73a0a56bf8a3`.
- **Feature check.** (1) A "Schedule reminder notification" article exists (S18, title only read). It is not the same as a reminder when the vehicle approaches or passes the pickup point. (4) Yes.
- **Competing explanations.** Routing re-optimisation changes pickup times late; notification delivery fails or arrives late; a client-side roster change.
- **Discriminating evidence.** Log of pickup-time changes (how late before pickup, how often per trip), notification send and delivery times.
- **Proposed fix.** [R] Notify every pickup-time change with the reason and the new time; cap late changes where routing allows; add the check-in reminder as an option.
- **Confidence.** Low-medium.

## Summary: what public data can and cannot support
| # | Cluster | Share of POOL | Public evidence supports | Needs internal data |
|---|---|---|---|---|
| R1 | Stability / loading | 17.7% | Symptom, size, mixed modes | Android vitals, API latency |
| R2 | Install / Android 17 | 2.0-3.0% (growing, uncorrected) | Symptom, emerging pattern | Error source, integrity verdicts |
| R3 | Login / OTP | 6.7% / 6.0% | Symptom, burst pattern | OTP funnel, session logs |
| R4 | Tracking / ETA | 7.2% / 5.1% | Symptom | Ping gaps, ETA error |
| R5 | No-show | 2.5% | Symptom; documented rules (S17) | No-show event logs |
| R6 | Booking | 5.1% + rules 2.1% | Symptom | Rejection reasons |
| R7 | Operations | up to 12.6% operations only | Symptom; some clear app gaps (driver contact) | Vendor and routing data |
| R8 | Forced rating / consent | 2.0% / 2.1% | Symptom | Funnel to 1-star reviews |
| R10 | Safety and boarding verification | 2.5% / 2.5% | Symptom; several clearly app-flow issues | Boarding funnel, QR/OTP failures |
| R11 | Notifications and pickup-time changes | 3.9% (+ pickup-time reviews inside ETA) | Symptom | Notification delivery logs, change log of pickup times |

## Limits
- All counts are approximate: the classifier has precision about 0.76 and recall about 0.65, so in aggregate it under-counts by roughly 14%, while individual categories can be over- or under-counted. Original validation labels were produced by Claude; a 30-row human spot check is complete, with 13 AI-assisted category mappings. It is not a full independent audit. Wilson intervals cover sampling error only, not classifier error.
- Reviews do not identify the employer, city or vendor.
- Small clusters (n < 25) cannot be ranked against each other.
- Android documentation (S19-S21) and Help Center articles (S13-S17) were read on 2026-10-11/12. Articles carry no year on some modification dates; whether a documented feature ships and works reliably is unverified. Internal behaviour was not observed.

Ownership labels are provisional taxonomy buckets, not proof that a cause lies outside Engineering. Routing causes need the B9 cross-team investigation; public text alone cannot separate planner software, client policy and vendor execution.
