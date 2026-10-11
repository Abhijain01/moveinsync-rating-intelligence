"""Parity with the Phase 3 results on the real snapshot. Skipped when the data folder is absent."""
import glob
from pathlib import Path

import pytest

from rating_intel.pipeline import run_analysis

FILES = sorted(glob.glob(str(Path(__file__).resolve().parents[1] / "data" / "processed" / "run_*" / "reviews_clean.csv")))
pytestmark = pytest.mark.skipif(not FILES, reason="no real snapshot under data/processed")


def test_phase3_numbers_reproduce(tmp_path):
    csv = next((f for f in FILES if "run_20261010T203205Z" in f), None)
    if csv is None:
        pytest.skip("Phase 3 snapshot run_20261010T203205Z not present")
    info = run_analysis(csv, tmp_path, since="2025-10-10", split_date="2026-04-10")
    assert (info["window_reviews"], info["pool_1to3"], info["neg_1to2"]) == (2856, 846, 772)
    assert (info["actionable"], info["generic_negative_only"]) == (593, 162)
    import pandas as pd
    t = pd.read_csv(tmp_path / "themes.csv", encoding="utf-8-sig").set_index("category")
    assert t.loc["CRASH_LOAD_PERF", "n_pool"] == 150 and t.loc["LOGIN_SESSION", "n_pool"] == 57
    assert t.loc["ACCESS_OTP", "n_pool"] == 51 and t.loc["NO_SHOW", "n_pool"] == 21
