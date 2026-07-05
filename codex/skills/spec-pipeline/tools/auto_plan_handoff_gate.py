#!/usr/bin/env python3
"""Auto $plan handoff predicate gate for SGR-v2."""
from __future__ import annotations
import json, pathlib, sys
from typing import Any
try:
    import yaml
except Exception:
    yaml = None

def load(path: str) -> Any:
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        return json.loads(text)
    if yaml is None:
        return json.loads(text)
    parsed = yaml.safe_load(text)
    if isinstance(parsed, dict):
        return parsed
    marker = "spec_governance_receipt:"
    if marker in text:
        return yaml.safe_load(text[text.index(marker):])
    return parsed

def unwrap(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict) and "spec_governance_receipt" in obj:
        return obj["spec_governance_receipt"]
    if isinstance(obj, dict):
        return obj
    raise SystemExit("input must be an object")

def get(d: dict[str, Any], *path: str, default=None):
    cur: Any = d
    for part in path:
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def eq(actual: Any, expected: Any) -> bool:
    if expected == "yes":
        return actual is True or str(actual).lower() == "yes"
    if expected == "no":
        return actual is False or str(actual).lower() == "no"
    return actual == expected

def yes_no_string(value: Any) -> str:
    return "yes" if eq(value, "yes") else "no"

def empty_list(v: Any) -> bool:
    return v is None or v == []

REQUIRED = [
    ("mode", "full|repair"),
    ("status", "complete"),
    ("lane", "spec_to_plan"),
    ("authoritative_brief.drift_detected", "no"),
    ("phase_presence.gate", "yes"),
    ("phase_presence.implementation_spec", "yes"),
    ("phase_presence.challenge", "yes"),
    ("phase_presence.fresh_eyes", "yes"),
    ("phase_presence.lint", "yes"),
    ("phase_presence.execution_handoff", "yes"),
    ("gate.plan_allowed", "yes"),
    ("gate.material_open_questions_remaining", "no"),
    ("fresh_eyes.drift_detected", "no"),
    ("lint.verdict", "pass"),
    ("lint.blocked_handoff", "no"),
    ("subagents.open_at_end", 0),
    ("execution_control.plan_allowed", "yes"),
    ("execution_control.execution_handoff", "yes"),
    ("execution_handoff.ready_for_plan", "yes"),
    ("execution_handoff.next_owner", "$plan"),
    ("auto_plan_handoff.eligible", "yes"),
    ("auto_plan_handoff.invocation", "same_turn_tail_call"),
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: auto_plan_handoff_gate.py <sgr-yaml-or-json>", file=sys.stderr)
        return 2
    sgr = unwrap(load(argv[1]))
    errors: list[str] = []
    for dotted, expected in REQUIRED:
        parts = dotted.split(".")
        actual = get(sgr, *parts)
        if expected == "full|repair":
            if actual not in ("full", "repair"):
                errors.append(f"{dotted}:expected:full-or-repair")
        else:
            if not eq(actual, expected):
                errors.append(f"{dotted}:expected:{expected}")
    if not empty_list(get(sgr, "execution_handoff", "do_not_execute_before")):
        errors.append("execution_handoff.do_not_execute_before:must-be-empty")
    if errors:
        if eq(get(sgr, "auto_plan_handoff", "eligible"), "yes"):
            errors.append("eligible=yes-but-predicates-failed")
        print(json.dumps({"auto_plan_handoff_gate": {
            "verdict": "blocked",
            "eligible": yes_no_string(get(sgr, "auto_plan_handoff", "eligible")),
            "next_owner": get(sgr, "execution_handoff", "next_owner", default=""),
            "errors": errors,
        }}, sort_keys=True))
        return 2
    print(json.dumps({"auto_plan_handoff_gate": {
        "verdict": "pass",
        "eligible": "yes",
        "next_owner": get(sgr, "execution_handoff", "next_owner", default=""),
        "errors": [],
    }}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
