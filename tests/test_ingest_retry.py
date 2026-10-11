"""Retry/failure behaviour of scripts/ingest.fetch_page (needs google-play-scraper installed; skipped otherwise)."""
import sys
from pathlib import Path

import pytest

pytest.importorskip("google_play_scraper")
_scripts = Path(__file__).resolve().parents[1] / "scripts"
if not (_scripts / "ingest.py").exists():
    pytest.skip("scripts/ingest.py not present", allow_module_level=True)
sys.path.insert(0, str(_scripts))
import ingest  # noqa: E402


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(ingest.time, "sleep", lambda s: None)


def page(n):
    return [{"reviewId": f"x{i}"} for i in range(n)]


def test_short_page_is_retried_until_full(monkeypatch):
    answers = iter([(page(10), "t1"), (page(200), "t2")])
    monkeypatch.setattr(ingest, "reviews", lambda *a, **k: next(answers))
    rows, tok = ingest.fetch_page("app", "en", "in", None, None, retries=2, base_sleep=0)
    assert len(rows) == 200 and tok == "t2"


def test_persistent_errors_return_empty_after_all_attempts(monkeypatch):
    calls = []

    def boom(*a, **k):
        calls.append(1)
        raise RuntimeError("network")

    monkeypatch.setattr(ingest, "reviews", boom)
    rows, tok = ingest.fetch_page("app", "en", "in", None, "keep", retries=2, base_sleep=0)
    assert rows == [] and tok == "keep" and len(calls) == 3


def test_best_partial_page_is_kept(monkeypatch):
    answers = iter([(page(50), "a"), (page(120), "b"), (page(30), "c")])
    monkeypatch.setattr(ingest, "reviews", lambda *a, **k: next(answers))
    rows, tok = ingest.fetch_page("app", "en", "in", None, None, retries=2, base_sleep=0)
    assert len(rows) == 120 and tok == "b"
