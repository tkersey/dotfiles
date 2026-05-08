#!/usr/bin/env python3
"""Conservative structural readiness gate for spec handoff packets.

Usage:
  python spec_gate.py handoff.md
  cat handoff.md | python spec_gate.py -

The script intentionally checks structure, not semantic truth. A model should still decide
whether the content is materially complete.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "goal",
    "problem_layer",
    "target_user_or_maintainer",
    "scope",
    "non_goals",
    "locked_decisions",
    "primary_invariant",
    "success_criteria",
    "proof_bar",
    "compatibility_posture",
    "rollout_rollback_posture",
    "default_assumptions",
]

FIELD_ALIASES = {
    "problem_layer": ["problem layer", "root problem layer"],
    "target_user_or_maintainer": ["target user", "target maintainer", "target user / maintainer", "users", "stakeholders"],
    "non_goals": ["non-goals", "non goals", "out of scope"],
    "locked_decisions": ["locked decisions", "decisions"],
    "primary_invariant": ["primary invariant", "invariant"],
    "success_criteria": ["success criteria", "acceptance criteria"],
    "proof_bar": ["proof bar", "proof", "proof commands"],
    "compatibility_posture": ["compatibility posture", "compatibility"],
    "rollout_rollback_posture": ["rollout rollback posture", "rollout / rollback posture", "rollout", "rollback"],
    "default_assumptions": ["default assumptions", "assumptions"],
}

EMPTY_MARKERS = {"", "n/a", "na", "none", "null", "tbd", "todo", "?", "[]"}


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def non_empty_value(value: str) -> bool:
    return normalize(value) not in EMPTY_MARKERS


def has_field(text: str, field: str) -> bool:
    labels = [field] + FIELD_ALIASES.get(field, [])
    empty_alt = "|".join(re.escape(x) for x in sorted(EMPTY_MARKERS, key=len, reverse=True) if x)
    for label in labels:
        norm_label = normalize(label)
        # YAML-like key with canonical underscore label.
        m = re.search(rf"(?im)^\s*{re.escape(norm_label)}\s*:\s*(.+)$", text)
        if m and non_empty_value(m.group(1)):
            return True
        # YAML-like key with human label.
        m = re.search(rf"(?im)^\s*{re.escape(label)}\s*:\s*(.+)$", text)
        if m and non_empty_value(m.group(1)):
            return True
        # Markdown heading.
        heading = re.compile(rf"(?im)^\s*#+\s*{re.escape(label)}\s*$")
        match = heading.search(text)
        if match:
            start = match.end()
            next_heading = re.search(r"(?m)^\s*#+\s+", text[start:])
            body = text[start : start + next_heading.start()] if next_heading else text[start:]
            if non_empty_value(body):
                return True
    return False


def extract_plan_allowed(text: str) -> bool | None:
    m = re.search(r"(?im)^\s*plan[_\s-]*allowed\s*:\s*(true|false|yes|no)\s*$", text)
    if not m:
        return None
    return m.group(1).lower() in {"true", "yes"}


def handoff_sentence_present(text: str) -> bool:
    return bool(re.search(r"we are building .+ for .+ by changing .+ while explicitly not doing .+ success means", text, re.I | re.S))


def open_questions_are_accountable(text: str) -> bool:
    # Conservative: if open_questions says none/n/a, pass. If there are open questions,
    # require owner and default/action markers somewhere nearby or globally.
    m = re.search(r"(?is)(open[_\s-]*questions\s*:\s*)(.*?)(\n\s*[a-z0-9_ /-]+\s*:|\Z)", text)
    if not m:
        return True
    body = m.group(2).strip()
    if normalize(body) in EMPTY_MARKERS or re.match(r"(?i)^(none|n/a|na|null|\[\])\.?$", body):
        return True
    needed = ["owner", "default", "consequence"]
    lower = body.lower()
    return all(k in lower for k in needed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()

    text = read_text(args.file)
    missing = [field for field in REQUIRED_FIELDS if not has_field(text, field)]
    explicit = extract_plan_allowed(text)
    sentence_ok = handoff_sentence_present(text)
    open_ok = open_questions_are_accountable(text)

    blocking = []
    if missing:
        blocking.append("missing_required_fields")
    if explicit is False:
        blocking.append("plan_allowed_explicitly_false")
    if explicit is None:
        blocking.append("plan_allowed_missing")
    if not sentence_ok:
        blocking.append("handoff_sentence_missing_or_incomplete")
    if not open_ok:
        blocking.append("open_questions_lack_owner_default_consequence")

    allowed = not blocking and explicit is True
    result = {
        "PLAN_ALLOWED": allowed,
        "missing_fields": missing,
        "blocking_risks": blocking,
        "handoff_sentence_present": sentence_ok,
        "open_questions_accountable": open_ok,
        "next_grill_questions": [] if allowed else [
            {
                "id": "handoff_completion",
                "question": "Which missing handoff field should be resolved before planning?",
                "options": ["scope_and_non_goals", "proof_bar", "rollout_rollback", "primary_invariant"],
            }
        ],
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PLAN_ALLOWED: {str(allowed).lower()}")
        print(json.dumps(result, indent=2, sort_keys=True))

    return 0 if allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
