import json

import pandas as pd

from rating_intel.pipeline import run_analysis
from rating_intel.status import headline, read_listing


def frame(rows):
    d = pd.DataFrame(rows)
    d["version_known"] = True
    d["app_version"] = "1"
    d["has_reply"] = False
    d["month_ist"] = d["date_ist"].str[:7]
    d["text_norm"] = d.get("text_norm", "ok")
    d["review_id"] = [f"r{i}" for i in range(len(d))]
    return d


def test_headline_detects_a_real_drop():
    rows = [{"date_ist": "2026-08-20", "score": 5, "text_norm": "great"} for _ in range(300)]
    rows += [{"date_ist": "2026-10-05", "score": 1, "text_norm": "app crashing"} for _ in range(150)]
    rows += [{"date_ist": "2026-10-05", "score": 5, "text_norm": "great"} for _ in range(150)]
    h = headline(frame(rows), days=30)
    assert h["current"]["n"] == 300 and h["current"]["one_pct"] == 50.0
    assert h["mean_change"] < -1 and h["one_star_p"] < 0.001
    assert "statistically detectable change" in " ".join(h["lines"])
    assert h["top_themes"][0][0] == "CRASH_LOAD_PERF"


def test_headline_flat_period_says_no_change():
    rows = [{"date_ist": d, "score": s, "text_norm": "x"} for d in ("2026-08-20", "2026-10-05") for s in ([1] * 25 + [5] * 75)]
    h = headline(frame(rows), days=30)
    assert "no statistically distinguishable change" in " ".join(h["lines"])


def test_headline_with_empty_previous_period_does_not_crash():
    h = headline(frame([{"date_ist": "2026-10-05", "score": 4, "text_norm": "x"}] * 5), days=30)
    assert h["previous"]["n"] == 0 and h["mean_change"] is None


def test_listing_from_manifest(tmp_path):
    m = tmp_path / "manifest.json"
    m.write_text(json.dumps({"started_utc": "2026-10-10T20:32:05+00:00",
                             "listing_at_start": {"score": 4.6, "ratings": 114855, "reviews": 24000}}))
    assert read_listing(m)["ratings"] == 114855 and read_listing(tmp_path / "missing.json") is None
    (tmp_path / "bad.json").write_text("{not json")
    assert read_listing(tmp_path / "bad.json") is None


def test_report_starts_with_headline(tmp_path, clean_df):
    csv = tmp_path / "c.csv"
    clean_df.to_csv(csv, index=False, encoding="utf-8-sig")
    run_analysis(csv, tmp_path / "o")
    text = (tmp_path / "o" / "report.md").read_text(encoding="utf-8")
    assert "## 0. How are our Play Store ratings?" in text
