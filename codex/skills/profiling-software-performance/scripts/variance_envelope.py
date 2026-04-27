#!/usr/bin/env python3
"""
variance_envelope.py — Check whether a set of repeated same-host runs
satisfies the variance envelope from BUDGETS.md (≤ 10% drift on p95).

Usage:
    variance_envelope.py run1.json run2.json run3.json [...]

Input format: hyperfine JSON (`hyperfine --export-json`), or JSON with a top-level
`"p95_ms"` field per file. Missing fields cause exit 2.

Percentiles use nearest-rank indexing: ceil(p*N)-1, clamped into bounds.

Verdict:
    ≤  5% max drift  → "✓ STABLE"
    ≤ 10% max drift  → "✓ NOISE"
    ≤ 20% max drift  → "⚠ INVESTIGATE"
    >  20% max drift → "✗ ESCALATE"
"""

from __future__ import annotations
import json
import math
import sys
from pathlib import Path


def nearest_rank(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = max(0, min(math.ceil(p * len(ordered)) - 1, len(ordered) - 1))
    return ordered[idx]


def median_value(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def extract_p95(obj: dict) -> float | None:
    if "p95_ms" in obj:
        return float(obj["p95_ms"])
    # hyperfine format
    results = obj.get("results") or []
    if results:
        times = sorted(results[0].get("times") or [])
        if times:
            p95 = nearest_rank([float(t) for t in times], 0.95)
            return None if p95 is None else p95 * 1000.0  # sec → ms
    return None


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    p95s: list[tuple[str, float]] = []
    for path in argv[1:]:
        data = json.loads(Path(path).read_text())
        p95 = extract_p95(data)
        if p95 is None:
            print(f"ERROR: could not extract p95 from {path}", file=sys.stderr)
            return 2
        p95s.append((path, p95))

    median = median_value([p for _, p in p95s])
    if median == 0:
        max_abs = max(abs(p) for _, p in p95s)
        if max_abs == 0:
            max_drift = 0.0
        else:
            print("ERROR: median p95 is zero but at least one run is non-zero; relative drift is undefined", file=sys.stderr)
            return 2
    else:
        max_drift = max(abs(p - median) / median for _, p in p95s)

    print(f"{'file':40s}  p95_ms")
    for path, p in p95s:
        print(f"{path:40s}  {p:8.2f}")
    print(f"\nMedian p95: {median:.2f} ms")
    print(f"Max drift:  {max_drift*100:.1f}%")

    sys.stdout.flush()
    if max_drift <= 0.05:
        print("Verdict: STABLE")
        return 0
    if max_drift <= 0.10:
        print("Verdict: NOISE (within envelope)")
        return 0
    if max_drift <= 0.20:
        print("Verdict: INVESTIGATE — p95 drift > 10%")
        return 1
    print("Verdict: ESCALATE — p95 drift > 20%")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
