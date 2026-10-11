"""Command line: python -m rating_intel {clean|analyze|status|compare} ..."""
import argparse
import datetime as dt
import sys
from pathlib import Path

from .compare import compare_snapshots, new_review_score_mix
from .llm import load_env_file, provider_from_env
from .pipeline import load_clean, run_analysis
from .status import headline


def cmd_clean(a):
    from .clean import main as clean_main
    return clean_main([a.run_dir, "--out", a.out])


def cmd_analyze(a):
    env = load_env_file(a.env_file)
    provider = None
    if a.llm:
        if "RI_LLM_PROVIDER" not in env:
            print("--llm needs RI_LLM_PROVIDER=ollama in the env file (copy .env.example to .env).", file=sys.stderr)
            return 2
        provider = provider_from_env(env)
    out = a.out or f"reports/analysis_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    info = run_analysis(a.csv, out, since=a.since, split_date=a.split_date, prev_csv=a.prev, provider=provider, manifest_path=a.manifest)
    print(f"window {info['window_since']}..{info['window_until']}: {info['window_reviews']} reviews, "
          f"pool {info['pool_1to3']}, actionable {info['actionable']}, spikes {info['n_spikes']}, "
          f"version flags {info['n_version_flags']}")
    print(f"taxonomy {info['taxonomy_sha256_16']}  input {info['input_sha256_16']}")
    print(f"report: {Path(info['out_dir']) / 'report.md'}")
    return 0


def cmd_status(a):
    h = headline(load_clean(a.csv), days=a.days, manifest_path=a.manifest)
    print("\n".join(h["lines"]))
    return 0


def cmd_compare(a):
    c = compare_snapshots(load_clean(a.old), load_clean(a.new))
    print(f"rows {c['old_rows']} -> {c['new_rows']}; new {c['n_new']}; missing in new {c['n_missing_in_new']}; "
          f"edited {c['n_edited']}; re-scored {c['n_rescored']}; replies added {c['n_reply_added']}")
    print(f"star mix of new reviews: {new_review_score_mix(c['new_reviews'])}")
    if c["new_snapshot_may_be_partial"]:
        print("WARNING: new snapshot starts later than the old one; 'missing' counts are unreliable.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="rating_intel", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("clean", help="validate and clean a raw run folder")
    c.add_argument("run_dir"); c.add_argument("--out", default="data/processed"); c.set_defaults(fn=cmd_clean)
    an = sub.add_parser("analyze", help="classify and analyse a cleaned snapshot")
    an.add_argument("csv"); an.add_argument("--since"); an.add_argument("--split-date")
    an.add_argument("--prev", help="previous cleaned snapshot to compare with"); an.add_argument("--out")
    an.add_argument("--llm", action="store_true", help="add local-LLM labels for reviews the rules missed (needs .env)")
    an.add_argument("--env-file", default=".env")
    an.add_argument("--manifest", help="raw run manifest.json (adds the Play listing rating to the headline)")
    an.set_defaults(fn=cmd_analyze)
    st = sub.add_parser("status", help="answer 'How are our ratings?' in a few lines")
    st.add_argument("csv"); st.add_argument("--days", type=int, default=90); st.add_argument("--manifest")
    st.set_defaults(fn=cmd_status)
    cp = sub.add_parser("compare", help="compare two cleaned snapshots")
    cp.add_argument("old"); cp.add_argument("new"); cp.set_defaults(fn=cmd_compare)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
