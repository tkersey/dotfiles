#!/usr/bin/env -S uv run python
"""Reproducible performance harness for seq.py workloads."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Variant:
    label: str
    script: Path


@dataclass(frozen=True)
class Workload:
    name: str
    args: list[str]


@dataclass
class SampleResult:
    workload: str
    variant: str
    seconds: float


def pct(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    values = sorted(values)
    k = (len(values) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(values) - 1)
    if lo == hi:
        return values[lo]
    frac = k - lo
    return values[lo] + (values[hi] - values[lo]) * frac


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {
            "n": 0,
            "min": 0.0,
            "p50": 0.0,
            "p95": 0.0,
            "p99": 0.0,
            "max": 0.0,
            "mean": 0.0,
        }
    mean = sum(values) / len(values)
    return {
        "n": len(values),
        "min": min(values),
        "p50": pct(values, 50),
        "p95": pct(values, 95),
        "p99": pct(values, 99),
        "max": max(values),
        "mean": mean,
    }


def run_once(script: Path, args: list[str]) -> float:
    cmd = [sys.executable, str(script), *args]
    t0 = time.perf_counter()
    proc = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    dt = time.perf_counter() - t0
    if proc.returncode != 0:
        err = (proc.stderr or "").strip()
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\n{err}"
        )
    return dt


def build_workloads(
    names: list[str], root: Path, specs_dir: Path, token_top: int
) -> list[Workload]:
    known: dict[str, Workload] = {
        "skills-rank": Workload(
            name="skills-rank",
            args=[
                "query",
                "--root",
                str(root),
                "--spec",
                f"@{specs_dir / 'skills-rank.json'}",
            ],
        ),
        "tokens-top-days": Workload(
            name="tokens-top-days",
            args=[
                "query",
                "--root",
                str(root),
                "--spec",
                f"@{specs_dir / 'tokens-top-days.json'}",
            ],
        ),
        "token-usage": Workload(
            name="token-usage",
            args=["token-usage", "--root", str(root), "--top", str(token_top)],
        ),
    }
    out: list[Workload] = []
    for name in names:
        w = known.get(name)
        if not w:
            raise ValueError(
                f"unknown workload '{name}' (valid: {', '.join(sorted(known))})"
            )
        out.append(w)
    return out


def format_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "(no results)"
    cols = [
        "workload",
        "variant",
        "n",
        "min",
        "p50",
        "p95",
        "p99",
        "max",
        "mean",
        "delta_sec_vs_baseline",
        "delta_pct_vs_baseline",
    ]
    widths = {c: len(c) for c in cols}
    for r in rows:
        for c in cols:
            v = r.get(c, "")
            s = f"{v:.4f}" if isinstance(v, float) else str(v)
            widths[c] = max(widths[c], len(s))
    lines = []
    lines.append("  ".join(c.ljust(widths[c]) for c in cols))
    lines.append("  ".join("-" * widths[c] for c in cols))
    for r in rows:
        parts = []
        for c in cols:
            v = r.get(c, "")
            s = f"{v:.4f}" if isinstance(v, float) else str(v)
            parts.append(s.ljust(widths[c]))
        lines.append("  ".join(parts))
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reproducible seq performance harness")
    p.add_argument(
        "--root",
        default=str(Path.home() / ".codex" / "sessions"),
        help="sessions root (prefer a fixed snapshot for reproducibility)",
    )
    p.add_argument(
        "--candidate",
        default=str(Path(__file__).resolve().parent / "seq.py"),
        help="candidate seq.py path (default: this skill's scripts/seq.py)",
    )
    p.add_argument(
        "--baseline",
        help="optional baseline seq.py path for A/B delta reporting",
    )
    p.add_argument("--warmup", type=int, default=1, help="warmup runs per workload")
    p.add_argument("--samples", type=int, default=5, help="measured runs per workload")
    p.add_argument(
        "--workloads",
        default="skills-rank,tokens-top-days,token-usage",
        help="comma-separated workloads: skills-rank,tokens-top-days,token-usage",
    )
    p.add_argument(
        "--token-top",
        type=int,
        default=10,
        help="--top value used for token-usage workload",
    )
    p.add_argument("--json", action="store_true", help="emit JSON report")
    p.add_argument("--output", help="optional output file path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.warmup < 0 or args.samples <= 0:
        raise SystemExit("--warmup must be >= 0 and --samples must be > 0")

    root = Path(args.root).expanduser().resolve()
    candidate = Path(args.candidate).expanduser().resolve()
    baseline = Path(args.baseline).expanduser().resolve() if args.baseline else None
    if not root.exists():
        raise SystemExit(f"root does not exist: {root}")
    if not candidate.exists():
        raise SystemExit(f"candidate does not exist: {candidate}")
    if baseline and not baseline.exists():
        raise SystemExit(f"baseline does not exist: {baseline}")

    specs_dir = Path(__file__).resolve().parents[1] / "specs"
    workload_names = [x.strip() for x in args.workloads.split(",") if x.strip()]
    workloads = build_workloads(workload_names, root, specs_dir, args.token_top)

    variants = [Variant(label="candidate", script=candidate)]
    if baseline:
        variants = [Variant(label="baseline", script=baseline), *variants]

    samples: list[SampleResult] = []

    # Run warmup per workload/variant; then measured runs in round-robin order.
    for workload in workloads:
        for _ in range(args.warmup):
            for variant in variants:
                run_once(variant.script, workload.args)

        for _ in range(args.samples):
            for variant in variants:
                dt = run_once(variant.script, workload.args)
                samples.append(
                    SampleResult(
                        workload=workload.name, variant=variant.label, seconds=dt
                    )
                )

    grouped: dict[tuple[str, str], list[float]] = {}
    for s in samples:
        grouped.setdefault((s.workload, s.variant), []).append(s.seconds)

    baseline_means: dict[str, float] = {}
    if baseline:
        for workload in workloads:
            key = (workload.name, "baseline")
            vals = grouped.get(key, [])
            baseline_means[workload.name] = stats(vals)["mean"] if vals else 0.0

    report_rows: list[dict[str, Any]] = []
    for workload in workloads:
        for variant in variants:
            vals = grouped.get((workload.name, variant.label), [])
            s = stats(vals)
            row: dict[str, Any] = {
                "workload": workload.name,
                "variant": variant.label,
                **s,
                "delta_sec_vs_baseline": "",
                "delta_pct_vs_baseline": "",
            }
            if baseline and variant.label != "baseline":
                b = baseline_means.get(workload.name, 0.0)
                if b > 0:
                    delta = s["mean"] - b
                    row["delta_sec_vs_baseline"] = delta
                    row["delta_pct_vs_baseline"] = (delta / b) * 100.0
            report_rows.append(row)

    payload = {
        "root": str(root),
        "candidate": str(candidate),
        "baseline": str(baseline) if baseline else None,
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": sys.platform,
        "warmup": args.warmup,
        "samples": args.samples,
        "workloads": [w.name for w in workloads],
        "workload_args": {w.name: w.args for w in workloads},
        "results": report_rows,
    }

    text = json.dumps(payload, indent=2) if args.json else format_table(report_rows)
    if args.output:
        Path(args.output).write_text(text + ("\n" if not text.endswith("\n") else ""))
    else:
        print(text)


if __name__ == "__main__":
    main()
