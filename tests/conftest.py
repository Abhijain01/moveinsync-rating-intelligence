import datetime as dt
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def raw_row(i, text="ok", score=5, at="2026-03-10T08:00:00+00:00", ver="12.1.0", reply=None, retrieved="2026-10-10T10:00:00+00:00", page=1):
    return {"review_id": f"r{i}", "source_ref": f"play:x:r{i}", "text_original": text, "score": score,
            "thumbs_up": 0, "app_version": ver, "at_utc": at, "reply_text": reply, "replied_at_utc": None,
            "page_index": page, "retrieved_at_utc": retrieved}


@pytest.fixture
def raw_row_factory():
    return raw_row


@pytest.fixture
def clean_df():
    """A small valid cleaned snapshot spanning ten months with known counts."""
    from rating_intel.clean import validate_and_clean
    rows = []
    n = 0
    start = dt.date(2026, 1, 15)
    for m in range(10):
        month = (start.month - 1 + m) % 12 + 1
        year = start.year + (start.month - 1 + m) // 12
        for k in range(20):
            n += 1
            score = 1 if k < 4 else (3 if k < 6 else 5)
            text = "OTP not received" if (k < 2) else ("great app" if score == 5 else "worst app")
            rows.append(raw_row(n, text=text, score=score, at=f"{year}-{month:02d}-10T06:00:00+00:00",
                                ver="12.1.0" if m < 8 else "12.2.0"))
    clean, _, _ = validate_and_clean(pd.DataFrame(rows), retrieved_cutoff="2026-12-31T00:00:00+00:00")
    return clean
