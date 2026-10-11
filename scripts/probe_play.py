"""Phase 1 probe: what review data can actually be retrieved for the MoveInSync employee app?

Run locally (the cloud workspace cannot reach play.google.com). Read-only, low request rate.
Writes an auditable raw snapshot to data/raw/ and prints a short availability report.
"""
import argparse
import collections
import datetime as dt
import json
import sys
import time
from pathlib import Path

from google_play_scraper import Sort, app, reviews

APP_ID = "com.moveinsync.ets"
FIELDS = [
    "reviewId", "userName", "content", "score", "thumbsUpCount",
    "reviewCreatedVersion", "at", "replyContent", "repliedAt", "appVersion",
]


def fetch_reviews(app_id, lang, country, target, page_size=200, sleep_s=1.0, retries=3):
    """Page through newest-first reviews until `target` collected or data runs out."""
    collected, token = [], None
    while len(collected) < target:
        want = min(page_size, target - len(collected))
        for attempt in range(1, retries + 1):
            try:
                batch, token = reviews(
                    app_id, lang=lang, country=country, sort=Sort.NEWEST,
                    count=want, continuation_token=token,
                )
                break
            except Exception as exc:  # network/format errors from the scraper
                if attempt == retries:
                    print(f"ERROR after {retries} attempts: {exc!r}", file=sys.stderr)
                    return collected
                time.sleep(2 ** attempt)
        if not batch:
            break
        collected.extend(batch)
        if token is None:
            break
        time.sleep(sleep_s)
    return collected


def summarize(rows):
    """Pure function: availability statistics for a list of review dicts."""
    n = len(rows)
    if n == 0:
        return {"n": 0}
    ids = [r.get("reviewId") for r in rows]
    dates = [r["at"] for r in rows if r.get("at")]
    versions = collections.Counter(
        (r.get("appVersion") or r.get("reviewCreatedVersion") or "missing") for r in rows
    )
    return {
        "n": n,
        "unique_review_ids": len(set(i for i in ids if i)),
        "date_min": str(min(dates)) if dates else None,
        "date_max": str(max(dates)) if dates else None,
        "score_counts": dict(sorted(collections.Counter(r.get("score") for r in rows).items(), key=lambda kv: str(kv[0]))),
        "with_developer_reply": sum(1 for r in rows if r.get("replyContent")),
        "empty_text": sum(1 for r in rows if not (r.get("content") or "").strip()),
        "thumbs_up_gt0": sum(1 for r in rows if (r.get("thumbsUpCount") or 0) > 0),
        "null_counts": {f: sum(1 for r in rows if r.get(f) in (None, "")) for f in FIELDS},
        "top_versions": versions.most_common(10),
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--app-id", default=APP_ID)
    p.add_argument("--lang", default="en")
    p.add_argument("--country", default="in")
    p.add_argument("--target", type=int, default=400)
    p.add_argument("--out", default="data/raw")
    args = p.parse_args(argv)

    retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
    meta = {}
    try:
        info = app(args.app_id, lang=args.lang, country=args.country)
        keep = ["appId", "title", "developer", "score", "ratings", "reviews",
                "histogram", "installs", "version", "updated", "genre", "url"]
        meta = {k: info.get(k) for k in keep}
    except Exception as exc:
        print(f"app() metadata failed: {exc!r}", file=sys.stderr)
    print("APP METADATA:", json.dumps(meta, indent=2, default=str))

    rows = fetch_reviews(args.app_id, args.lang, args.country, args.target)
    stats = summarize(rows)
    print("REVIEW AVAILABILITY:", json.dumps(stats, indent=2, default=str))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"probe_{args.app_id}_{stamp}.json"
    payload = {
        "retrieved_at_utc": retrieved_at,
        "params": {"app_id": args.app_id, "lang": args.lang,
                   "country": args.country, "target": args.target, "sort": "NEWEST"},
        "library": "google-play-scraper",
        "app_metadata": meta,
        "summary": stats,
        "reviews": rows,
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Saved snapshot: {path}")
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())