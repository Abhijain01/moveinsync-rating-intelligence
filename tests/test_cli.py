import json

from rating_intel.cli import main
from tests.conftest import raw_row


def make_raw_run(tmp_path, n=30):
    run = tmp_path / "raw" / "run_TEST"
    run.mkdir(parents=True)
    rows = [raw_row(i, text="OTP not received" if i % 3 == 0 else "great app", score=1 if i % 3 == 0 else 5,
                    at=f"2026-0{1 + i % 9}-10T06:00:00+00:00") for i in range(n)]
    rows.append(raw_row(999, score=9))  # invalid, must be rejected not crash
    (run / "reviews.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    (run / "manifest.json").write_text(json.dumps({"run_id": "run_TEST", "status": "complete", "stop_reason": "token_exhausted",
                                                   "pages": 1, "params": {}, "environment": {},
                                                   "started_utc": "2026-10-10T20:00:00+00:00",
                                                   "listing_at_start": {"score": 4.6, "ratings": 1000, "reviews": 31}}))
    return run


def test_clean_status_analyze_compare_end_to_end(tmp_path, capsys):
    run = make_raw_run(tmp_path)
    proc = tmp_path / "processed"
    assert main(["clean", str(run), "--out", str(proc)]) == 0
    csv = proc / "run_TEST" / "reviews_clean.csv"
    assert csv.exists() and (proc / "run_TEST" / "rejects.csv").exists()

    assert main(["status", str(csv), "--manifest", str(run / "manifest.json")]) == 0
    assert "Play listing" in capsys.readouterr().out

    out = tmp_path / "rep"
    assert main(["analyze", str(csv), "--manifest", str(run / "manifest.json"), "--out", str(out)]) == 0
    assert (out / "report.md").exists()
    assert main(["compare", str(csv), str(csv)]) == 0


def test_llm_flag_without_env_is_refused(tmp_path, capsys):
    run = make_raw_run(tmp_path)
    proc = tmp_path / "p"
    main(["clean", str(run), "--out", str(proc)])
    rc = main(["analyze", str(proc / "run_TEST" / "reviews_clean.csv"), "--llm", "--env-file", str(tmp_path / "none.env"),
               "--out", str(tmp_path / "o")])
    assert rc == 2 and "RI_LLM_PROVIDER" in capsys.readouterr().err
