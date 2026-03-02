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

  # Optional mesh-truth and deadlock hooks
  uv run codex/skills/mesh/references/lane_completeness_lint.py \
    --check full \
    --require-spawn-substrate \
    --deps-csv .mesh/wave-deps.csv \
    .mesh/*.exec.out.csv
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


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


def _parse_dep_cells(raw: str) -> list[str]:
    parts = [p.strip() for p in raw.replace(";", ",").split(",")]
    return [p for p in parts if p]


def _parse_truthy(raw: str) -> bool:
    text = raw.strip().lower()
    return text in {"1", "true", "yes", "y", "on"}


def lint_deadlock_csvs(paths: Iterable[Path]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for path in paths:
        rows = _read_csv_rows(path)
        header_errs = _require_headers(path, rows, {"id"})
        if header_errs:
            errors.extend(header_errs)
            continue

        ids = {row.get("id", "").strip() for row in rows if row.get("id", "").strip()}
        deps_by_id: dict[str, list[str]] = {}

        for row in rows:
            unit_id = row.get("id", "").strip()
            if not unit_id:
                continue
            deps = _parse_dep_cells(row.get("depends_on", ""))
            deps_by_id[unit_id] = deps

            unknown = sorted([dep for dep in deps if dep not in ids])
            if unknown:
                errors.append(
                    f"{path}:{unit_id}: unknown deps: {', '.join(unknown)}"
                )

            if _parse_truthy(row.get("interactive_lead", "")) and deps:
                errors.append(
                    f"{path}:{unit_id}: interactive_lead waits on deps ({', '.join(deps)})"
                )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str, stack: list[str]) -> None:
            if node in visited or node not in deps_by_id:
                return
            if node in visiting:
                loop = " -> ".join(stack + [node])
                errors.append(f"{path}: cycle detected: {loop}")
                return
            visiting.add(node)
            for dep in deps_by_id.get(node, []):
                visit(dep, stack + [node])
            visiting.remove(node)
            visited.add(node)

        for node in sorted(deps_by_id.keys()):
            visit(node, [])

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
    parser.add_argument(
        "--require-spawn-substrate",
        action="store_true",
        help="Fail if full-check rows do not include spawn_substrate=spawn_agents_on_csv.",
    )
    parser.add_argument(
        "--expected-spawn-substrate",
        default="spawn_agents_on_csv",
        help="Expected spawn substrate value when --require-spawn-substrate is enabled.",
    )
    parser.add_argument(
        "--deps-csv",
        action="append",
        default=[],
        help="Optional dependency CSV for deadlock checks (headers: id,depends_on,interactive_lead). Repeatable.",
    )
    parser.add_argument("csv_paths", nargs="+", help="One or more CSV paths")
    args = parser.parse_args()

    paths = [Path(p).expanduser() for p in args.csv_paths]

    ok, errs = lint_candidate(paths) if args.check == "candidate" else lint_full(paths)

    if args.check == "full" and args.require_spawn_substrate:
        for path in paths:
            rows = _read_csv_rows(path)
            if not rows:
                continue
            if "spawn_substrate" not in rows[0]:
                errs.append(
                    f"{path}: missing headers: spawn_substrate (required by --require-spawn-substrate)"
                )
                continue
            bad = sorted(
                {
                    row.get("id", "").strip() or "<unknown>"
                    for row in rows
                    if row.get("spawn_substrate", "").strip()
                    != args.expected_spawn_substrate
                }
            )
            if bad:
                errs.append(
                    f"{path}: spawn_substrate mismatch for ids: {', '.join(bad)}"
                )

    deps_paths = [Path(p).expanduser() for p in args.deps_csv]
    if deps_paths:
        dep_ok, dep_errs = lint_deadlock_csvs(deps_paths)
        if not dep_ok:
            errs.extend(dep_errs)

    ok = len(errs) == 0
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
