#!/usr/bin/env python3
"""Validate actuation_frontier / AFR-v1 and derive mutation eligibility."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROUTES = {
    "no_change",
    "validate_only",
    "reuse_existing_owner",
    "delete_or_collapse",
    "canonicalize",
    "representation_change",
    "bounded_new_surface",
    "blocked",
}
MUTATION_ROUTES = {
    "reuse_existing_owner",
    "delete_or_collapse",
    "canonicalize",
    "representation_change",
    "bounded_new_surface",
}
CLASS_STATUS = {"open", "selected", "closed", "rejected", "unknown"}
PROOF_SCOPE = {"focused", "affected_aggregate", "full_closure"}
PROOF_STATUS = {"missing", "running", "pass", "fail", "stale"}
REALIZATION = {"not_started", "valid", "return_to_frontier", "blocked", "invalid"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    body = value.get("actuation_frontier", value) if isinstance(value, dict) else value
    if not isinstance(body, dict):
        raise ValueError("actuation_frontier must be an object")
    return body


def obj(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> dict[str, Any]:
    value = parent.get(key)
    name = f"{prefix}{key}"
    if not isinstance(value, dict):
        errors.append(f"{name}:must-be-object")
        return {}
    return value


def arr(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> list[Any]:
    value = parent.get(key)
    name = f"{prefix}{key}"
    if not isinstance(value, list):
        errors.append(f"{name}:must-be-list")
        return []
    return value


def nonempty(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> Any:
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
        afr = load(args.file)
    except Exception as exc:
        print(json.dumps({"afr_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if afr.get("record_version") != "AFR-v1":
        errors.append("record_version")
    for key in ("afr_id", "run_id", "slice_id"):
        nonempty(afr, key, errors)

    artifact = obj(afr, "artifact_state", errors)
    for key in ("repository", "branch", "base", "head", "dirty_fingerprint"):
        nonempty(artifact, key, errors, "artifact_state.")

    graph = obj(afr, "graph_binding", errors)
    for key in (
        "plan_ref",
        "plan_seq",
        "authority_id",
        "authority_ref",
        "structure_fingerprint",
        "contract_fingerprint",
        "coverage_fingerprint",
        "execution_fingerprint",
    ):
        nonempty(graph, key, errors, "graph_binding.")
    tasks = arr(graph, "selected_task_ids", errors, "graph_binding.")
    if not tasks:
        errors.append("graph_binding.selected_task_ids:empty")
    if len(tasks) != len(set(tasks)):
        errors.append("graph_binding.selected_task_ids:duplicate")
    if graph.get("execution_allowed") is not True:
        errors.append("graph_binding.execution_allowed:not-true")
    debt = arr(graph, "blocking_debt", errors, "graph_binding.")
    if debt:
        errors.append("graph_binding.blocking_debt:not-empty")

    contracts = obj(afr, "skill_contracts", errors)
    nonempty(contracts, "actuating", errors, "skill_contracts.")
    nonempty(contracts, "fixed_point_driver", errors, "skill_contracts.")
    if not isinstance(contracts.get("language_skills"), dict):
        errors.append("skill_contracts.language_skills:must-be-object")

    domain = obj(afr, "domain", errors)
    for key in ("owner", "invariant", "objective", "selected_class_id"):
        nonempty(domain, key, errors, "domain.")
    arr(domain, "non_goals", errors, "domain.")
    arr(domain, "prior_closed_classes", errors, "domain.")
    state_space = obj(domain, "state_space", errors, "domain.")
    dimensions = arr(state_space, "dimensions", errors, "domain.state_space.")
    if not dimensions:
        warnings.append("domain.state_space.dimensions:empty")
    arr(state_space, "observed_counterexamples", errors, "domain.state_space.")
    classes = arr(state_space, "equivalence_classes", errors, "domain.state_space.")
    class_ids: set[str] = set()
    selected_count = 0
    for index, row in enumerate(classes):
        prefix = f"domain.state_space.equivalence_classes[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}:must-be-object")
            continue
        class_id = row.get("class_id")
        if not isinstance(class_id, str) or not class_id:
            errors.append(f"{prefix}.class_id")
            continue
        if class_id in class_ids:
            errors.append(f"{prefix}.class_id:duplicate")
        class_ids.add(class_id)
        for key in ("governing_invariant", "canonical_owner", "representative_witness", "proof_obligation"):
            nonempty(row, key, errors, f"{prefix}.")
        arr(row, "covered_combinations", errors, f"{prefix}.")
        status = row.get("status")
        if status not in CLASS_STATUS:
            errors.append(f"{prefix}.status")
        if status == "selected":
            selected_count += 1
    if domain.get("selected_class_id") not in class_ids:
        errors.append("domain.selected_class_id:not-found")
    if selected_count != 1:
        errors.append("domain.state_space:selected-class-count-must-be-one")
    selected_row = next(
        (row for row in classes if isinstance(row, dict) and row.get("class_id") == domain.get("selected_class_id")),
        None,
    )
    if selected_row and selected_row.get("canonical_owner") != domain.get("owner"):
        warnings.append("domain.owner:differs-from-selected-class-owner")

    decision = obj(afr, "decision", errors)
    nonempty(decision, "question", errors, "decision.")
    alternatives = arr(decision, "alternatives", errors, "decision.")
    alternative_routes = []
    for index, row in enumerate(alternatives):
        if not isinstance(row, dict) or not row.get("route"):
            errors.append(f"decision.alternatives[{index}]")
            continue
        alternative_routes.append(row["route"])
        arr(row, "evidence_refs", errors, f"decision.alternatives[{index}].")
    route = decision.get("selected_route")
    if route not in ROUTES:
        errors.append("decision.selected_route")
    if route and route not in alternative_routes:
        errors.append("decision.selected_route:not-in-alternatives")
    rejected = arr(decision, "rejected_routes", errors, "decision.")
    for index, row in enumerate(rejected):
        if not isinstance(row, dict) or not row.get("route") or not row.get("reason"):
            errors.append(f"decision.rejected_routes[{index}]")
            continue
        arr(row, "evidence_refs", errors, f"decision.rejected_routes[{index}].")
    for key in ("canonical_owner", "route_flip_condition", "expected_outcome"):
        nonempty(decision, key, errors, "decision.")
    if decision.get("canonical_owner") != domain.get("owner"):
        errors.append("decision.canonical_owner:must-match-domain-owner")
    scope = arr(decision, "permitted_scope", errors, "decision.")
    if route in MUTATION_ROUTES and not scope:
        errors.append("decision.permitted_scope:empty-for-mutation")
    arr(decision, "forbidden_actions", errors, "decision.")

    budget = obj(decision, "surface_budget", errors, "decision.")
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
            errors.append(f"decision.surface_budget.{key}")
    arr(budget, "surfaces_to_retire", errors, "decision.surface_budget.")

    proof = obj(afr, "proof_dag", errors)
    nodes = arr(proof, "nodes", errors, "proof_dag.")
    proof_ids: set[str] = set()
    focused_count = 0
    for index, node in enumerate(nodes):
        prefix = f"proof_dag.nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{prefix}:must-be-object")
            continue
        proof_id = node.get("proof_id")
        if not isinstance(proof_id, str) or not proof_id:
            errors.append(f"{prefix}.proof_id")
            continue
        if proof_id in proof_ids:
            errors.append(f"{prefix}.proof_id:duplicate")
        proof_ids.add(proof_id)
        if node.get("scope") not in PROOF_SCOPE:
            errors.append(f"{prefix}.scope")
        if node.get("scope") == "focused":
            focused_count += 1
        nonempty(node, "command", errors, f"{prefix}.")
        arr(node, "dependencies", errors, f"{prefix}.")
        if node.get("status") not in PROOF_STATUS:
            errors.append(f"{prefix}.status")
        arr(node, "invalidators", errors, f"{prefix}.")
    if focused_count == 0:
        errors.append("proof_dag:no-focused-proof")
    selected_proofs = arr(proof, "selected_proof_ids", errors, "proof_dag.")
    if not selected_proofs:
        errors.append("proof_dag.selected_proof_ids:empty")
    for proof_id in selected_proofs:
        if proof_id not in proof_ids:
            errors.append(f"proof_dag.selected_proof_ids:unknown:{proof_id}")
    arr(proof, "current_receipts", errors, "proof_dag.")
    arr(proof, "stale_receipts", errors, "proof_dag.")

    specialists = obj(afr, "specialists", errors)
    for key in ("frontier_mapper_ref", "proof_mapper_ref", "wave_skeptic_ref"):
        if key not in specialists:
            errors.append(f"specialists.{key}:missing")

    realization = obj(afr, "realization", errors)
    if realization.get("result") not in REALIZATION:
        errors.append("realization.result")
    arr(realization, "new_observations", errors, "realization.")

    outcome = obj(afr, "outcome", errors)
    arr(outcome, "graph_updates", errors, "outcome.")
    if outcome.get("terminal") not in {True, False}:
        errors.append("outcome.terminal")

    receipt = obj(afr, "skill_decision_receipt", errors)
    if receipt.get("receipt_version") != "SDR-v1":
        errors.append("skill_decision_receipt.receipt_version")
    if receipt.get("skill") != "actuating":
        errors.append("skill_decision_receipt.skill")
    for key in ("decision_id", "question", "selected_route", "expected_outcome", "artifact_state"):
        nonempty(receipt, key, errors, "skill_decision_receipt.")
    for key in ("trigger_refs", "clause_refs", "alternatives_considered", "rejected_routes"):
        arr(receipt, key, errors, "skill_decision_receipt.")
    if receipt.get("selected_route") != route:
        errors.append("skill_decision_receipt.selected_route:mismatch")

    mutation_allowed = (
        not errors
        and route in MUTATION_ROUTES
        and graph.get("execution_allowed") is True
        and not debt
        and realization.get("result") in {"not_started", "return_to_frontier"}
    )
    if realization.get("result") == "return_to_frontier":
        mutation_allowed = False
        warnings.append("realization:return-to-frontier-requires-new-afr")

    result = {
        "afr_gate": {
            "verdict": "pass" if not errors else "fail",
            "afr_id": afr.get("afr_id"),
            "run_id": afr.get("run_id"),
            "slice_id": afr.get("slice_id"),
            "selected_route": route,
            "selected_class_id": domain.get("selected_class_id"),
            "mutation_allowed": mutation_allowed,
            "terminal": outcome.get("terminal"),
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
