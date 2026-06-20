#!/usr/bin/env python3
"""Validate zig_semantic_route / ZSR-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

FAMILIES = {
    "claim-binding",
    "lifetime-escape",
    "atomic-transition",
    "verifier-completeness",
    "repo-closure",
    "proof-context",
}

SURFACES = {
    "migration",
    "API/domain-design",
    "build/package/dependency",
    "comptime/reflection/codegen",
    "formatting/lint",
    "testing/fuzzing/failure-discovery",
    "hazardous-low-level-code",
    "allocator/ownership/lifetime",
    "FFI/layout/wire/MMIO",
    "I/O/effects",
    "concurrency/atomics/cancellation",
    "performance/profiling",
    "cache/disk-operations",
}

YES = {"yes", True}
NO = {"no", False}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        value = json.loads(text)
    else:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML routes")
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("route must be an object")
    body = value.get("zig_semantic_route", value)
    if not isinstance(body, dict):
        raise ValueError("zig_semantic_route must be an object")
    return body


def list_of_strings(
    value: Any,
    field: str,
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{field}:must-be-string-list")
        return []
    if nonempty and not value:
        errors.append(f"{field}:empty")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    try:
        route = load(args.file)
    except Exception as exc:
        print(json.dumps({"zig_semantic_route_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if route.get("route_version") != "ZSR-v1":
        errors.append("route_version")

    artifact = route.get("artifact_state")
    if not isinstance(artifact, dict):
        errors.append("artifact_state:must-be-object")
        artifact = {}
    for field in ["repository_root", "head", "dirty_fingerprint", "zig_version"]:
        if artifact.get(field) in (None, ""):
            errors.append(f"artifact_state.{field}:missing")

    surfaces = list_of_strings(route.get("task_surfaces"), "task_surfaces", errors, nonempty=True)
    for surface in surfaces:
        if surface not in SURFACES:
            warnings.append(f"task_surfaces:unknown:{surface}")

    material = route.get("material")
    if material not in YES | NO:
        errors.append("material:expected-yes-or-no")

    families = list_of_strings(route.get("active_families"), "active_families", errors)
    if len(set(families)) != len(families):
        errors.append("active_families:duplicate")
    for family in families:
        if family not in FAMILIES:
            errors.append(f"active_families:unknown:{family}")

    if material in YES:
        if not route.get("owner"):
            errors.append("owner:missing")
        if not route.get("concrete_counterexample"):
            errors.append("concrete_counterexample:missing")
        if not route.get("selected_repair_boundary"):
            errors.append("selected_repair_boundary:missing")
        list_of_strings(route.get("required_proof"), "required_proof", errors, nonempty=True)
        list_of_strings(route.get("forbidden_shortcuts"), "forbidden_shortcuts", errors, nonempty=True)
        if not families and not route.get("no_family_reason"):
            errors.append("no_family_reason:missing")
    else:
        if families:
            warnings.append("nonmaterial-route-has-active-families")
        if not route.get("no_family_reason"):
            errors.append("no_family_reason:missing")

    contracts = route.get("family_contracts")
    if not isinstance(contracts, dict):
        errors.append("family_contracts:must-be-object")
        contracts = {}
    for family in families:
        contract = contracts.get(family)
        if not isinstance(contract, dict) or not contract:
            errors.append(f"family_contracts.{family}:missing")
            continue
        if not contract.get("question"):
            errors.append(f"family_contracts.{family}.question:missing")
        if not contract.get("proof"):
            errors.append(f"family_contracts.{family}.proof:missing")

    proof_epoch_required = route.get("proof_epoch_required")
    if proof_epoch_required not in YES | NO:
        errors.append("proof_epoch_required:expected-yes-or-no")
    if material in YES and proof_epoch_required not in YES:
        errors.append("proof_epoch_required:material-route-must-require")

    gate = route.get("gate")
    if not isinstance(gate, dict):
        errors.append("gate:must-be-object")
        gate = {}
    if gate.get("classified_before_first_edit") not in YES:
        errors.append("gate.classified_before_first_edit:not-yes")
    if gate.get("mutation_allowed") not in YES | NO:
        errors.append("gate.mutation_allowed:expected-yes-or-no")

    if errors and gate.get("mutation_allowed") in YES:
        errors.append("gate.mutation_allowed:cannot-be-yes-with-errors")

    result = {
        "zig_semantic_route_gate": {
            "verdict": "pass" if not errors else "fail",
            "material": material in YES,
            "active_families": families,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
