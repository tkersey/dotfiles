#!/usr/bin/env python3
"""Validate retrace_inquiry_plan / RIP-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

HORIZONS = {"pre_decision", "post_decision_pre_outcome", "outcome_aware"}
MODES = {
    "rationale",
    "counterfactual",
    "alternative_challenge",
    "assumption_probe",
    "evidence_ablation",
    "retrospective",
}
MODEL_POLICIES = {"historical_if_available", "current_recorded", "explicit_model"}
WORKSPACE_POLICIES = {"exact", "head_only", "transcript_only", "no_current_checkout"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    body = value.get("retrace_inquiry_plan", value) if isinstance(value, dict) else value
    if not isinstance(body, dict):
        raise ValueError("retrace_inquiry_plan must be an object")
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        plan = load(args.file)
    except Exception as exc:
        print(json.dumps({"rip_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if plan.get("plan_version") != "RIP-v1":
        errors.append("plan_version")
    for key in ("inquiry_id", "source_capsule", "objective"):
        if not plan.get(key):
            errors.append(key)

    lanes = plan.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        errors.append("lanes")
        lanes = []

    lane_ids: set[str] = set()
    total_forks = 0
    for index, lane in enumerate(lanes):
        if not isinstance(lane, dict):
            errors.append(f"lanes[{index}]:object")
            continue
        prefix = f"lanes[{index}]"
        lane_id = lane.get("lane_id")
        if not isinstance(lane_id, str) or not lane_id:
            errors.append(f"{prefix}.lane_id")
        elif lane_id in lane_ids:
            errors.append(f"{prefix}.lane_id:duplicate")
        else:
            lane_ids.add(lane_id)

        horizon = lane.get("temporal_horizon")
        mode = lane.get("inquiry_mode")
        if horizon not in HORIZONS:
            errors.append(f"{prefix}.temporal_horizon")
        if mode not in MODES:
            errors.append(f"{prefix}.inquiry_mode")

        count = lane.get("fork_count")
        if not isinstance(count, int) or count < 1:
            errors.append(f"{prefix}.fork_count")
        else:
            total_forks += count

        for key in ("evidence_allowed", "evidence_withheld", "expected_receipt_fields"):
            if not isinstance(lane.get(key), list):
                errors.append(f"{prefix}.{key}")
        if not lane.get("prompt_template"):
            errors.append(f"{prefix}.prompt_template")

        if mode == "counterfactual" and horizon != "pre_decision":
            errors.append(f"{prefix}:counterfactual-requires-pre-decision")
        if mode == "alternative_challenge" and horizon != "pre_decision":
            errors.append(f"{prefix}:challenge-requires-pre-decision")
        if mode == "retrospective" and horizon != "outcome_aware":
            errors.append(f"{prefix}:retrospective-requires-outcome-aware")
        if mode == "rationale" and horizon != "post_decision_pre_outcome":
            warnings.append(f"{prefix}:rationale-usually-post-decision-pre-outcome")

    if plan.get("model_policy") not in MODEL_POLICIES:
        errors.append("model_policy")
    if plan.get("workspace_policy") not in WORKSPACE_POLICIES:
        errors.append("workspace_policy")

    permissions = plan.get("permission_policy")
    if not isinstance(permissions, dict):
        errors.append("permission_policy")
    else:
        if permissions.get("read_only") is not True:
            errors.append("permission_policy.read_only")
        if permissions.get("network") is not False:
            errors.append("permission_policy.network")

    budgets = plan.get("budgets")
    if not isinstance(budgets, dict):
        errors.append("budgets")
        budgets = {}
    max_forks = budgets.get("max_forks")
    if not isinstance(max_forks, int) or max_forks < 1:
        errors.append("budgets.max_forks")
    elif total_forks > max_forks:
        errors.append("budgets:max-forks-exceeded")
    turns = budgets.get("max_turns_per_fork")
    if not isinstance(turns, int) or turns < 1:
        errors.append("budgets.max_turns_per_fork")
    elif turns > 1:
        warnings.append("budgets.max_turns_per_fork:greater-than-default-one")
    for key in ("max_total_tokens", "timeout_ms"):
        if not isinstance(budgets.get(key), int) or budgets[key] < 1:
            errors.append(f"budgets.{key}")

    if not plan.get("cleanup"):
        errors.append("cleanup")

    result = {
        "rip_gate": {
            "verdict": "pass" if not errors else "fail",
            "inquiry_id": plan.get("inquiry_id"),
            "lane_count": len(lanes),
            "fork_count": total_forks,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
