#!/usr/bin/env python3
"""Fail-closed lane-selection gate for SGR-v2.

Catches the regression:
  full + complete + plan-ready + lane=spec_only solely because user invoked
  $spec-pipeline and did not separately request $plan.
"""
from __future__ import annotations
import json, sys, pathlib
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

YES = {"yes", True}
NO = {"no", False}

def load(path: str) -> Any:
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        return json.loads(text)
    if yaml is None:
        return json.loads(text)
    return yaml.safe_load(text)

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

def is_yes(v: Any) -> bool:
    return v in YES or str(v).lower() == "yes"

def is_no(v: Any) -> bool:
    return v in NO or str(v).lower() == "no"

def as_list(v: Any) -> list[Any]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]

LEGAL_SPEC_ONLY = {
    "explicit_spec_only",
    "explicit_no_plan",
    "mode_not_full",
    "blocked",
    "drift",
    "partial",
    "material_questions",
    "gate_plan_disallowed",
    "lint_failed",
    "lint_blocked_handoff",
    "fresh_eyes_drift",
    "fresh_eyes_returned_to_grill",
    "not_ready_for_plan",
    "next_owner_not_plan",
    "do_not_execute_before",
    "runtime_plan_unavailable",
}

BAD_REASON_PATTERNS = [
    "user did not request same-turn planning",
    "user did not request $plan",
    "invoked spec-pipeline, not planning",
    "invoked spec-pipeline, not plan",
    "did not separately",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: spec_lane_selection_gate.py <sgr-yaml-or-json>", file=sys.stderr)
        return 2
    sgr = unwrap(load(argv[1]))
    errors: list[str] = []

    mode = get(sgr, "mode")
    status = get(sgr, "status")
    lane = get(sgr, "lane")
    blockers = set(str(x) for x in as_list(get(sgr, "lane_selection", "blockers", default=[])))
    reason = " ".join(str(x) for x in [
        get(sgr, "gate", "reason", default=""),
        get(sgr, "auto_plan_handoff", "reason", default=""),
        get(sgr, "execution_handoff", "handoff_summary", default=""),
    ]).lower()

    if mode == "full" and status == "complete" and lane == "spec_only":
        concrete = blockers & LEGAL_SPEC_ONLY
        # Derive blockers if they are visible in receipt.
        if get(sgr, "gate", "plan_allowed") not in ("yes", True):
            concrete.add("gate_plan_disallowed")
        if get(sgr, "gate", "material_open_questions_remaining") in ("yes", True):
            concrete.add("material_questions")
        if get(sgr, "lint", "verdict") == "fail":
            concrete.add("lint_failed")
        if get(sgr, "lint", "blocked_handoff") in ("yes", True):
            concrete.add("lint_blocked_handoff")
        if get(sgr, "fresh_eyes", "drift_detected") in ("yes", True):
            concrete.add("fresh_eyes_drift")
        if get(sgr, "execution_handoff", "ready_for_plan") in ("no", False):
            # only concrete if next_owner is not $plan or reason says why
            if get(sgr, "execution_handoff", "next_owner") != "$plan":
                concrete.add("next_owner_not_plan")
        if as_list(get(sgr, "execution_handoff", "do_not_execute_before", default=[])):
            concrete.add("do_not_execute_before")
        if any(p in reason for p in BAD_REASON_PATTERNS):
            errors.append("illegal spec_only reason: explicit $spec-pipeline / missing separate $plan request is not a blocker")
        if not concrete:
            errors.append("lane=spec_only in full complete SGR-v2 requires a concrete blocker")

    # Catch plan-ready but not spec_to_plan.
    plan_ready = (
        mode in {"full", "repair"}
        and status == "complete"
        and get(sgr, "gate", "plan_allowed") in ("yes", True)
        and get(sgr, "gate", "material_open_questions_remaining") in ("no", False)
        and get(sgr, "lint", "verdict") == "pass"
        and get(sgr, "lint", "blocked_handoff") in ("no", False)
        and get(sgr, "execution_handoff", "ready_for_plan") in ("yes", True)
        and get(sgr, "execution_handoff", "next_owner") == "$plan"
        and not as_list(get(sgr, "execution_handoff", "do_not_execute_before", default=[]))
    )
    if plan_ready and lane != "spec_to_plan":
        errors.append("plan-ready full/repair SGR-v2 must use lane=spec_to_plan")

    if errors:
        print("spec-lane-selection: blocked", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print("spec-lane-selection: pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
