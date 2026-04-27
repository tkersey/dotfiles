#!/usr/bin/env python3
"""
render_hotspot_table.py — Consume structured perf.profile.* JSONL logs and emit
the ranked hotspot table that extreme-software-optimization consumes.

Usage:
    render_hotspot_table.py profile.jsonl [--top N] [--by cumulative|count|p95]
                                          [--evidence-prefix PATH]

Input contract: one JSON object per line. Event types:
    {"event":"perf.profile.span_summary",
     "span" | "span_name": "X",
     "cumulative_us" | "cumulative": 123, "count": 45,
     "p50_us" | "p50": ..., "p95_us" | "p95": ...,
     "category":"CPU|IO|alloc|lock", "evidence":"flame.svg:0.23"}
    {"event":"perf.profile.hypothesis_evaluated","name":"...","verdict":"supports|rejects","evidence":"..."}

Either naming convention is accepted (matches the JSONL contract documented in the main skill readme).

Output: a markdown hotspot table + optional hypothesis ledger, to stdout.
Missing category defaults to "CPU". Missing evidence becomes "-" (reviewer flags).
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def load_events(path: Path) -> list[dict]:
    events: list[dict] = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"WARN: skipping line {i}: {e}", file=sys.stderr)
    return events


def format_us(value: float) -> str:
    value = float(value)
    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}s"
    if value >= 1_000:
        return f"{value/1_000:.1f}ms"
    return f"{value:.0f}µs"


def field(s: dict, *names: str, default=0):
    """Return the first present field from names. Accepts both `p95` and `p95_us`
    naming conventions, and `span` / `span_name`."""
    for n in names:
        if n in s and s[n] is not None:
            return s[n]
    return default


def numeric_field(s: dict, *names: str, default=0.0) -> float:
    value = field(s, *names, default=default)
    try:
        return float(value)
    except (TypeError, ValueError) as e:
        joined = " | ".join(names)
        raise ValueError(f"field {joined} must be numeric, got {value!r}") from e


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", type=Path)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--by", choices=["cumulative", "count", "p95"], default="cumulative")
    ap.add_argument("--evidence-prefix", default="")
    args = ap.parse_args(argv[1:])

    events = load_events(args.log)
    spans = [e for e in events if e.get("event") == "perf.profile.span_summary"]
    hyps = [e for e in events if e.get("event") == "perf.profile.hypothesis_evaluated"]
    if not spans:
        print("ERROR: no perf.profile.span_summary events found", file=sys.stderr)
        return 2

    key_map = {
        "cumulative": lambda s: numeric_field(s, "cumulative_us", "cumulative"),
        "count":      lambda s: numeric_field(s, "count"),
        "p95":        lambda s: numeric_field(s, "p95_us", "p95"),
    }
    try:
        spans.sort(key=key_map[args.by], reverse=True)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(f"# Hotspot Table — ranked by {args.by}\n")
    print("| Rank | Location | Metric | Value | Category | Evidence |")
    print("|------|----------|--------|-------|----------|----------|")
    for rank, s in enumerate(spans[: args.top], 1):
        loc = field(s, "span", "span_name", default="?")
        if args.by == "count":
            metric, value = "count", str(int(numeric_field(s, "count")))
        elif args.by == "p95":
            metric, value = "p95", format_us(numeric_field(s, "p95_us", "p95"))
        else:
            metric, value = "cumulative", format_us(numeric_field(s, "cumulative_us", "cumulative"))
        cat = s.get("category", "CPU")
        ev = s.get("evidence", "-")
        if args.evidence_prefix and ev != "-":
            ev = f"{args.evidence_prefix.rstrip('/')}/{ev}"
        print(f"| {rank} | `{loc}` | {metric} | {value} | {cat} | {ev} |")

    if hyps:
        print("\n## Hypothesis Ledger\n")
        for h in hyps:
            name = h.get("name", "?")
            verdict = h.get("verdict", "?")
            ev = h.get("evidence", "-")
            print(f"- **{name}** → `{verdict}` — {ev}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
