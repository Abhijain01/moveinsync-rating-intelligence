"""MoveInSync Rating Intelligence: a reproducible, free, deterministic pipeline for Google Play review analysis.

Stages: collect (scripts/ingest.py) -> clean -> classify -> trends/spikes -> snapshot compare -> report.
The deterministic rule classifier is the baseline; an optional local-LLM layer can add labels for reviews
the rules miss, with strict output validation and automatic fallback. No paid API is required or implemented.
"""
__version__ = "1.0.0"
