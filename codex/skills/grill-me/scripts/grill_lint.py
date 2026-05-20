#!/usr/bin/env python3
"""Conservative structural lint for grill-me final outputs.

Usage:
  python grill_lint.py final-output.md
  cat final-output.md | python grill_lint.py -

This checks mechanical contract markers only. It is not a substitute for model judgment.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_SNAPSHOT_FIELDS = [
    "Stage",
    "Problem statement",
    "Problem layer",
    "Users / stakeholders / owners",
    "Scope",
    "Non-goals",
    "Primary invariant",
    "Success criteria",
    "Proof bar",
    "Compatibility posture",
    "Rollout / rollback posture",
    "Constraints",
    "Facts",
    "Decisions",
    "Trade-offs accepted",
    "Assumptions",
    "Risks / edge cases",
    "Deferred items",
    "Open questions",
    "Lane status",
    "User confirmation",
]

REQUIRED_PACKET_FIELDS = [
    "goal",
    "problem_layer",
    "target_user_or_maintainer",
    "stakeholders_and_owners",
    "scope",
    "non_goals",
    "locked_decisions",
    "tradeoffs_accepted",
    "primary_invariant",
    "success_criteria",
    "proof_bar",
    "compatibility_posture",
    "rollout_rollback_posture",
    "support_and_maintenance_posture",
    "researched_facts",
    "default_assumptions",
    "open_questions",
    "deferred_questions",
    "immaterial_questions",
    "lane_status",
    "plan_allowed",
]

EMPTY_MARKERS = {"", "n/a", "na", "none", "null", "tbd", "todo", "?", "[]"}
FORBIDDEN_PATTERNS = [
    r"<proposed_plan>",
    r"restate (the )?brief",
    r"in your own words",
    r"draft (a )?prompt",
    r"write (me )?a prose brief",
]


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def non_empty(value: str) -> bool:
    return normalize(value) not in EMPTY_MARKERS


def has_snapshot_field(text: str, field: str) -> bool:
    pattern = rf"(?im)^\s*-\s*{re.escape(field)}\s*:\s*(.*)$"
    m = re.search(pattern, text)
    if not m:
        return False
    value = m.group(1).strip()
    if value:
        return non_empty(value)
    # Accept multiline value until next bullet/heading if non-empty.
    start = m.end()
    rest = text[start:]
    stop = re.search(r"(?m)^\s*(?:-|#|```)", rest)
    body = rest[: stop.start()] if stop else rest
    return non_empty(body)


def has_packet_field(text: str, field: str) -> bool:
    pattern = rf"(?im)^\s{{2}}{re.escape(field)}\s*:\s*(.*)$"
    m = re.search(pattern, text)
    if not m:
        return False
    value = m.group(1).strip()
    if value:
        return non_empty(value)
    # Lists and nested mappings may start after the key.
    start = m.end()
    rest = text[start:]
    stop = re.search(rf"(?m)^\s{{2}}[a-zA-Z0-9_]+\s*:", rest)
    body = rest[: stop.start()] if stop else rest
    return non_empty(body)


def plan_allowed_value(text: str) -> str | None:
    m = re.search(r"(?im)^\s{2}plan_allowed\s*:\s*(true|false)\s*$", text)
    return m.group(1).lower() if m else None


def extract_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"(?m)^#{1,3}\s+(.+?)\s*$", text))
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[normalize(title)] = text[start:end]
    return sections


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = read_text(args.file)
    sections = extract_sections(text)

    missing_snapshot = [f for f in REQUIRED_SNAPSHOT_FIELDS if not has_snapshot_field(text, f)]
    missing_packet = [f for f in REQUIRED_PACKET_FIELDS if not has_packet_field(text, f)]
    forbidden = [p for p in FORBIDDEN_PATTERNS if re.search(p, text, re.I)]
    plan_allowed = plan_allowed_value(text)

    blocking = []
    if "snapshot" not in sections and not re.search(r"(?m)^Snapshot\s*$", text):
        blocking.append("snapshot_heading_missing")
    if "grill_decision_packet" not in text:
        blocking.append("grill_decision_packet_missing")
    if missing_snapshot:
        blocking.append("snapshot_fields_missing_or_empty")
    if missing_packet:
        blocking.append("packet_fields_missing_or_empty")
    if plan_allowed is None:
        blocking.append("plan_allowed_missing_or_not_boolean")
    if forbidden:
        blocking.append("forbidden_patterns_present")

    result = {
        "GRILL_OUTPUT_READY": not blocking,
        "missing_snapshot_fields": missing_snapshot,
        "missing_packet_fields": missing_packet,
        "plan_allowed": plan_allowed,
        "forbidden_patterns": forbidden,
        "blocking_errors": blocking,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"GRILL_OUTPUT_READY: {str(not blocking).lower()}")
        print(json.dumps(result, indent=2, sort_keys=True))

    return 0 if not blocking else 2


if __name__ == "__main__":
    raise SystemExit(main())
