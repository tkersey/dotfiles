#!/usr/bin/env python3
"""Calibration harness for $join patch routing heuristics.

Evaluates synthetic scenarios and exits non-zero on expectation mismatches.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass
class Score:
    number: int
    score: float
    file_overlap: float
    symbol_overlap: float
    dependency_edge: bool
    recently_updated: bool


def tokenize(text: str) -> set[str]:
    return {m.group(0).lower() for m in TOKEN_RE.finditer(text)}


def overlap_ratio(left: list[str], right: list[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set:
        return 0.0
    return len(left_set & right_set) / len(left_set)


def semantic_match(hint: str, title: str, body: str) -> bool:
    hint_tokens = tokenize(hint)
    if len(hint_tokens) < 2:
        return False
    pr_tokens = tokenize(f"{title} {body}")
    if not pr_tokens:
        return False
    matched = len(hint_tokens & pr_tokens)
    return (matched / len(hint_tokens)) >= 0.4


def score_pr(patch: dict[str, Any], pr: dict[str, Any]) -> Score:
    context = patch.get("context", {})
    score = 0.0

    if context.get("pr_number") == pr["number"]:
        score += 90

    if context.get("branch_hint") and context["branch_hint"] == pr.get("head_ref"):
        score += 40

    semantic_hint = context.get("semantic_hint", "")
    if semantic_hint and semantic_match(semantic_hint, pr.get("title", ""), pr.get("body", "")):
        score += 40

    file_overlap = overlap_ratio(patch.get("files", []), pr.get("files", []))
    score += file_overlap * 50

    symbol_overlap = overlap_ratio(patch.get("symbols", []), pr.get("symbols", []))
    score += symbol_overlap * 20

    recently_updated = bool(pr.get("recently_updated", False))
    if recently_updated:
        score += 10

    if pr.get("conflicting_hunk_overlap", False):
        score -= 40

    return Score(
        number=pr["number"],
        score=score,
        file_overlap=file_overlap,
        symbol_overlap=symbol_overlap,
        dependency_edge=bool(pr.get("dependency_edge", False)),
        recently_updated=recently_updated,
    )


def sort_scores(scores: list[Score]) -> list[Score]:
    return sorted(
        scores,
        key=lambda s: (-s.score, -s.file_overlap, -int(s.recently_updated), s.number),
    )


def decide_route(patch: dict[str, Any], scores: list[Score]) -> dict[str, Any]:
    supersedes_prs = sorted({int(x) for x in patch.get("supersedes_prs", [])})
    prefer_replacement_branch = bool(patch.get("prefer_replacement_branch", False))

    if not scores:
        if supersedes_prs:
            return {"decision": "replacement_create", "target_pr": None, "supersedes_prs": supersedes_prs}
        return {"decision": "create", "target_pr": None}

    best = scores[0]
    second = scores[1] if len(scores) > 1 else None
    margin = math.inf if second is None else (best.score - second.score)

    if supersedes_prs:
        if prefer_replacement_branch:
            return {"decision": "replacement_create", "target_pr": None, "supersedes_prs": supersedes_prs}
        if best.number in supersedes_prs and best.score >= 70 and margin >= 15:
            return {"decision": "replacement_update", "target_pr": best.number, "supersedes_prs": supersedes_prs}
        return {"decision": "replacement_create", "target_pr": None, "supersedes_prs": supersedes_prs}

    if patch.get("requires_stack", False) and best.dependency_edge and best.score >= 40:
        return {"decision": "stack", "target_pr": best.number}

    if best.score >= 70 and margin >= 15:
        return {"decision": "update", "target_pr": best.number}

    if 40 <= best.score < 70:
        if best.dependency_edge:
            return {"decision": "update", "target_pr": best.number}
        return {"decision": "create", "target_pr": None}

    return {"decision": "create", "target_pr": None}


def evaluate_scenario(scenario: dict[str, Any]) -> tuple[dict[str, Any], list[Score]]:
    scores = sort_scores([score_pr(scenario["patch"], pr) for pr in scenario.get("open_prs", [])])
    decision = decide_route(scenario["patch"], scores)
    return decision, scores


def compare_expected(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("decision", "target_pr", "supersedes_prs"):
        if key in expected and actual.get(key) != expected.get(key):
            errors.append(f"{key}: expected={expected.get(key)!r} actual={actual.get(key)!r}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run synthetic routing calibration scenarios.")
    parser.add_argument(
        "--scenarios",
        default=str(Path(__file__).resolve().parents[1] / "assets" / "routing-scenarios.json"),
        help="Path to scenario JSON file.",
    )
    parser.add_argument(
        "--scenario-id",
        action="append",
        default=[],
        help="Limit execution to one or more scenario IDs.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON result summary.",
    )
    return parser.parse_args()


def load_scenarios(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("Scenario file must contain a top-level JSON array.")
    return data


def format_score(score: Score) -> str:
    return (
        f"PR #{score.number} score={score.score:.1f} "
        f"(files={score.file_overlap:.2f}, symbols={score.symbol_overlap:.2f}, "
        f"dep={score.dependency_edge}, recent={score.recently_updated})"
    )


def main() -> int:
    args = parse_args()
    scenarios = load_scenarios(args.scenarios)
    if args.scenario_id:
        scenario_ids = set(args.scenario_id)
        scenarios = [s for s in scenarios if s.get("id") in scenario_ids]
    if not scenarios:
        print("No scenarios selected.", file=sys.stderr)
        return 2

    failures: list[dict[str, Any]] = []
    outputs: list[dict[str, Any]] = []

    for scenario in scenarios:
        actual, scores = evaluate_scenario(scenario)
        expected = scenario.get("expected", {})
        mismatches = compare_expected(actual, expected)

        result = {
            "id": scenario.get("id"),
            "name": scenario.get("name"),
            "actual": actual,
            "expected": expected,
            "top_scores": [format_score(s) for s in scores[:3]],
            "pass": not mismatches,
            "mismatches": mismatches,
        }
        outputs.append(result)
        if mismatches:
            failures.append(result)

    if args.json:
        print(json.dumps(outputs, indent=2))
    else:
        for result in outputs:
            status = "PASS" if result["pass"] else "FAIL"
            print(f"[{status}] {result['id']}: {result['name']}")
            print(f"  expected: {result['expected']}")
            print(f"  actual:   {result['actual']}")
            for line in result["top_scores"]:
                print(f"  score:    {line}")
            for mismatch in result["mismatches"]:
                print(f"  mismatch: {mismatch}")

    if failures:
        print(f"\n{len(failures)} scenario(s) failed.", file=sys.stderr)
        return 1

    print(f"\nAll {len(outputs)} scenario(s) passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
