import hashlib
from pathlib import Path

import pandas as pd

from rating_intel.classify import classify_frame, classify_text


def test_multi_label_review_counts_in_each_category():
    hits = classify_text("Live location not updating, ETA is wrong")
    assert set(hits) == {"TRACKING_LOCATION", "ETA_PICKUP_TIME"}


def test_empty_none_and_non_string_have_no_labels():
    assert classify_text("") == {} and classify_text("   ") == {}
    assert classify_text(None) == {} and classify_text(float("nan")) == {}


def test_generic_negative_has_no_category_but_is_flagged():
    df = pd.DataFrame({"text_norm": ["worst app ever"], "score": [1]})
    out = classify_frame(df)
    assert out.loc[0, "n_labels"] == 0 and bool(out.loc[0, "generic_negative_only"]) and not bool(out.loc[0, "actionable"])


def test_category_counts_overlap_and_are_not_a_partition():
    df = pd.DataFrame({"text_norm": ["OTP not received, cannot login", "Live location not updating, ETA is wrong"], "score": [1, 1]})
    out = classify_frame(df)
    assert out["n_labels"].sum() >= 3
    assert out[["ACCESS_OTP", "TRACKING_LOCATION", "ETA_PICKUP_TIME"]].to_numpy().sum() == 3
    assert out["actionable"].sum() == 2  # reviews, not labels


def test_cross_cutting_tag_alone_is_not_actionable():
    # SAFETY annotates but does not count as an actionable complaint by itself
    out = classify_frame(pd.DataFrame({"text_norm": ["I felt unsafe"], "score": [1]}))
    if out.loc[0, "SAFETY"] == 1 and out.loc[0, "n_labels"] == 1:
        assert not bool(out.loc[0, "actionable"])


def test_frozen_taxonomy_hash():
    p = Path(__file__).resolve().parents[1] / "rating_intel" / "taxonomy.py"
    assert hashlib.sha256(p.read_bytes()).hexdigest()[:16] == "e3799ec1be70c4ee", \
        "taxonomy changed: re-run the hand-labelled validation before using new counts"


def test_empty_frame_keeps_all_columns_and_pipeline_survives(tmp_path):
    empty = classify_frame(pd.DataFrame({"text_norm": [], "score": []}))
    assert "ACCESS_OTP" in empty.columns and "actionable" in empty.columns and len(empty) == 0
