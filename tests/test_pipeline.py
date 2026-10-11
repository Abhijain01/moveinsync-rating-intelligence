import json

import pandas as pd
import pytest

from rating_intel.pipeline import load_clean, run_analysis
from tests.test_llm import Fake, good  # noqa: F401


def test_end_to_end_outputs(tmp_path, clean_df):
    csv = tmp_path / "clean.csv"
    clean_df.to_csv(csv, index=False, encoding="utf-8-sig")
    info = run_analysis(csv, tmp_path / "out")
    for name in ["report.md", "themes.csv", "monthly.csv", "spikes.csv", "version_flags.csv", "classified_pool.csv", "run_info.json"]:
        assert (tmp_path / "out" / name).exists(), name
    assert info["window_reviews"] == 200 and info["pool_1to3"] == 60 and info["actionable"] == 20
    assert info["generic_negative_only"] == 40
    themes = pd.read_csv(tmp_path / "out" / "themes.csv", encoding="utf-8-sig").set_index("category")
    assert themes.loc["ACCESS_OTP", "n_pool"] == 20
    assert json.loads((tmp_path / "out" / "run_info.json").read_text())["taxonomy_sha256_16"] == "e3799ec1be70c4ee"
    assert "Limits" in (tmp_path / "out" / "report.md").read_text()


def test_same_input_gives_identical_counts(tmp_path, clean_df):
    csv = tmp_path / "c.csv"
    clean_df.to_csv(csv, index=False, encoding="utf-8-sig")
    run_analysis(csv, tmp_path / "a")
    run_analysis(csv, tmp_path / "b")
    assert (tmp_path / "a" / "themes.csv").read_text(encoding="utf-8-sig") == (tmp_path / "b" / "themes.csv").read_text(encoding="utf-8-sig")


def test_llm_labels_do_not_change_counts_and_failures_fall_back(tmp_path, clean_df):
    csv = tmp_path / "c.csv"
    clean_df.to_csv(csv, index=False, encoding="utf-8-sig")
    base = run_analysis(csv, tmp_path / "base")
    failing = run_analysis(csv, tmp_path / "llm", provider=Fake([RuntimeError("down")]), sleep=lambda _: None)
    assert failing["llm"]["enabled"] and failing["llm"]["attempted"] == 40 and failing["llm"]["fallback"] == 40
    assert failing["actionable"] == base["actionable"]
    a = pd.read_csv(tmp_path / "base" / "themes.csv", encoding="utf-8-sig")
    b = pd.read_csv(tmp_path / "llm" / "themes.csv", encoding="utf-8-sig")
    assert a.equals(b)


def test_rejects_non_clean_input_and_empty(tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"a": [1]}).to_csv(bad, index=False)
    with pytest.raises(ValueError, match="not a cleaned snapshot"):
        load_clean(bad)


def test_comparison_section_when_previous_given(tmp_path, clean_df):
    new = tmp_path / "new.csv"
    old = tmp_path / "old.csv"
    clean_df.to_csv(new, index=False, encoding="utf-8-sig")
    clean_df.iloc[10:].to_csv(old, index=False, encoding="utf-8-sig")
    info = run_analysis(new, tmp_path / "o", prev_csv=old)
    text = (tmp_path / "o" / "report.md").read_text()
    assert "Change since the previous snapshot" in text and (tmp_path / "o" / "new_reviews.csv").exists()
    assert info["previous_csv"]


def test_window_with_only_positive_reviews_does_not_crash(tmp_path, clean_df):
    pos = clean_df[clean_df["score"] >= 4]
    csv = tmp_path / "pos.csv"
    pos.to_csv(csv, index=False, encoding="utf-8-sig")
    info = run_analysis(csv, tmp_path / "o")
    assert info["pool_1to3"] == 0 and (tmp_path / "o" / "report.md").exists()
