#!/usr/bin/env python3
"""Validate fixed_point_slice_result / FPSR-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROUTES = {
    "reuse_existing_owner",
    "delete_or_collapse",
    "canonicalize",
    "representation_change",
    "bounded_new_surface",
}
RESULTS = {"valid", "return_to_frontier", "blocked", "invalid"}
PROOF = {"pass", "fail", "blocked", "missing", "stale"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    body = value.get("fixed_point_slice_result", value) if isinstance(value, dict) else value
    if not isinstance(body, dict):
        raise ValueError("fixed_point_slice_result must be an object")
    return body


def obj(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{prefix}{key}:must-be-object")
        return {}
    return value


def arr(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        errors.append(f"{prefix}{key}:must-be-list")
        return []
    return value


def required(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> Any:
    value = parent.get(key)
    if value is None or value == "":
        errors.append(f"{prefix}{key}:missing")
    return value


def is_within_scope(path: str, allowed: list[str]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    for item in allowed:
        candidate = str(item).replace("\\", "/").rstrip("/").lstrip("./")
        if normalized == candidate or normalized.startswith(candidate + "/"):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--handoff", help="Optional ARH-v1 file for strict boundary comparison.")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        result = load(args.file)
    except Exception as exc:
        print(json.dumps({"fpsr_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if result.get("result_version") != "FPSR-v1":
        errors.append("result_version")
    for key in (
        "run_id",
        "slice_id",
        "gcr_id",
        "afr_id",
        "artifact_state_before",
        "artifact_state_after",
        "canonical_owner",
        "patch_ref",
        "reason",
    ):
        required(result, key, errors)

    route = result.get("selected_route")
    if route not in ROUTES:
        errors.append("selected_route")
    permitted = arr(result, "permitted_scope", errors)
    if not permitted:
        errors.append("permitted_scope:empty")
    changed = arr(result, "files_changed", errors)
    for path in changed:
        if not isinstance(path, str) or not is_within_scope(path, permitted):
            errors.append(f"files_changed:outside-permitted-scope:{path}")

    construct_map = arr(result, "construct_map", errors)
    construct_names: set[str] = set()
    for index, row in enumerate(construct_map):
        prefix = f"construct_map[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}:must-be-object")
            continue
        for key in ("construct", "kind", "class_id", "invariant", "route"):
            required(row, key, errors, f"{prefix}.")
        arr(row, "proof_ids", errors, f"{prefix}.")
        if row.get("route") != route:
            errors.append(f"{prefix}.route:mismatch")
        name = row.get("construct")
        if name in construct_names:
            errors.append(f"{prefix}.construct:duplicate")
        if isinstance(name, str):
            construct_names.add(name)

    surfaces = obj(result, "surfaces", errors)
    surface_values: dict[str, int] = {}
    for key in (
        "helpers_added",
        "branches_added",
        "fields_added",
        "public_symbols_added",
        "fallback_paths_added",
        "test_families_added",
    ):
        value = surfaces.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"surfaces.{key}")
            value = 0
        surface_values[key] = value
    arr(surfaces, "surfaces_retired", errors, "surfaces.")

    proof = obj(result, "proof", errors)
    obligations = arr(proof, "obligations", errors, "proof.")
    commands = arr(proof, "commands", errors, "proof.")
    evidence = arr(proof, "evidence_refs", errors, "proof.")
    if proof.get("status") not in PROOF:
        errors.append("proof.status")
    if proof.get("status") == "pass" and (not obligations or not commands or not evidence):
        errors.append("proof:pass-requires-obligation-command-evidence")

    orphans = arr(result, "orphan_constructs", errors)
    scope_violations = arr(result, "scope_violations", errors)
    budget_violations = arr(result, "budget_violations", errors)
    observations = arr(result, "new_observations", errors)
    result_state = result.get("result")
    if result_state not in RESULTS:
        errors.append("result")

    if result_state == "valid":
        if proof.get("status") != "pass":
            errors.append("valid:proof-not-pass")
        if orphans:
            errors.append("valid:orphan-constructs")
        if scope_violations:
            errors.append("valid:scope-violations")
        if budget_violations:
            errors.append("valid:budget-violations")
        if observations:
            errors.append("valid:new-observations")
    elif result_state == "return_to_frontier":
        if not observations:
            errors.append("return_to_frontier:new-observations-empty")
    elif result_state == "invalid":
        if not (orphans or scope_violations or budget_violations or proof.get("status") == "fail"):
            warnings.append("invalid:no-concrete-violation")
    elif result_state == "blocked":
        if proof.get("status") == "pass":
            warnings.append("blocked:proof-pass")

    if args.handoff:
        try:
            raw = json.loads(Path(args.handoff).read_text(encoding="utf-8"))
            handoff = raw.get("actuation_realization_handoff", raw)
        except Exception as exc:
            errors.append(f"handoff:read-failed:{exc}")
            handoff = {}
        for key in ("run_id", "slice_id", "gcr_id", "afr_id", "selected_route", "canonical_owner"):
            if handoff.get(key) != result.get(key):
                errors.append(f"handoff:{key}:mismatch")
        hscope = handoff.get("permitted_scope")
        if isinstance(hscope, list) and hscope != permitted:
            errors.append("handoff:permitted_scope:mismatch")
        hbudget = handoff.get("surface_budget", {})
        mapping = {
            "helpers_added": "helpers_added_max",
            "branches_added": "branches_added_max",
            "fields_added": "fields_added_max",
            "public_symbols_added": "public_symbols_added_max",
            "fallback_paths_added": "fallback_paths_added_max",
            "test_families_added": "test_families_added_max",
        }
        for actual_key, max_key in mapping.items():
            limit = hbudget.get(max_key)
            if isinstance(limit, int) and surface_values[actual_key] > limit:
                errors.append(f"handoff:surface-budget-exceeded:{actual_key}")

    result_out = {
        "fpsr_gate": {
            "verdict": "pass" if not errors else "fail",
            "run_id": result.get("run_id"),
            "slice_id": result.get("slice_id"),
            "result": result_state,
            "selected_route": route,
            "proof_status": proof.get("status"),
            "return_required": result_state == "return_to_frontier",
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result_out, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
