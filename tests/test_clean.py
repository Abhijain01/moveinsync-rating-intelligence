import pandas as pd

from rating_intel.clean import normalise_text, script_class, validate_and_clean


def run(rows, cutoff="2026-10-10T12:00:00+00:00"):
    return validate_and_clean(pd.DataFrame(rows), retrieved_cutoff=cutoff)


def test_invalid_ratings_are_rejected(raw_row_factory):
    rows = [raw_row_factory(1, score=0), raw_row_factory(2, score=6), raw_row_factory(3, score="x"),
            raw_row_factory(4, score=4.5), raw_row_factory(5, score=None), raw_row_factory(6, score=3)]
    clean, rej, counts = run(rows)
    assert list(clean["review_id"]) == ["r6"]
    assert counts["rejected"] == 5
    assert counts["rejected_by_reason"] == {"invalid_score": 5}


def test_missing_id_and_bad_dates_rejected(raw_row_factory):
    rows = [raw_row_factory(1), raw_row_factory(2, at="not a date"), raw_row_factory(3, at=None),
            raw_row_factory(4, at="2030-01-01T00:00:00+00:00")]
    rows.append({**raw_row_factory(5), "review_id": "  "})
    clean, rej, counts = run(rows)
    assert list(clean["review_id"]) == ["r1"]
    reasons = rej.set_index("review_id")["reject_reason"].to_dict()
    assert reasons["r2"] == "invalid_date" and reasons["r3"] == "invalid_date" and reasons["r4"] == "future_date"
    assert counts["rejected_by_reason"]["missing_review_id"] == 1


def test_duplicate_review_id_keeps_latest_retrieval(raw_row_factory):
    old = raw_row_factory(1, text="old text", retrieved="2026-10-01T00:00:00+00:00")
    new = raw_row_factory(1, text="new text", retrieved="2026-10-09T00:00:00+00:00")
    clean, _, counts = run([old, new, raw_row_factory(2)])
    assert len(clean) == 2 and counts["duplicate_review_id_dropped"] == 1
    assert clean.set_index("review_id").loc["r1", "text_norm"] == "new text"


def test_empty_review_text_is_flagged_not_dropped(raw_row_factory):
    rows = [raw_row_factory(1, text=None), raw_row_factory(2, text="   "), raw_row_factory(3, text="fine")]
    clean, _, _ = run(rows)
    c = clean.set_index("review_id")
    assert bool(c.loc["r1", "empty_text"]) and bool(c.loc["r2", "empty_text"]) and not bool(c.loc["r3", "empty_text"])
    assert c.loc["r1", "script_class"] == "empty"


def test_utc_converted_to_ist_date_and_week(raw_row_factory):
    # 2026-03-09 20:00 UTC is 2026-03-10 01:30 IST (Tuesday); the IST week starts Monday 2026-03-09.
    clean, _, _ = run([raw_row_factory(1, at="2026-03-09T20:00:00+00:00")])
    r = clean.iloc[0]
    assert r["date_ist"] == "2026-03-10" and r["month_ist"] == "2026-03" and r["week_start_ist"] == "2026-03-09"


def test_month_boundary_in_ist(raw_row_factory):
    clean, _, _ = run([raw_row_factory(1, at="2026-02-28T19:00:00+00:00")])  # 2026-03-01 00:30 IST
    assert clean.iloc[0]["month_ist"] == "2026-03"


def test_reply_and_version_flags(raw_row_factory):
    clean, _, _ = run([raw_row_factory(1, reply="Thanks"), raw_row_factory(2, ver=None)])
    c = clean.set_index("review_id")
    assert bool(c.loc["r1", "has_reply"]) and not bool(c.loc["r2", "has_reply"])
    assert bool(c.loc["r1", "version_known"]) and not bool(c.loc["r2", "version_known"])


def test_repeated_text_is_flagged_not_removed(raw_row_factory):
    rows = [raw_row_factory(i, text="this exact long sentence repeats") for i in range(3)]
    clean, _, _ = run(rows)
    assert len(clean) == 3 and (clean["text_dup_group_size"] == 3).all()


def test_text_normalisation_and_script():
    assert normalise_text("  a  b\n c ") == "a b c"
    assert normalise_text(None) == ""
    assert script_class("hello") == "latin" and script_class("") == "empty"
    assert script_class("नमस्ते") == "indic"
