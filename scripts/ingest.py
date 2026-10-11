"""Phase 2 ingestion: pull Google Play reviews (newest first) into an auditable raw snapshot.

Output (one folder per run under --out):
  reviews.jsonl     one JSON object per review, appended page by page (nothing is lost if the run stops)
  manifest.json     parameters, library version, listing metadata, counts, status
  checkpoint.pkl    pagination token so an interrupted run can be resumed with --resume

Notes
- google-play-scraper hides network errors: a failed request comes back as an empty/short page with no
  continuation token, which looks exactly like "no more reviews". We therefore retry short pages and
  compare the final count with the listing's own review count (see manifest + data-quality report).
- Reviewer names and avatars are NOT stored (data minimisation); analysis does not need them.
- The scraper builds timestamps with datetime.fromtimestamp (naive local time); we convert to UTC here.
"""
import argparse
import datetime as dt
import json
import pickle
import platform
import sys
import time
from importlib import metadata
from pathlib import Path

from google_play_scraper import Sort, app, reviews

APP_ID = "com.moveinsync.ets"
PAGE_SIZE = 200


def utc_iso(value):
    """datetime -> ISO-8601 UTC string. Naive datetimes are treated as machine-local time."""
    if not isinstance(value, dt.datetime):
        return None
    if value.tzinfo is None:
        value = value.astimezone()  # attach the machine's local timezone
    return value.astimezone(dt.timezone.utc).isoformat()


def to_record(raw, app_id, page_index, retrieved_at):
    """Map a scraper review dict to our raw schema. Original text is kept untouched."""
    return {
        "review_id": raw.get("reviewId"),
        "source_ref": f"play:{app_id}:{raw.get('reviewId')}",
        "text_original": raw.get("content"),
        "score": raw.get("score"),
        "thumbs_up": raw.get("thumbsUpCount"),
        # the scraper maps appVersion and reviewCreatedVersion to the same source element
        "app_version": raw.get("appVersion") or raw.get("reviewCreatedVersion"),
        "at_utc": utc_iso(raw.get("at")),
        "reply_text": raw.get("replyContent"),
        "replied_at_utc": utc_iso(raw.get("repliedAt")),
        "page_index": page_index,
        "retrieved_at_utc": retrieved_at,
    }


def fetch_page(app_id, lang, country, score, token, retries, base_sleep):
    """Return (rows, next_token). Short pages are retried because errors are swallowed upstream."""
    best_rows, best_token = [], token
    for attempt in range(retries + 1):
        try:
            rows, nxt = reviews(
                app_id, lang=lang, country=country, sort=Sort.NEWEST,
                count=PAGE_SIZE, filter_score_with=score, continuation_token=token,
            )
        except Exception as exc:
            print(f"  request error: {exc!r}", file=sys.stderr)
            rows, nxt = [], token
        if len(rows) >= PAGE_SIZE:
            return rows, nxt
        if len(rows) > len(best_rows):
            best_rows, best_token = rows, nxt
        if attempt < retries:
            time.sleep(base_sleep * (2 ** (attempt + 1)))
    return best_rows, best_token


def write_manifest(path, manifest):
    path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")


def run(args):
    now = dt.datetime.now(dt.timezone.utc)
    if args.resume:
        run_dir = Path(args.resume)
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        state = pickle.loads((run_dir / "checkpoint.pkl").read_bytes())
        token, pages, written = state["token"], state["pages"], state["rows"]
        manifest.setdefault("resumed_at_utc", []).append(now.isoformat())
        app_id = manifest["params"]["app_id"]
        lang, country, score = (manifest["params"][k] for k in ("lang", "country", "score"))
    else:
        app_id, lang, country, score = args.app_id, args.lang, args.country, args.score
        run_dir = Path(args.out) / f"run_{now.strftime('%Y%m%dT%H%M%SZ')}"
        run_dir.mkdir(parents=True, exist_ok=False)
        token, pages, written = None, 0, 0
        listing = {}
        try:
            info = app(app_id, lang=lang, country=country)
            keep = ["appId", "title", "developer", "score", "ratings", "reviews",
                    "histogram", "installs", "version", "updated", "genre", "url"]
            listing = {k: info.get(k) for k in keep}
            if isinstance(listing.get("updated"), (int, float)):
                listing["updated_utc"] = dt.datetime.fromtimestamp(
                    listing["updated"], dt.timezone.utc).isoformat()
        except Exception as exc:
            print(f"app() metadata failed: {exc!r}", file=sys.stderr)
        manifest = {
            "run_id": run_dir.name,
            "started_utc": now.isoformat(),
            "params": {"app_id": app_id, "lang": lang, "country": country, "score": score,
                       "sort": "NEWEST", "max_reviews": args.max_reviews,
                       "sleep_seconds": args.sleep, "retries": args.retries},
            "environment": {
                "google_play_scraper": metadata.version("google-play-scraper"),
                "python": platform.python_version(), "os": platform.platform()},
            "listing_at_start": listing,
        }

    jsonl_path = run_dir / "reviews.jsonl"
    ckpt_path = run_dir / "checkpoint.pkl"
    stop_reason, status = "unknown", "running"
    manifest["status"] = status
    write_manifest(run_dir / "manifest.json", manifest)
    print(f"Run folder: {run_dir}")

    try:
        with jsonl_path.open("a", encoding="utf-8") as fh:
            while True:
                if args.max_reviews and written >= args.max_reviews:
                    stop_reason = "max_reviews_reached"
                    break
                rows, token = fetch_page(app_id, lang, country, score, token,
                                         args.retries, args.sleep)
                if not rows:
                    stop_reason = "no_more_rows"
                    break
                retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
                pages += 1
                for raw in rows:
                    fh.write(json.dumps(to_record(raw, app_id, pages, retrieved_at),
                                        ensure_ascii=False) + "\n")
                fh.flush()
                written += len(rows)
                ckpt_path.write_bytes(pickle.dumps({"token": token, "pages": pages, "rows": written}))
                oldest = min((utc_iso(r.get("at")) or "" for r in rows), default="")
                print(f"page {pages}: +{len(rows)} (total {written}), oldest in page {oldest[:10]}")
                if token is None or getattr(token, "token", None) is None:
                    stop_reason = "token_exhausted"
                    break
                time.sleep(args.sleep)
        status = "complete"
    except KeyboardInterrupt:
        stop_reason, status = "interrupted_by_user", "incomplete"
        print("Interrupted. Resume with: --resume", run_dir)
    except Exception as exc:
        stop_reason, status = f"error: {exc!r}", "incomplete"
        print(f"ERROR: {exc!r}", file=sys.stderr)

    manifest.update({
        "status": status, "stop_reason": stop_reason, "pages": pages, "rows_written": written,
        "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    })
    write_manifest(run_dir / "manifest.json", manifest)
    expected = (manifest.get("listing_at_start") or {}).get("reviews")
    print(f"Done: status={status}, stop_reason={stop_reason}, rows={written}, listing text-review count={expected}")
    return 0 if written else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--app-id", default=APP_ID)
    p.add_argument("--lang", default="en")
    p.add_argument("--country", default="in")
    p.add_argument("--score", type=int, choices=[1, 2, 3, 4, 5], default=None,
                   help="optional single-star filter (fallback if a full pull is truncated)")
    p.add_argument("--max-reviews", type=int, default=0, help="0 = everything the source returns")
    p.add_argument("--sleep", type=float, default=1.5, help="seconds between requests")
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--out", default="data/raw")
    p.add_argument("--resume", default=None, help="path of an interrupted run folder")
    return run(p.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())