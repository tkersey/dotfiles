#!/usr/bin/env python3
"""Validate actuation_slice / ASL-v1, including optional EPG lineage."""

from __future__ import annotations

import argparse
import json
import re
from typing import Any

from common import load_document, no, require_list, require_object, unwrap, yes

STATES = {
    "prepared",
    "mutating",
    "focused_proved",
    "wave_proved",
    "return_to_frontier",
    "blocked",
    "closed",
}
MUTABLE_STATES = {"prepared", "mutating"}
POLICY_ACTION_KINDS = {
    "inspect",
    "probe",
    "decide",
    "mutate",
    "prove",
    "stabilize",
    "deploy",
    "rollback",
}


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", value))


def validate_policy_control(body: dict[str, Any], errors: list[str]) -> tuple[bool, str | None]:
    """Validate optional EPG binding. Returns (policy_ready, action_id)."""
    value = body.get("policy_control")
    if value is None:
        return True, None
    if not isinstance(value, dict):
        errors.append("policy_control:must-be-object")
        return False, None
    if value.get("mode") != "epg":
        errors.append("policy_control.mode")
    for key in ("policy_id", "state_id", "decision_id", "action_id"):
        if not value.get(key):
            errors.append(f"policy_control.{key}")
    revision = value.get("policy_revision")
    if not isinstance(revision, int) or revision < 1:
        errors.append("policy_control.policy_revision")
    for key in ("policy_digest", "state_digest"):
        if not valid_digest(value.get(key)):
            errors.append(f"policy_control.{key}")
    if value.get("action_kind") not in POLICY_ACTION_KINDS:
        errors.append("policy_control.action_kind")
    if not yes(value.get("policy_current")):
        errors.append("policy_control.policy_current")
    if not yes(value.get("decision_selected")):
        errors.append("policy_control.decision_selected")
    sequence = value.get("commitment_horizon_sequence")
    if not isinstance(sequence, int) or sequence < 1:
        errors.append("policy_control.commitment_horizon_sequence")
    if not isinstance(value.get("expected_effects"), dict):
        errors.append("policy_control.expected_effects:must-be-object")
    for key in ("expected_observation_refs", "failure_observation_refs"):
        if not isinstance(value.get(key), list):
            errors.append(f"policy_control.{key}:must-be-list")
    if value.get("decision_mutation_authority") not in {"no", False}:
        errors.append("policy_control.decision_mutation_authority:must-be-no")
    return not any(item.startswith("policy_control") for item in errors), value.get("action_id")


