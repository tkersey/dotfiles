#!/usr/bin/env -S uv run python
"""Mesh lane completeness lint (fail-closed).

This catches the most common orchestration miss:
- concurrency was used, but the run only executed lane=coder rows.

Usage:

  # Candidate wave must have coder x2 + reducer x1 per unit
  uv run codex/skills/mesh/references/lane_completeness_lint.py \
    --check candidate .mesh/wave1.csv

  # A full mesh run must have downstream lanes too
  uv run codex/skills/mesh/references/lane_completeness_lint.py \
    --check full .mesh/*.exec.out.csv
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


LANES = {
    "coder",
    "reducer",
    "locksmith",
    "applier",
    "prover",
    "fixer",
    "integrator",
}


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("missing CSV header")
        rows: list[dict[str, str]] = []
        for row in reader:
            # Normalize None -> "" for safety.
            rows.append({k: ("" if v is None else v) for k, v in row.items()})
        return rows


def _require_headers(
    path: Path, rows: list[dict[str, str]], required: set[str]
) -> list[str]:
    if not rows:
        return [f"{path}: no rows"]
    missing = sorted(required - set(rows[0].keys()))
    if missing:
        return [f"{path}: missing headers: {', '.join(missing)}"]
    return []


def _collect(rows: list[dict[str, str]]):
    lanes = []
    lanes_by_unit: dict[str, Counter[str]] = defaultdict(Counter)

    for row in rows:
        unit_id = row.get("id", "").strip()
        lane = row.get("lane", "").strip()
        if unit_id:
            lanes_by_unit[unit_id][lane] += 1
        lanes.append(lane)

    return Counter(lanes), lanes_by_unit


def lint_candidate(paths: list[Path]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    all_rows: list[dict[str, str]] = []

    for path in paths:
        rows = _read_csv_rows(path)
        errors.extend(
            _require_headers(
                path, rows, {"id", "lane", "candidate_id", "triplet_index"}
            )
        )
        all_rows.extend(rows)

    if errors:
        return False, errors

    lane_counts, lanes_by_unit = _collect(all_rows)

    unknown = sorted([lane for lane in lane_counts if lane and lane not in LANES])
    if unknown:
        errors.append(f"unknown lane values: {', '.join(unknown)}")

    disallowed = sorted(
        [lane for lane in lane_counts if lane and lane not in {"coder", "reducer"}]
    )
    if disallowed:
        errors.append(
            "candidate check expects only coder/reducer lanes; found: "
            + ", ".join(disallowed)
        )

    for unit_id, by_lane in sorted(lanes_by_unit.items()):
        if by_lane["coder"] < 2 or by_lane["reducer"] < 1:
            errors.append(
                f"{unit_id}: candidate cohort incomplete (need coder>=2 and reducer>=1; got coder={by_lane['coder']}, reducer={by_lane['reducer']})"
            )

    return (len(errors) == 0), errors


def lint_full(paths: list[Path]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    all_rows: list[dict[str, str]] = []

    for path in paths:
        rows = _read_csv_rows(path)
        errors.extend(_require_headers(path, rows, {"id", "lane"}))
        all_rows.extend(rows)

    if errors:
        return False, errors

    lane_counts, lanes_by_unit = _collect(all_rows)

    if lane_counts and set(lane_counts.keys()) <= {"", "coder"}:
        errors.append(
            "coder-only run detected (this is not lane-complete mesh orchestration)"
        )

    unknown = sorted([lane for lane in lane_counts if lane and lane not in LANES])
    if unknown:
        errors.append(f"unknown lane values: {', '.join(unknown)}")

    required_per_unit = {
        "coder",
        "reducer",
        "locksmith",
        "applier",
        "prover",
        "fixer",
        "integrator",
    }

    for unit_id, by_lane in sorted(lanes_by_unit.items()):
        missing = sorted([l for l in required_per_unit if by_lane[l] == 0])
        if missing:
            errors.append(f"{unit_id}: missing lanes: {', '.join(missing)}")
        if by_lane["coder"] < 2 or by_lane["reducer"] < 1:
            errors.append(
                f"{unit_id}: candidate cohort incomplete (need coder>=2 and reducer>=1; got coder={by_lane['coder']}, reducer={by_lane['reducer']})"
            )

    return (len(errors) == 0), errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mesh lane completeness lint (fail-closed)"
    )
    parser.add_argument(
        "--check",
        choices=["candidate", "full"],
        required=True,
        help="Which invariants to enforce.",
    )
    parser.add_argument(
        "--collapsed-ok",
        action="store_true",
        help="Waive lane completeness failures (explicit collapsed-path override).",
    )
    parser.add_argument("csv_paths", nargs="+", help="One or more CSV paths")
    args = parser.parse_args()

    paths = [Path(p).expanduser() for p in args.csv_paths]

    ok, errs = lint_candidate(paths) if args.check == "candidate" else lint_full(paths)

    if ok:
        print("lane_completeness_lint: PASS")
        return 0

    if args.collapsed_ok:
        print("lane_completeness_lint: WAIVED (collapsed path override)")
        for e in errs:
            print(f"- {e}")
        return 0

    print("lane_completeness_lint: FAIL")
    for e in errs:
        print(f"- {e}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
