#!/usr/bin/env python3
"""PSC-v1 receiver gate for $plan."""
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
    return yaml.safe_load(text)

def unwrap_psc(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict) and "plan_source_contract" in obj:
        return obj["plan_source_contract"]
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

def list_empty(v: Any) -> bool:
    return v is None or v == []

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: plan_source_contract_gate.py <psc-yaml-or-json>", file=sys.stderr)
        return 2
    psc = unwrap_psc(load(argv[1]))
    errors: list[str] = []
    req = {
        "contract_version": "PSC-v1",
        "source_owner": "spec-pipeline",
    }
    for key, expected in req.items():
        if psc.get(key) != expected:
            errors.append(f"{key}: expected {expected!r}, got {psc.get(key)!r}")
    for key in ("spec_id", "implementation_spec", "decision_packet", "proof_bar", "target_branch"):
        if not psc.get(key):
            errors.append(f"{key}: required")
    if not list_empty(psc.get("do_not_execute_before")):
        errors.append("do_not_execute_before must be empty")

    sgr = get(psc, "sgr_v2", "spec_governance_receipt")
    if not isinstance(sgr, dict):
        errors.append("sgr_v2.spec_governance_receipt: required")
    else:
        checks = [
            ("receipt_version", "SGR-v2"),
            ("status", "complete"),
            ("lane", "spec_to_plan"),
            ("gate.plan_allowed", "yes"),
            ("gate.material_open_questions_remaining", "no"),
            ("lint.verdict", "pass"),
            ("lint.blocked_handoff", "no"),
            ("execution_handoff.ready_for_plan", "yes"),
            ("execution_handoff.next_owner", "$plan"),
            ("auto_plan_handoff.eligible", "yes"),
        ]
        if sgr.get("mode") not in ("full", "repair"):
            errors.append(f"mode: expected full|repair, got {sgr.get('mode')!r}")
        for dotted, expected in checks:
            actual = get(sgr, *dotted.split("."))
            if not eq(actual, expected):
                errors.append(f"sgr_v2.{dotted}: expected {expected!r}, got {actual!r}")
        if not list_empty(get(sgr, "execution_handoff", "do_not_execute_before")):
            errors.append("sgr_v2.execution_handoff.do_not_execute_before must be empty")
    if errors:
        print("plan-source-contract: blocked", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("plan-source-contract: pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
