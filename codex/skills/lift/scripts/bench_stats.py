#!/usr/bin/env python3
"""
Summarize benchmark samples with basic statistics and percentiles.

Usage examples:
  cat samples.txt | bench_stats.py
  bench_stats.py --input samples.txt --unit ms
  bench_stats.py --input samples.txt --scale 1000 --unit us
  bench_stats.py --input samples.txt --all
  bench_stats.py --input samples.txt --json
  bench_stats.py --input baseline.txt --compare variant.txt --unit ms
  bench_stats.py --input baseline.txt --compare variant.txt --ci-samples 2000
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics
import sys
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Tuple

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


def read_lines(path: Optional[str]) -> List[str]:
    if path:
        return Path(path).read_text().splitlines()
    return sys.stdin.read().splitlines()


def compute_report(values: List[float], unit: str) -> dict:
    values.sort()
    count = len(values)
    mean = statistics.fmean(values)
    median = statistics.median(values)
    stdev = statistics.pstdev(values) if count > 1 else 0.0
    return {
        "count": count,
        "min": values[0],
        "p50": percentile(values, 50),
        "p90": percentile(values, 90),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "max": values[-1],
        "mean": mean,
        "median": median,
        "stdev": stdev,
        "unit": unit,
    }


def bootstrap_ci_delta(
    baseline: List[float],
    variant: List[float],
    stat_fn: Callable[[List[float]], float],
    samples: int,
    alpha: float,
    rng: random.Random,
) -> Tuple[float, float]:
    if samples <= 0:
        raise ValueError("samples must be > 0")

    n0 = len(baseline)
    n1 = len(variant)
    if n0 == 0 or n1 == 0:
        raise ValueError("empty input")

    deltas: List[float] = []
    for _ in range(samples):
        b = [baseline[rng.randrange(n0)] for _ in range(n0)]
        v = [variant[rng.randrange(n1)] for _ in range(n1)]
        deltas.append(stat_fn(v) - stat_fn(b))

    deltas.sort()
    lo = percentile(deltas, (alpha / 2.0) * 100.0)
    hi = percentile(deltas, (1.0 - (alpha / 2.0)) * 100.0)
    return lo, hi


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize benchmark samples.")
    parser.add_argument("--input", help="Input file path (default: stdin)")
    parser.add_argument(
        "--compare",
        help="Variant input file path to compare against baseline (--input or stdin)",
    )
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor")
    parser.add_argument("--unit", default="", help="Unit label")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Parse all numbers in each line instead of only the first",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON (numbers stay unformatted)",
    )
    parser.add_argument(
        "--ci-samples",
        type=int,
        default=None,
        help="Bootstrap samples for compare-mode CI (default: 1000; 0 disables)",
    )
    parser.add_argument(
        "--ci-alpha",
        type=float,
        default=0.05,
        help="Alpha for compare-mode CI (default: 0.05 => 95%% CI)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for compare-mode bootstrap (default: random)",
    )
    return parser


def format_value(value: float, unit: str) -> str:
    suffix = f" {unit}" if unit else ""
    return f"{value:.6g}{suffix}"


def format_delta(value: float, unit: str) -> str:
    suffix = f" {unit}" if unit else ""
    return f"{value:+.6g}{suffix}"


def format_pct(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.3g}%"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.compare:
        if args.ci_samples is None:
            args.ci_samples = 1000
        if args.ci_samples < 0:
            print("error: --ci-samples must be >= 0", file=sys.stderr)
            return 2
        if not (0.0 < args.ci_alpha < 1.0):
            print("error: --ci-alpha must be in (0, 1)", file=sys.stderr)
            return 2

        baseline_lines = read_lines(args.input)
        variant_lines = Path(args.compare).read_text().splitlines()

        baseline_values = [
            v * args.scale for v in parse_numbers(baseline_lines, args.all)
        ]
        variant_values = [
            v * args.scale for v in parse_numbers(variant_lines, args.all)
        ]

        if not baseline_values:
            print("No numeric baseline samples found.")
            return 1
        if not variant_values:
            print("No numeric variant samples found.")
            return 1

        baseline_report = compute_report(baseline_values, args.unit)
        variant_report = compute_report(variant_values, args.unit)

        keys = ["min", "p50", "p90", "p95", "p99", "max", "mean", "median", "stdev"]
        delta: dict = {k: (variant_report[k] - baseline_report[k]) for k in keys}
        delta_pct: dict = {}
        for k in keys:
            b = float(baseline_report[k])
            if b == 0.0:
                delta_pct[k] = None
            else:
                delta_pct[k] = (delta[k] / b) * 100.0

        ci: dict = {}
        if args.ci_samples > 0:
            rng = random.Random(args.seed)

            def stat_p(p: float) -> Callable[[List[float]], float]:
                def _stat(values: List[float]) -> float:
                    vals = list(values)
                    vals.sort()
                    return percentile(vals, p)

                return _stat

            for name, stat_fn in (
                ("p50", stat_p(50)),
                ("p95", stat_p(95)),
                ("p99", stat_p(99)),
            ):
                lo, hi = bootstrap_ci_delta(
                    baseline_values,
                    variant_values,
                    stat_fn=stat_fn,
                    samples=int(args.ci_samples),
                    alpha=float(args.ci_alpha),
                    rng=rng,
                )
                ci[name] = {"lo": lo, "hi": hi}

        if args.json:
            out = {
                "baseline": baseline_report,
                "variant": variant_report,
                "delta": delta,
                "delta_pct": delta_pct,
                "ci": {
                    "samples": int(args.ci_samples),
                    "alpha": float(args.ci_alpha),
                    "delta": ci,
                },
            }
            print(json.dumps(out, separators=(",", ":")))
            return 0

        def fmt_report(report_numeric: dict) -> dict:
            return {
                "count": str(report_numeric["count"]),
                "min": format_value(report_numeric["min"], args.unit),
                "p50": format_value(report_numeric["p50"], args.unit),
                "p90": format_value(report_numeric["p90"], args.unit),
                "p95": format_value(report_numeric["p95"], args.unit),
                "p99": format_value(report_numeric["p99"], args.unit),
                "max": format_value(report_numeric["max"], args.unit),
                "mean": format_value(report_numeric["mean"], args.unit),
                "median": format_value(report_numeric["median"], args.unit),
                "stdev": format_value(report_numeric["stdev"], args.unit),
            }

        b = fmt_report(baseline_report)
        v = fmt_report(variant_report)

        print("baseline")
        print("count  :", b["count"])
        print("min    :", b["min"])
        print("p50    :", b["p50"])
        print("p90    :", b["p90"])
        print("p95    :", b["p95"])
        print("p99    :", b["p99"])
        print("max    :", b["max"])
        print("mean   :", b["mean"])
        print("median :", b["median"])
        print("stdev  :", b["stdev"])
        print("")
        print("variant")
        print("count  :", v["count"])
        print("min    :", v["min"])
        print("p50    :", v["p50"])
        print("p90    :", v["p90"])
        print("p95    :", v["p95"])
        print("p99    :", v["p99"])
        print("max    :", v["max"])
        print("mean   :", v["mean"])
        print("median :", v["median"])
        print("stdev  :", v["stdev"])
        print("")
        print("delta (variant - baseline)")
        for k in keys:
            d = format_delta(float(delta[k]), args.unit)
            p = format_pct(delta_pct[k])
            print(f"{k:6}: {d} ({p})")

        if ci:
            ci_pct = int(round((1.0 - float(args.ci_alpha)) * 100.0))
            print("")
            print(f"ci{ci_pct} (bootstrap; samples={args.ci_samples})")
            for k in ("p50", "p95", "p99"):
                lo = format_value(float(ci[k]["lo"]), args.unit)
                hi = format_value(float(ci[k]["hi"]), args.unit)
                print(f"{k:6}: [{lo}, {hi}]")

        return 0

    lines = read_lines(args.input)

    values = [v * args.scale for v in parse_numbers(lines, args.all)]
    if not values:
        print("No numeric samples found.")
        return 1

    report_numeric = compute_report(values, args.unit)

    if args.json:
        print(json.dumps(report_numeric, separators=(",", ":")))
        return 0

    report = {
        "count": str(report_numeric["count"]),
        "min": format_value(report_numeric["min"], args.unit),
        "p50": format_value(report_numeric["p50"], args.unit),
        "p90": format_value(report_numeric["p90"], args.unit),
        "p95": format_value(report_numeric["p95"], args.unit),
        "p99": format_value(report_numeric["p99"], args.unit),
        "max": format_value(report_numeric["max"], args.unit),
        "mean": format_value(report_numeric["mean"], args.unit),
        "median": format_value(report_numeric["median"], args.unit),
        "stdev": format_value(report_numeric["stdev"], args.unit),
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
