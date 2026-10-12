# Submission corrections and validation - 2026-10-12

## Six corrections
1. Original collection JSONL/manifest, cleaned CSV, quality report and canonical generated report are included. `.gitignore` whitelists this evidence. `scripts/demo.py` provides offline reproduction after dependency installation.
2. Removed displayed-rating-lift arithmetic and replaced its test with collection-manifest verification. Added Google's recent-weighted rating definition to the source register (S22). Historical probe and collection values are distinguished.
3. B0/B6 now investigate self-booking from day 1: attempt-to-confirmation funnel, policy vs technical failure, manual review of weak classifier categories, and reproduction of wrong-date/duplicate/disabled-booking defects.
4. B9 now has an accountable coordinator, joint Product/Routing/Operations ownership, a day-5 action register, a 2-4 week pilot, weekly reviews, metrics and guardrails. Historic score values remain unchanged; they describe an app-team queue, not company-wide priorities.
5. Credible safety failures get same-day assessment on discovery; daily Product Support triage supplements the monthly tool. Ordinary session expiry is separated from explicit logout and security revocation. No protected data is exposed after revocation.
6. Updated population, uncertainty and human-validation wording across the documents. The 30-review check is complete but partly assisted (13 mappings), not a full independent audit. Listing values use their dated source captures.

## Verified results
- `python -m pytest -ra`: **85 passed, zero failed, zero skipped** with the included original snapshot.
- `python scripts/demo.py`: runs offline; reproduces **2,856** reviews in the year, **846** rated 1-3 stars, **593** actionable, **150** stability complaints, **105** authentication-union complaints, and July/August install-error flags.
- Frozen classifier validation reproduced: precision **0.76**, recall **0.65**, F1 **0.70**. No taxonomy rules were changed.
- Raw-to-clean reconstruction matches the supplied cleaned snapshot after normalizing CSV round-trip representations; original cleaned CSV bytes are preserved for exact claim reproduction.
- Collection manifest confirms 24,314 rows, 122 pages, token exhaustion; this is not proof of a census. Displayed rating captured 4.637723; ratings count 114,857.
- Reviewer identity fields removed from the supplied probe. Virtual environments, caches, Git history, private `.env` and pagination checkpoints excluded from the ZIP. Public review text/IDs retained for traceability.

## Publish the corrected project
The live GitHub repository is unchanged by this local correction. Extract the ZIP and copy the project files into your existing checkout, keeping your existing `.git` directory. Review `git diff` and `git status`, run `python scripts/demo.py` and `python -m pytest -ra`, then commit and push the corrected source, documentation and whitelisted snapshot. The original evidence paths must appear in the commit; otherwise the 16 data-dependent checks can be skipped again.

For the submission form: link the repository, `docs/EXECUTIVE_RECOMMENDATION.md`, `docs/engineering_tickets.md` and the canonical report. Field 7 uses `docs/SUBMISSION_NOTE.md`. Add a short demonstration video if you have one. Check all public links in a signed-out window. CV and LinkedIn links are separate; they were not changed or verified here.

## Remaining limits
Public reviews are self-selected and scoped to English/India collection; labels are approximate; hypotheses need internal telemetry and customer validation. Future fresh ingestion needs Google access. Optional Ollama labeling is not validated against a real model. Recommendations have not been deployed and no causal rating improvement is demonstrated.
