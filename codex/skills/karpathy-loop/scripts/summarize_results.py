#!/usr/bin/env python3
"""Summarize a Karpathy Loop results.tsv file.

Usage:
    python scripts/summarize_results.py templates/results.tsv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


def parse_score(value: str) -> float | None:
    value = (value or "").strip().replace("%", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: summarize_results.py <results.tsv>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    rows = list(csv.DictReader(path.open(newline=""), delimiter="\t"))
    if not rows:
        print("No experiment rows found.")
        return 0

    kept = [r for r in rows if (r.get("decision") or "").lower() == "keep"]
    rejected = [r for r in rows if (r.get("decision") or "").lower() == "reject"]
    baseline = next((r for r in rows if (r.get("decision") or "").lower() == "baseline"), rows[0])
    final = rows[-1]

    baseline_score = parse_score(baseline.get("candidate_score", "")) or parse_score(baseline.get("baseline_score", ""))
    final_score = parse_score(final.get("candidate_score", "")) or parse_score(final.get("baseline_score", ""))

    print("Karpathy Loop Summary")
    print("======================")
    print(f"Experiments: {len(rows) - 1 if baseline else len(rows)}")
    print(f"Kept: {len(kept)}")
    print(f"Rejected: {len(rejected)}")
    if baseline_score is not None:
        print(f"Baseline score: {baseline_score:g}")
    if final_score is not None:
        print(f"Final score: {final_score:g}")
    if baseline_score is not None and final_score is not None:
        print(f"Improvement: {final_score - baseline_score:+g}")

    if kept:
        print("\nKept changes:")
        for row in kept:
            print(f"- {row.get('experiment_id')}: {row.get('mutation_summary')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
