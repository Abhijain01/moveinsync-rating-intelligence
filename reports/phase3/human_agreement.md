# Human agreement check (n=30 reviews, 26 categories)

F1 and kappa are over all review-category decisions; exact = the whole label set is identical.

| Pair | F1 | Cohen kappa | Exact match | both | only 2nd | only 1st |
|---|---|---|---|---|---|---|
| Human vs AI hand labels | 0.84 | 0.84 | 73% | 24 | 7 | 2 |
| Human vs rule classifier | 0.67 | 0.66 | 60% | 17 | 8 | 9 |
| AI hand labels vs rule classifier (same 30) | 0.75 | 0.74 | 63% | 21 | 4 | 10 |

Reading: kappa above about 0.6 is substantial agreement. If human vs AI hand labels is much lower than that, treat the Phase 3 validation numbers as optimistic. If human vs classifier is close to AI vs classifier, the classifier's measured quality holds up under an independent labeller.

Small sample: with 30 reviews every figure has a wide margin of error.

Validation caveat: this was a 30-review human spot check, not a full independent audit. Thirteen category mappings were assisted by AI. Original gold labels and category definitions were AI-produced; use these results with that limitation.
