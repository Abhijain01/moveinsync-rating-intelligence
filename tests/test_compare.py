import pandas as pd

from rating_intel.clean import validate_and_clean
from rating_intel.compare import compare_snapshots, new_review_score_mix


def snap(rows):
    c, _, _ = validate_and_clean(pd.DataFrame(rows), retrieved_cutoff="2026-12-31T00:00:00+00:00")
    return c


def test_compare_detects_all_change_types(raw_row_factory):
    f = raw_row_factory
    old = snap([f(1, text="a", score=5), f(2, text="b", score=3), f(3, text="c"), f(4, text="d")])
    new = snap([f(1, text="a", score=5), f(2, text="b changed", score=3), f(3, text="c", score=1),
                f(4, text="d", reply="thanks"), f(5, text="brand new", score=2)])
    c = compare_snapshots(old, new)
    assert (c["n_new"], c["n_missing_in_new"], c["n_edited"], c["n_rescored"], c["n_reply_added"]) == (1, 0, 1, 1, 1)
    assert new_review_score_mix(c["new_reviews"]) == {2: 1}


def test_compare_reports_deleted_reviews_and_partial_new_snapshot(raw_row_factory):
    f = raw_row_factory
    old = snap([f(1, at="2026-01-01T00:00:00+00:00"), f(2, at="2026-06-01T00:00:00+00:00")])
    new = snap([f(2, at="2026-06-01T00:00:00+00:00")])
    c = compare_snapshots(old, new)
    assert c["n_missing_in_new"] == 1 and c["new_snapshot_may_be_partial"] is True


def test_identical_snapshots_show_no_change(raw_row_factory):
    s = snap([raw_row_factory(i) for i in range(3)])
    c = compare_snapshots(s, s)
    assert (c["n_new"], c["n_missing_in_new"], c["n_edited"], c["n_rescored"]) == (0, 0, 0, 0)
    assert new_review_score_mix(c["new_reviews"]) == {}
