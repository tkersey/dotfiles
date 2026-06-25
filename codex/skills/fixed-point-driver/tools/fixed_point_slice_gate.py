#!/usr/bin/env python3
"""Validate FPS-v1 input and optional FPSR-v1 result, including EPG lineage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

try:
    import yaml
except ImportError:  # optional
    yaml = None

RESULTS = {"valid", "no_change", "return_to_frontier", "blocked", "invalid"}
ACTION_KINDS = {"inspect", "probe", "decide", "mutate", "prove", "stabilize", "deploy", "rollback"}


def load(path: str) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    value = json.loads(text) if path.endswith(".json") or yaml is None else yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("document must be an object")
    return value


def body(value: dict[str, Any], key: str) -> dict[str, Any]:
    result = value.get(key, value)
    if not isinstance(result, dict):
        raise ValueError(f"{key} must be an object")
    return result


def yes(value: Any) -> bool:
    return value is True or value == "yes"


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", value))


def path_allowed(path: str, boundaries: list[str]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    for item in boundaries:
        candidate = str(item).replace("\\", "/").lstrip("./").rstrip("/")
        if normalized == candidate or normalized.startswith(candidate + "/"):
            return True
    return False


def validate_policy_control(value: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    policy = value.get("policy_control")
    if policy is None:
        return None
    if not isinstance(policy, dict):
        errors.append("policy_control:object")
        return None
    if policy.get("mode") != "epg":
        errors.append("policy_control.mode")
    for key in ("policy_id", "state_id", "decision_id", "action_id"):
        if not policy.get(key):
            errors.append(f"policy_control.{key}")
    revision = policy.get("policy_revision")
    if not isinstance(revision, int) or revision < 1:
        errors.append("policy_control.policy_revision")
    for key in ("policy_digest", "state_digest"):
        if not valid_digest(policy.get(key)):
            errors.append(f"policy_control.{key}")
    if policy.get("action_kind") not in ACTION_KINDS:
        errors.append("policy_control.action_kind")
    sequence = policy.get("commitment_horizon_sequence")
    if not isinstance(sequence, int) or sequence < 1:
        errors.append("policy_control.commitment_horizon_sequence")
    if not isinstance(policy.get("expected_effects"), dict):
        errors.append("policy_control.expected_effects:object")
    for key in ("expected_observation_refs", "failure_observation_refs"):
        if not isinstance(policy.get(key), list):
            errors.append(f"policy_control.{key}:list")
    return policy


def validate_input(value: dict[str, Any]) -> tuple[list[str], dict[str, Any] | None]:
    errors: list[str] = []
    if value.get("slice_version") != "FPS-v1":
        errors.append("slice_version")
    for key in (
        "slice_id",
        "artifact_state",
        "graph_control_ref",
        "actuation_slice_ref",
        "owner",
        "invariant",
        "selected_normal_form",
        "patch_boundary",
        "surface_budget",
        "gate",
    ):
        if value.get(key) in (None, "", [], {}):
            errors.append(key)
    for key in (
        "st_task_refs",
        "semantic_route_refs",
        "selected_rows",
        "alternatives",
        "forbidden_actions",
        "proof_obligations",
        "stop_conditions",
    ):
        if not isinstance(value.get(key), list):
            errors.append(f"{key}:list")
    if not value.get("st_task_refs"):
        errors.append("st_task_refs:empty")
    if not value.get("selected_rows") and not value.get("proof_obligations"):
        errors.append("selected_rows-or-proof-obligations-required")
    if not value.get("alternatives"):
        errors.append("alternatives:empty")
    boundary = value.get("patch_boundary", {})
    if isinstance(boundary, dict):
        if not isinstance(boundary.get("files"), list) or not isinstance(boundary.get("symbols"), list):
            errors.append("patch_boundary:lists")
        elif not boundary["files"] and not boundary["symbols"]:
            errors.append("patch_boundary:empty")
    gate = value.get("gate", {})
    if not isinstance(gate, dict):
        errors.append("gate:object")
    else:
        if not yes(gate.get("prepared")):
            errors.append("gate.prepared")
        if not yes(gate.get("mutation_allowed")):
            errors.append("gate.mutation_allowed")
    policy = validate_policy_control(value, errors)
    return errors, policy


def validate_policy_result(
    value: dict[str, Any],
    policy: dict[str, Any],
    result_state: str | None,
    new_observations: list[Any],
    errors: list[str],
) -> None:
    policy_result = value.get("policy_result")
    if not isinstance(policy_result, dict):
        errors.append("policy_result:required-for-epg")
        return
    for key in ("policy_id", "policy_revision", "policy_digest", "state_id", "decision_id", "action_id"):
        if policy_result.get(key) != policy.get(key):
            errors.append(f"policy_result.{key}:mismatch")
    effects = policy_result.get("observed_effects")
    if not isinstance(effects, dict):
        errors.append("policy_result.observed_effects:object")
        effects = {}
    for key in ("facts_added", "unknowns_resolved", "obligations_closed"):
        if not isinstance(effects.get(key), list):
            errors.append(f"policy_result.observed_effects.{key}:list")
    observations = policy_result.get("observations")
    if not isinstance(observations, list):
        errors.append("policy_result.observations:list")
        observations = []
    for index, row in enumerate(observations):
        if not isinstance(row, dict):
            errors.append(f"policy_result.observations[{index}]:object")
            continue
        for key in ("observation_id", "outcome", "evidence_ref"):
            if not row.get(key):
                errors.append(f"policy_result.observations[{index}].{key}")
    invalidated = policy_result.get("prediction_invalidated")
    if not isinstance(invalidated, bool):
        errors.append("policy_result.prediction_invalidated:bool")
        invalidated = False

    expected = policy.get("expected_effects", {})
    unexpected: list[str] = []
    for key in ("facts_added", "unknowns_resolved", "obligations_closed"):
        expected_values = set(expected.get(key, [])) if isinstance(expected, dict) else set()
        observed_values = set(effects.get(key, [])) if isinstance(effects, dict) else set()
        for item in sorted(observed_values - expected_values):
            unexpected.append(f"{key}:{item}")
    expected_obs = set(policy.get("expected_observation_refs", [])) | set(policy.get("failure_observation_refs", []))
    for row in observations:
        if isinstance(row, dict) and row.get("observation_id") not in expected_obs:
            unexpected.append(f"observation:{row.get('observation_id')}")

    if unexpected and not invalidated:
        errors.append("policy_result.unexpected-effects-without-invalidation:" + ",".join(unexpected))
    if (invalidated or unexpected or new_observations) and result_state != "return_to_frontier":
        errors.append("policy_result.invalidation-requires-return-to-frontier")
    if result_state == "valid" and invalidated:
        errors.append("valid:prediction-invalidated")


def validate_result(
    value: dict[str, Any],
    input_value: dict[str, Any],
    policy: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    if value.get("result_version") != "FPSR-v1":
        errors.append("result_version")
    if value.get("slice_id") != input_value.get("slice_id"):
        errors.append("slice_id:mismatch")
    for key in ("artifact_state", "owner", "invariant", "surface_delta", "budget", "result"):
        if value.get(key) in (None, "", [], {}):
            errors.append(key)
    if value.get("owner") != input_value.get("owner"):
        errors.append("owner:mismatch")
    if value.get("invariant") != input_value.get("invariant"):
        errors.append("invariant:mismatch")
    for key in (
        "selected_rows",
        "changed_files",
        "changed_symbols",
        "construct_map",
        "proof_refs",
        "obligations_covered",
        "new_observations",
    ):
        if not isinstance(value.get(key), list):
            errors.append(f"{key}:list")
    result_state = value.get("result")
    if result_state not in RESULTS:
        errors.append("result")

    boundary = input_value.get("patch_boundary", {})
    allowed_files = boundary.get("files", []) if isinstance(boundary, dict) else []
    allowed_symbols = boundary.get("symbols", []) if isinstance(boundary, dict) else []
    for path in value.get("changed_files", []):
        if not path_allowed(str(path), [str(item) for item in allowed_files]):
            errors.append(f"changed_files:outside-boundary:{path}")
    if allowed_symbols:
        for symbol in value.get("changed_symbols", []):
            if symbol not in allowed_symbols:
                errors.append(f"changed_symbols:outside-boundary:{symbol}")

    construct_map = value.get("construct_map", [])
    for index, row in enumerate(construct_map):
        if not isinstance(row, dict):
            errors.append(f"construct_map[{index}]:object")
            continue
        for key in ("construct", "owner", "invariant"):
            if not row.get(key):
                errors.append(f"construct_map[{index}].{key}")
        if row.get("owner") != input_value.get("owner"):
            errors.append(f"construct_map[{index}].owner:mismatch")
        if row.get("invariant") != input_value.get("invariant"):
            errors.append(f"construct_map[{index}].invariant:mismatch")
        if not isinstance(row.get("row_refs", []), list):
            errors.append(f"construct_map[{index}].row_refs:list")
        if policy is not None:
            if not isinstance(row.get("obligation_refs"), list) or not row.get("obligation_refs"):
                errors.append(f"construct_map[{index}].obligation_refs:required-for-epg")
            if not isinstance(row.get("proof_refs"), list) or not row.get("proof_refs"):
                errors.append(f"construct_map[{index}].proof_refs:required-for-epg")

    surface = value.get("surface_delta", {})
    budget = input_value.get("surface_budget", {})
    mapping = {
        "files": "max_files",
        "production_net": "max_production_net",
        "new_private_helpers": "max_new_private_helpers",
        "new_public_symbols": "max_new_public_symbols",
        "new_state_fields": "max_new_state_fields",
        "new_test_families": "max_new_test_families",
    }
    derived_violations: list[str] = []
    if isinstance(surface, dict) and isinstance(budget, dict):
        for actual_key, max_key in mapping.items():
            if max_key not in budget:
                continue
            actual = surface.get(actual_key, 0)
            maximum = budget.get(max_key)
            if not isinstance(actual, int) or not isinstance(maximum, int):
                errors.append(f"surface-budget:{actual_key}:integer-required")
            elif actual > maximum:
                derived_violations.append(f"{actual_key}:{actual}>{maximum}")
    budget_result = value.get("budget", {})
    if not isinstance(budget_result, dict):
        errors.append("budget:object")
        budget_result = {}
    declared_violations = budget_result.get("violations")
    if not isinstance(declared_violations, list):
        errors.append("budget.violations:list")
        declared_violations = []
    if yes(budget_result.get("respected")) == bool(derived_violations):
        errors.append("budget.respected:contradicts-derived-value")
    if derived_violations and not declared_violations:
        errors.append("budget.violations:missing-derived-violations")

    observations = value.get("new_observations", [])
    if result_state == "valid":
        if observations:
            errors.append("valid:new-observations-present")
        if derived_violations or not yes(budget_result.get("respected")):
            errors.append("valid:budget-not-respected")
        if not value.get("proof_refs"):
            errors.append("valid:proof-refs-empty")
        expected = set(input_value.get("proof_obligations", []))
        covered = set(value.get("obligations_covered", []))
        missing = expected - covered
        if missing:
            errors.append("valid:missing-obligations:" + ",".join(sorted(missing)))
    if observations and result_state != "return_to_frontier":
        errors.append("new-observations-require-return-to-frontier")
    if result_state == "return_to_frontier" and not observations and policy is None:
        errors.append("return_to_frontier:new-observations-required")

    if policy is not None:
        validate_policy_result(value, policy, result_state, observations, errors)
    elif value.get("policy_result") is not None:
        errors.append("policy_result:forbidden-without-policy-control")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--result")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        input_value = body(load(args.input), "fixed_point_slice")
        input_errors, policy = validate_input(input_value)
        errors.extend("input." + error for error in input_errors)
        result_value = None
        if args.result:
            result_value = body(load(args.result), "fixed_point_slice_result")
            errors.extend("result." + error for error in validate_result(result_value, input_value, policy))
    except Exception as exc:
        input_value = {}
        result_value = None
        policy = None
        errors.append(str(exc))

    output = {
        "fixed_point_slice_gate": {
            "verdict": "pass" if not errors else "fail",
            "slice_id": input_value.get("slice_id"),
            "policy_action_id": policy.get("action_id") if isinstance(policy, dict) else None,
            "result": result_value.get("result") if result_value else None,
            "errors": errors,
        }
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
