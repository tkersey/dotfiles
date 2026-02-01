#!/usr/bin/env python3
"""
Summarize benchmark samples with basic statistics and percentiles.

Usage examples:
  cat samples.txt | bench_stats.py
  bench_stats.py --input samples.txt --unit ms
  bench_stats.py --input samples.txt --scale 1000 --unit us
  bench_stats.py --input samples.txt --all
"""

from __future__ import annotations

import argparse
import math
import re
import statistics
import sys
from pathlib import Path
from typing import Iterable, List

NUMBER_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def parse_numbers(lines: Iterable[str], use_all: bool) -> List[float]:
    values: List[float] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        matches = NUMBER_RE.findall(stripped)
        if not matches:
            continue
        if use_all:
            for match in matches:
                values.append(float(match))
        else:
            values.append(float(matches[0]))
    return values


def percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        raise ValueError("No data")
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize benchmark samples.")
    parser.add_argument("--input", help="Input file path (default: stdin)")
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor")
    parser.add_argument("--unit", default="", help="Unit label")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Parse all numbers in each line instead of only the first",
    )
    return parser


def format_value(value: float, unit: str) -> str:
    suffix = f" {unit}" if unit else ""
    return f"{value:.6g}{suffix}"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.input:
        lines = Path(args.input).read_text().splitlines()
    else:
        lines = sys.stdin.read().splitlines()

    values = [v * args.scale for v in parse_numbers(lines, args.all)]
    if not values:
        print("No numeric samples found.")
        return 1

    values.sort()
    count = len(values)
    mean = statistics.fmean(values)
    median = statistics.median(values)
    stdev = statistics.pstdev(values) if count > 1 else 0.0

    report = {
        "count": str(count),
        "min": format_value(values[0], args.unit),
        "p50": format_value(percentile(values, 50), args.unit),
        "p90": format_value(percentile(values, 90), args.unit),
        "p95": format_value(percentile(values, 95), args.unit),
        "p99": format_value(percentile(values, 99), args.unit),
        "max": format_value(values[-1], args.unit),
        "mean": format_value(mean, args.unit),
        "median": format_value(median, args.unit),
        "stdev": format_value(stdev, args.unit),
    }

    print("count  :", report["count"])
    print("min    :", report["min"])
    print("p50    :", report["p50"])
    print("p90    :", report["p90"])
    print("p95    :", report["p95"])
    print("p99    :", report["p99"])
    print("max    :", report["max"])
    print("mean   :", report["mean"])
    print("median :", report["median"])
    print("stdev  :", report["stdev"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
