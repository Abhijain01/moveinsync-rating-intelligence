# Classifier validation: audit2_sample.csv (n=100)

- Micro precision **0.76**, recall **0.65**, F1 **0.70** (tp=68, fp=21, fn=36)
- 'Has an actionable category' flag: gold 76, predicted 60, precision 1.00, recall 0.79

| Category | gold n | predicted n | TP | FP | FN | Precision | Recall | Note |
|---|---|---|---|---|---|---|---|---|
| CRASH_LOAD_PERF | 21 | 22 | 17 | 5 | 4 | 0.77 | 0.81 |  |
| VEHICLE_DRIVER_OPS | 12 | 9 | 7 | 2 | 5 | 0.78 | 0.58 |  |
| ACCESS_OTP | 10 | 6 | 6 | 0 | 4 | 1.0 | 0.6 |  |
| ADDRESS_LOCATION_MGMT | 6 | 1 | 1 | 0 | 5 | 1.0 | 0.17 | gold n < 10: unstable |
| INSTALL_ERROR | 5 | 5 | 4 | 1 | 1 | 0.8 | 0.8 | gold n < 10: unstable |
| FEATURE_REQUEST | 5 | 3 | 2 | 1 | 3 | 0.67 | 0.4 | gold n < 10: unstable |
| UI_UX | 5 | 6 | 4 | 2 | 1 | 0.67 | 0.8 | gold n < 10: unstable |
| LOGIN_SESSION | 4 | 5 | 3 | 2 | 1 | 0.6 | 0.75 | gold n < 10: unstable |
| BOOKING_FAILURE | 4 | 1 | 1 | 0 | 3 | 1.0 | 0.25 | gold n < 10: unstable |
| PERMISSIONS_CONSENT | 4 | 2 | 2 | 0 | 2 | 1.0 | 0.5 | gold n < 10: unstable |
| UPDATE_REGRESSION | 3 | 1 | 1 | 0 | 2 | 1.0 | 0.33 | gold n < 10: unstable |
| DRIVER_CONTACT | 3 | 3 | 2 | 1 | 1 | 0.67 | 0.67 | gold n < 10: unstable |
| ROUTING_ALLOCATION | 3 | 4 | 2 | 2 | 1 | 0.5 | 0.67 | gold n < 10: unstable |
| SUPPORT_HELPDESK | 3 | 2 | 2 | 0 | 1 | 1.0 | 0.67 | gold n < 10: unstable |
| TRACKING_LOCATION | 3 | 4 | 3 | 1 | 0 | 0.75 | 1.0 | gold n < 10: unstable |
| FORCED_RATING | 3 | 3 | 3 | 0 | 0 | 1.0 | 1.0 | gold n < 10: unstable |
| FEEDBACK_FLOW_BROKEN | 2 | 1 | 0 | 1 | 2 | 0.0 | 0.0 | gold n < 10: unstable |
| DEVICE_COMPAT | 2 | 2 | 2 | 0 | 0 | 1.0 | 1.0 | gold n < 10: unstable |
| BOOKING_RULES | 1 | 1 | 1 | 0 | 0 | 1.0 | 1.0 | gold n < 10: unstable |
| NOTIFICATIONS | 1 | 1 | 1 | 0 | 0 | 1.0 | 1.0 | gold n < 10: unstable |
| ETA_PICKUP_TIME | 1 | 2 | 1 | 1 | 0 | 0.5 | 1.0 | gold n < 10: unstable |
| CANCEL_EDIT | 1 | 2 | 1 | 1 | 0 | 0.5 | 1.0 | gold n < 10: unstable |
| SAFETY | 1 | 1 | 1 | 0 | 0 | 1.0 | 1.0 | gold n < 10: unstable |
| BOARDING_QR_OTP | 1 | 2 | 1 | 1 | 0 | 0.5 | 1.0 | gold n < 10: unstable |
| NO_SHOW | 0 | 0 | 0 | 0 | 0 | nan | nan | gold n < 10: unstable |
| WORKPLACE_FEATURE | 0 | 0 | 0 | 0 | 0 | nan | nan | gold n < 10: unstable |