def validate_slice(body: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if body.get("slice_version") != "ASL-v1":
        errors.append("slice_version")
    for key in ("run_id", "slice_id"):
        if not body.get(key):
            errors.append(key)

    artifact = require_object(body, "artifact_state", errors)
    for key in ("repository_root", "branch", "head", "dirty_fingerprint", "st_plan_fingerprint"):
        if not artifact.get(key):
            errors.append(f"artifact_state.{key}")

    policy_ready, policy_action_id = validate_policy_control(body, errors)

    task = require_object(body, "task_control", errors)
    for key in ("plan_ref", "gcr_id", "gcr_ref"):
        if not task.get(key):
            errors.append(f"task_control.{key}")
    if not isinstance(task.get("gcr_seq"), int) or task.get("gcr_seq", -1) < 0:
        errors.append("task_control.gcr_seq")
    if not (yes(task.get("gcr_current")) or no(task.get("gcr_current"))):
        errors.append("task_control.gcr_current")
    if not (yes(task.get("execution_allowed")) or no(task.get("execution_allowed"))):
        errors.append("task_control.execution_allowed")
    tasks = require_list(task, "selected_task_ids", errors)
    if len(tasks) != len(set(tasks)):
        errors.append("task_control.selected_task_ids:duplicates")
    require_list(task, "graph_debt_refs", errors)
    if policy_action_id is not None:
        lineage = task.get("policy_action_id")
        if lineage != policy_action_id:
            errors.append("task_control.policy_action_id:mismatch")

    semantic = require_object(body, "semantic_control", errors)
    for key in ("owner", "invariant"):
        if not semantic.get(key):
            errors.append(f"semantic_control.{key}")
    require_list(semantic, "semantic_route_refs", errors)
    selected_rows = require_list(semantic, "selected_rows", errors)
    open_rows = require_list(semantic, "open_rows", errors)
    observations = require_list(semantic, "new_observations", errors)
    if len(selected_rows) != len(set(selected_rows)):
        errors.append("semantic_control.selected_rows:duplicates")
    if len(open_rows) != len(set(open_rows)):
        errors.append("semantic_control.open_rows:duplicates")

    decision = require_object(body, "decision", errors)
    for key in ("question", "selected_route", "selected_normal_form"):
        if not decision.get(key):
            errors.append(f"decision.{key}")
    alternatives = require_list(decision, "alternatives", errors)
    rejected = require_list(decision, "rejected_routes", errors)
    if not alternatives:
        errors.append("decision.alternatives:empty")
    if not rejected:
        warnings.append("decision.rejected_routes:empty")
    boundary = require_object(decision, "patch_boundary", errors)
    files = require_list(boundary, "files", errors)
    symbols = require_list(boundary, "symbols", errors)
    if not files and not symbols:
        errors.append("decision.patch_boundary:empty")
    require_list(decision, "forbidden_actions", errors)
    require_object(decision, "surface_budget", errors)

    realization = require_object(body, "realization", errors)
    if not realization.get("fixed_point_slice_ref"):
        errors.append("realization.fixed_point_slice_ref")
    if realization.get("status") not in {
        "not_started",
        "prepared",
        "valid",
        "no_change",
        "return_to_frontier",
        "blocked",
        "invalid",
    }:
        errors.append("realization.status")

    proof = require_object(body, "proof", errors)
    if not proof.get("proof_dag_ref"):
        errors.append("proof.proof_dag_ref")
    obligations = require_list(proof, "focused_obligations", errors)
    if not obligations:
        errors.append("proof.focused_obligations:empty")
    require_list(proof, "current_epoch_refs", errors)
    for key in ("focused_gate", "wave_gate", "final_gate"):
        if proof.get(key) not in {"pass", "fail", "missing", "stale"}:
            errors.append(f"proof.{key}")

    contracts = require_list(body, "active_skill_contracts", errors)
    for index, row in enumerate(contracts):
        if not isinstance(row, dict) or not row.get("skill") or not row.get("fingerprint"):
            errors.append(f"active_skill_contracts[{index}]")

    state = body.get("state")
    if state not in STATES:
        errors.append("state")
    frontier = require_object(body, "next_frontier", errors)
    require_list(frontier, "task_ids", errors)
    require_list(frontier, "matrix_rows", errors)
    if not frontier.get("reason"):
        errors.append("next_frontier.reason")

    gate = require_object(body, "gate", errors)
    allowed = gate.get("mutation_allowed")
    if not (yes(allowed) or no(allowed)):
        errors.append("gate.mutation_allowed")
    if not gate.get("reason"):
        errors.append("gate.reason")

    prerequisites = (
        policy_ready
        and yes(task.get("gcr_current"))
        and yes(task.get("execution_allowed"))
        and bool(tasks)
        and bool(semantic.get("owner"))
        and bool(semantic.get("invariant"))
        and bool(decision.get("selected_route"))
        and bool(decision.get("selected_normal_form"))
        and bool(files or symbols)
        and bool(obligations)
        and state in MUTABLE_STATES
        and not observations
    )

    if yes(allowed) and not prerequisites:
        errors.append("gate.mutation_allowed:prerequisites-fail")
    if prerequisites and no(allowed):
        warnings.append("gate.mutation_allowed:no-despite-prerequisites")
    if observations and yes(allowed):
        errors.append("new-observation-with-mutation-allowed")
    if observations and state != "return_to_frontier":
        errors.append("new-observation-requires-return-to-frontier")
    if state in {"return_to_frontier", "blocked", "closed"} and yes(allowed):
        errors.append(f"state:{state}:mutation-must-be-no")
    if state == "focused_proved" and proof.get("focused_gate") != "pass":
        errors.append("focused_proved:focused-gate-not-pass")
    if state == "wave_proved" and proof.get("wave_gate") != "pass":
        errors.append("wave_proved:wave-gate-not-pass")
    if state == "closed" and proof.get("final_gate") != "pass":
        errors.append("closed:final-gate-not-pass")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    try:
        body = unwrap(load_document(args.file), "actuation_slice")
        errors, warnings = validate_slice(body)
    except Exception as exc:
        errors, warnings, body = [str(exc)], [], {}
    policy = body.get("policy_control") if isinstance(body, dict) else None
    result = {
        "actuation_slice_gate": {
            "verdict": "pass" if not errors else "fail",
            "run_id": body.get("run_id"),
            "slice_id": body.get("slice_id"),
            "state": body.get("state"),
            "policy_action_id": policy.get("action_id") if isinstance(policy, dict) else None,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
