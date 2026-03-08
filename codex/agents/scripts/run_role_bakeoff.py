#!/usr/bin/env -S uv run --with pyyaml python
"""Validate and render the frozen custom-role bakeoff suite."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


REQUIRED_CASE_KEYS = {
    "id",
    "role",
    "goal",
    "context",
    "instructions",
    "acceptance_checks",
    "metrics",
}


def load_suite(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("suite root must be a mapping")
    return data


def validate_suite(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if not isinstance(data.get("suite_id"), str):
        errors.append("suite_id must be a string")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            errors.append("each case must be a mapping")
            continue
        missing = sorted(REQUIRED_CASE_KEYS - set(case))
        if missing:
            errors.append(f"case missing keys: {', '.join(missing)}")
            continue
        case_id = case["id"]
        if case_id in seen_ids:
            errors.append(f"duplicate case id: {case_id}")
        seen_ids.add(case_id)
        if not isinstance(case["acceptance_checks"], list) or not case["acceptance_checks"]:
            errors.append(f"{case_id}: acceptance_checks must be a non-empty list")
        if not isinstance(case["metrics"], list) or not case["metrics"]:
            errors.append(f"{case_id}: metrics must be a non-empty list")
    return errors


def render_markdown(data: dict) -> str:
    lines = [f"# {data['suite_id']}", ""]
    lines.append("Frozen bakeoff cases for baseline-vs-redesign comparison.")
    lines.append("")
    for case in data["cases"]:
        lines.append(f"## {case['id']} ({case['role']})")
        lines.append(f"- Goal: {case['goal']}")
        lines.append(f"- Context: {case['context']}")
        lines.append("- Acceptance:")
        for item in case["acceptance_checks"]:
            lines.append(f"  - {item}")
        lines.append("- Metrics:")
        for item in case["metrics"]:
            lines.append(f"  - {item}")
        lines.append("- Instructions:")
        lines.append("")
        lines.append(case["instructions"].rstrip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_scorecard_template(data: dict) -> dict:
    return {
        "suite_id": data["suite_id"],
        "baseline_label": "current",
        "candidate_label": "redesigned",
        "cases": [
            {
                "id": case["id"],
                "role": case["role"],
                "winner": "pending",
                "overhead_delta": "pending",
                "leverage_delta": "pending",
                "throughput_delta": "pending",
                "notes": "",
            }
            for case in data["cases"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--suite",
        type=Path,
        default=Path("codex/agents/references/bakeoff_cases.yaml"),
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
    )
    parser.add_argument(
        "--emit-scorecard-template",
        action="store_true",
        help="Emit an empty scorecard template instead of the suite.",
    )
    args = parser.parse_args()

    data = load_suite(args.suite)
    errors = validate_suite(data)
    if errors:
        print("[FAIL] bakeoff suite errors:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    if args.emit_scorecard_template:
        print(json.dumps(render_scorecard_template(data), indent=2))
        return 0

    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(render_markdown(data), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
