#!/usr/bin/env python3
"""Conservative structural pre-spec gate for `$spec-pipeline`.

This script checks structure, not semantic truth.
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

ALIASES = {
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

EMPTY = {"", "n_a", "na", "none", "null", "tbd", "todo", "[]", "absent", "unknown"}
EXPLICIT_EMPTY_ALLOWED = {"default_assumptions"}


def read_text(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def non_empty(value: str) -> bool:
    return normalize(value) not in EMPTY


def has_field(text: str, field: str) -> bool:
    for label in [field, *ALIASES.get(field, [])]:
        match = re.search(rf"(?im)^\s*{re.escape(label).replace(r'\ ', r'[\s_-]*')}\s*:\s*(.+)$", text)
        if match:
            raw_value = match.group(1)
            if non_empty(raw_value) or (
                field in EXPLICIT_EMPTY_ALLOWED
                and normalize(raw_value) in {"none", "[]", "null"}
            ):
                return True
        heading = re.search(rf"(?im)^\s*#+\s*{re.escape(label)}\s*$", text)
        if heading:
            start = heading.end()
            next_heading = re.search(r"(?m)^\s*#+\s+", text[start:])
            body = text[start:start + next_heading.start()] if next_heading else text[start:]
            if non_empty(body):
                return True
    return False


def scalar(text: str, field: str) -> str | None:
    match = re.search(rf"(?im)^\s*{re.escape(field)}\s*:\s*(.*)$", text)
    return match.group(1).strip() if match else None


def extract_bool(text: str, field: str) -> bool | None:
    raw = scalar(text, field)
    if raw is None:
        return None
    value = normalize(raw)
    if value in {"true", "yes"}:
        return True
    if value in {"false", "no"}:
        return False
    return None


def handoff_sentence_present(text: str) -> bool:
    return bool(re.search(
        r"we are building .+ for .+ by changing .+ while explicitly not doing .+ success means",
        text,
        re.I | re.S,
    ))


def open_questions_accountable(text: str) -> bool:
    scalar_match = re.search(r"(?im)^\s*open[_\s-]*questions\s*:\s*(.*)$", text)
    if scalar_match and normalize(scalar_match.group(1)) in EMPTY:
        return True
    match = re.search(r"(?is)(open[_\s-]*questions\s*:)(.*?)(\n\s*[a-z0-9_ /-]+\s*:|\Z)", text)
    if not match:
        return True
    body = match.group(2).strip()
    if normalize(body) in EMPTY:
        return True
    lower = body.lower()
    return all(word in lower for word in ("owner", "default", "consequence"))


def clarification_ok(text: str, strict: bool) -> tuple[bool, str]:
    rounds_raw = scalar(text, "grill_rounds")
    no_grill = scalar(text, "no_grill_justification")
    clarification_present = re.search(r"(?im)^\s*clarification_receipt\s*:", text) is not None
    if rounds_raw is None and no_grill is None and not clarification_present:
        return (not strict, "clarification_receipt_missing")
    rounds = None
    if rounds_raw:
        match = re.match(r"\d+", rounds_raw)
        rounds = int(match.group(0)) if match else None
    if rounds == 0 and (not no_grill or normalize(no_grill) in EMPTY):
        return False, "grill_rounds_zero_without_no_grill_justification"
    return True, "present"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict-receipts", action="store_true")
    args = parser.parse_args()

    text = read_text(args.file)
    missing = [field for field in REQUIRED_FIELDS if not has_field(text, field)]
    plan_allowed = extract_bool(text, "plan_allowed")
    sentence_ok = handoff_sentence_present(text)
    questions_ok = open_questions_accountable(text)
    clar_ok, clar_reason = clarification_ok(text, args.strict_receipts)

    blocking: list[str] = []
    if missing:
        blocking.append("missing_required_fields")
    if plan_allowed is False:
        blocking.append("plan_allowed_explicitly_false")
    if plan_allowed is None:
        blocking.append("plan_allowed_missing")
    if not sentence_ok:
        blocking.append("handoff_sentence_missing_or_incomplete")
    if not questions_ok:
        blocking.append("open_questions_lack_owner_default_consequence")
    if not clar_ok:
        blocking.append(clar_reason)

    passed = not blocking and plan_allowed is True
    receipt = {
        "receipt_version": "SGATE-v1",
        "plan_allowed": "yes" if passed else "no",
        "mutation_allowed_pre_spec": "no",
        "script_gate": "passed" if passed else "failed",
        "gate_changed_decision": "unknown",
        "gate_blocked_plan": "no" if passed else "yes",
        "gate_defaulted_decisions": [],
        "material_open_questions_remaining": "no" if questions_ok else "yes",
        "pass_no_delta": "yes" if passed else "no",
        "reason": "structural_gate_pass" if passed else ",".join(blocking),
        "missing_fields": missing,
        "blocking_risks": blocking,
        "handoff_sentence_present": sentence_ok,
        "clarification_receipt": clar_reason,
    }
    result = {"spec_gate_receipt": receipt}

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
