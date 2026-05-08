#!/usr/bin/env python3
"""Conservative structural lint for implementation specs.

Usage:
  python spec_lint.py spec.md
  cat spec.md | python spec_lint.py -
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTION_ALIASES = {
    "Objective": ["Objective", "Goal"],
    "Context / Current State": ["Context", "Current State", "Context / Current State"],
    "Locked Decisions": ["Locked Decisions", "Decision Log", "Decisions"],
    "Scope": ["Scope"],
    "Non-Goals": ["Non-Goals", "Non Goals", "Out of Scope", "Non-Goals/Out of Scope"],
    "Requirements": ["Requirements", "Functional Requirements"],
    "Design / Implementation Approach": ["Design", "Implementation Approach", "Design / Implementation Approach"],
    "Dependency-Ordered Implementation Sequence": ["Dependency-Ordered Implementation Sequence", "Implementation Sequence", "Implementation Brief"],
    "Requirement-to-Test Traceability": ["Requirement-to-Test Traceability", "Requirement to Test Traceability", "Traceability"],
    "Proof Commands": ["Proof Commands", "Tests/Acceptance", "Tests", "Acceptance"],
    "Risks and Edge Cases": ["Risks and Edge Cases", "Risks", "Edge Cases", "Edge Cases/Failure Modes"],
    "Rollback / Abort Criteria": ["Rollback / Abort Criteria", "Rollback", "Abort Criteria", "Rollback/Abort Criteria"],
    "Binary Done-State": ["Binary Done-State", "Done State", "Done-State", "Completion Bar"],
}

EMPTY = {"", "n/a", "na", "none", "null", "tbd", "todo", "?"}


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def section_body(text: str, alias: str) -> str | None:
    pattern = re.compile(rf"(?im)^\s*#+\s*{re.escape(alias)}\s*$")
    m = pattern.search(text)
    if not m:
        return None
    start = m.end()
    next_heading = re.search(r"(?m)^\s*#+\s+", text[start:])
    return text[start : start + next_heading.start()] if next_heading else text[start:]


def has_section(text: str, canonical: str) -> bool:
    for alias in SECTION_ALIASES[canonical]:
        body = section_body(text, alias)
        if body is not None and normalize(body) not in EMPTY:
            return True
    return False


def table_has_mapping(text: str) -> bool:
    trace = None
    for alias in SECTION_ALIASES["Requirement-to-Test Traceability"]:
        trace = section_body(text, alias)
        if trace:
            break
    if not trace:
        return False
    return bool(re.search(r"(?i)(requirement|req).*?(test|proof|command|acceptance)", trace, re.S)) and ("|" in trace or "-" in trace)


def rollback_specific(text: str) -> bool:
    body = None
    for alias in SECTION_ALIASES["Rollback / Abort Criteria"]:
        body = section_body(text, alias)
        if body:
            break
    if not body:
        return False
    low = body.lower()
    return any(k in low for k in ["trigger", "abort", "rollback", "revert", "blast", "disable", "flag", "back out"])


def proof_specific(text: str) -> bool:
    body = None
    for alias in SECTION_ALIASES["Proof Commands"]:
        body = section_body(text, alias)
        if body:
            break
    if not body:
        return False
    return bool(re.search(r"(?im)^\s*(pytest|npm|pnpm|yarn|cargo|go test|zig build|uv run|make|just|bundle|rspec|python|bash|ruff|mypy|tsc|deno|bun|swift|xcodebuild|gradle|mvn)\b", body)) or "```" in body


def open_questions_accountable(text: str) -> bool:
    m = re.search(r"(?is)^\s*#+\s*Open[^\n]*\n(.*?)(^\s*#+\s+|\Z)", text, re.M)
    if not m:
        return True
    body = m.group(1).strip()
    if normalize(body) in EMPTY or re.match(r"(?i)^(none|n/a|na|null)\.?$", body):
        return True
    low = body.lower()
    return all(k in low for k in ["owner", "default", "consequence"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    text = read_text(args.file)

    missing = [s for s in SECTION_ALIASES if not has_section(text, s)]
    blocking = []
    if missing:
        blocking.append("missing_required_sections")
    if not table_has_mapping(text):
        blocking.append("requirement_to_test_traceability_missing_or_weak")
    if not rollback_specific(text):
        blocking.append("rollback_abort_criteria_missing_or_weak")
    if not proof_specific(text):
        blocking.append("proof_commands_missing_or_weak")
    if not open_questions_accountable(text):
        blocking.append("open_questions_lack_owner_default_consequence")

    risk = []
    length = len(text)
    if length > 12000 and not re.search(r"(?i)strictness[_\s-]*profile\s*[:=]\s*strict", text):
        risk.append("long_spec_without_strict_profile_marker")
    if re.search(r"(?i)round delta.*(replaced|changed objective|new objective|supersedes)", text, re.S):
        risk.append("possible_objective_drift_in_round_delta")

    ready = not blocking
    result = {
        "SPEC_READY": ready,
        "missing_sections": missing,
        "blocking_errors": blocking,
        "material_risks": risk,
        "recommended_next_action": "proceed_to_execution" if ready else "revise_spec_or_return_to_grill",
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"SPEC_READY: {str(ready).lower()}")
        print(json.dumps(result, indent=2, sort_keys=True))

    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
