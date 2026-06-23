#!/usr/bin/env python3
"""Validate actuation_realization_handoff / ARH-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

IMPLEMENTATION_ROUTES = {
    "reuse_existing_owner",
    "delete_or_collapse",
    "canonicalize",
    "representation_change",
    "bounded_new_surface",
}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    body = value.get("actuation_realization_handoff", value) if isinstance(value, dict) else value
    if not isinstance(body, dict):
        raise ValueError("actuation_realization_handoff must be an object")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        handoff = load(args.file)
    except Exception as exc:
        print(json.dumps({"arh_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if handoff.get("handoff_version") != "ARH-v1":
        errors.append("handoff_version")
    for key in ("run_id", "slice_id", "gcr_id", "afr_id"):
        required(handoff, key, errors)

    tasks = arr(handoff, "st_task_ids", errors)
    if not tasks:
        errors.append("st_task_ids:empty")
    if len(tasks) != len(set(tasks)):
        errors.append("st_task_ids:duplicate")

    artifact = obj(handoff, "artifact_state", errors)
    for key in ("repository", "branch", "base", "head", "dirty_fingerprint"):
        required(artifact, key, errors, "artifact_state.")

    route = handoff.get("selected_route")
    if route not in IMPLEMENTATION_ROUTES:
        errors.append("selected_route:not-implementation-capable")

    owner = required(handoff, "canonical_owner", errors)
    scope = arr(handoff, "permitted_scope", errors)
    if not scope:
        errors.append("permitted_scope:empty")
    arr(handoff, "forbidden_actions", errors)
    arr(handoff, "non_goals", errors)

    budget = obj(handoff, "surface_budget", errors)
    for key in (
        "helpers_added_max",
        "branches_added_max",
        "fields_added_max",
        "public_symbols_added_max",
        "fallback_paths_added_max",
        "test_families_added_max",
    ):
        value = budget.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"surface_budget.{key}")
    arr(budget, "surfaces_to_retire", errors, "surface_budget.")

    cls = obj(handoff, "counterexample_class", errors)
    for key in ("class_id", "governing_invariant", "representative_witness"):
        required(cls, key, errors, "counterexample_class.")
    arr(cls, "covered_combinations", errors, "counterexample_class.")
    invariant = required(handoff, "invariant", errors)
    if cls.get("governing_invariant") != invariant:
        warnings.append("counterexample_class.governing_invariant:differs-from-invariant")

    proof = arr(handoff, "proof_obligations", errors)
    if not proof:
        errors.append("proof_obligations:empty")
    required(handoff, "proof_dag_ref", errors)

    result = {
        "arh_gate": {
            "verdict": "pass" if not errors else "fail",
            "run_id": handoff.get("run_id"),
            "slice_id": handoff.get("slice_id"),
            "selected_route": route,
            "canonical_owner": owner,
            "implementation_allowed": not errors,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
