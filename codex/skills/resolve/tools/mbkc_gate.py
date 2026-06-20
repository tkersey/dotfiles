#!/usr/bin/env python3
"""Fail-closed gate for minimum_behavioral_kernel_certificate / MBKC-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


HARD_DIMENSIONS = [
    ("semantic_surface", "current", "realization", "truth_owners"),
    ("semantic_surface", "current", "realization", "public_symbols"),
    ("semantic_surface", "current", "realization", "state_fields"),
    ("semantic_surface", "current", "realization", "fallback_or_compatibility_paths"),
    ("semantic_surface", "current", "kernel", "protocol_cases"),
    ("semantic_surface", "current", "proof", "wound_specific_tests"),
]


def get(value: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = value
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--terminal", action="store_true")
    args = parser.parse_args()

    try:
        value = json.loads(Path(args.file).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"mbkc_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    body = value.get("minimum_behavioral_kernel_certificate", value)
    errors: list[str] = []
    warnings: list[str] = []

    if body.get("certificate_version") != "MBKC-v1":
        errors.append("certificate_version")
    for field in [
        "certificate_id", "stage", "campaign", "acceptance", "observations",
        "kernel", "kernel_review", "realization_designs", "selected_design",
        "realization_map", "semantic_surface", "proof_basis", "holdouts",
        "delivery", "closure_horizon", "gate",
    ]:
        if body.get(field) in (None, ""):
            errors.append(f"{field}:missing")

    campaign = body.get("campaign", {})
    for field in ["campaign_id", "campaign_base_sha", "review_ready_baseline_sha", "current_delivery_head"]:
        if not campaign.get(field):
            errors.append(f"campaign.{field}:missing")

    if body.get("kernel", {}).get("kernel_version") != "MBK-v1":
        errors.append("kernel.version")
    if body.get("kernel_review", {}).get("verdict") != "accepted":
        errors.append("kernel_review:not-accepted")

    realization_map = body.get("realization_map", {})
    gate = realization_map.get("gate", {}) if isinstance(realization_map, dict) else {}
    for field in [
        "kernel_conformance",
        "orphan_code_constructs_zero",
        "wound_specific_tests_zero",
        "proof_laws_covered",
        "semantic_surface_conserved",
    ]:
        if gate.get(field) != "pass":
            errors.append(f"realization_map.gate.{field}:not-pass")

    surface = body.get("semantic_surface", {})
    if surface.get("hard_dimensions_nonincreasing") != "yes":
        errors.append("semantic_surface.hard_dimensions_nonincreasing")
    if surface.get("total_description_nonincreasing") != "yes":
        approved = body.get("acceptance", {}).get("approved_complexity_rebaseline") is True
        if not approved:
            errors.append("semantic_surface.total_description_nonincreasing")
        else:
            warnings.append("approved-complexity-rebaseline")

    if body.get("proof_basis", {}).get("wound_specific_tests"):
        errors.append("proof_basis.wound_specific_tests")
    if body.get("realization_map", {}).get("orphan_code_constructs"):
        errors.append("realization_map.orphan_code_constructs")
    if body.get("proof_basis", {}).get("unmapped_proof_actions"):
        errors.append("proof_basis.unmapped_proof_actions")

    certificate_gate = body.get("gate", {})
    stage = body.get("stage")
    stage_requirement = {
        "kernel_accepted": "kernel_allowed",
        "realization_verified": "realization_allowed",
        "applied": "apply_allowed",
        "final_certified": "commit_allowed",
        "committed": "push_allowed",
        "pushed": "tuple_closure_allowed",
        "conformance_closed_for_tuple": "tuple_closure_allowed",
        "terminal_closed": "terminal_closure_allowed",
    }
    required = stage_requirement.get(stage)
    if required and certificate_gate.get(required) != "yes":
        errors.append(f"gate.{required}:not-yes")

    if args.terminal or stage == "terminal_closed":
        if stage != "terminal_closed":
            errors.append("stage:not-terminal_closed")
        holdouts = body.get("holdouts", {})
        if holdouts.get("kernel", {}).get("verdict") != "clean":
            errors.append("holdouts.kernel:not-clean")
        if holdouts.get("conformance", {}).get("verdict") != "clean":
            errors.append("holdouts.conformance:not-clean")
        delivery = body.get("delivery", {})
        for field in ["commit_sha", "pushed_head", "pr_sweep_ref"]:
            if not delivery.get(field):
                errors.append(f"delivery.{field}:missing")
        horizon = body.get("closure_horizon", {})
        if not horizon.get("review_backend") or not horizon.get("review_receipt"):
            errors.append("closure_horizon.review-proof-missing")
        if horizon.get("reopen_conditions") in (None, []):
            errors.append("closure_horizon.reopen_conditions:missing")

    result = {
        "mbkc_gate": {
            "verdict": "pass" if not errors else "fail",
            "stage": stage,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
