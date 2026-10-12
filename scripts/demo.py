"""Offline reproduction of the submission snapshot: python scripts/demo.py."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rating_intel.pipeline import run_analysis
from rating_intel.status import headline
from rating_intel.pipeline import load_clean

def main():
    csv = ROOT / "data/processed/run_20261010T203205Z/reviews_clean.csv"
    manifest = ROOT / "data/raw/run_20261010T203205Z/manifest.json"
    out = ROOT / "reports/analysis_run_20261010T203205Z"
    if not csv.is_file() or not manifest.is_file():
        raise SystemExit("Original snapshot missing. Download the complete submission package; see README.")
    print("\n".join(headline(load_clean(csv), manifest_path=manifest)["lines"]))
    info = run_analysis(csv, out, since="2025-10-10", split_date="2026-04-10", manifest_path=manifest)
    print(f"\nReproduced {info['window_reviews']} reviews; {info['pool_1to3']} low-star reviews.")
    print(f"Report: {out / 'report.md'}")
    return 0
if __name__ == "__main__":
    sys.exit(main())
