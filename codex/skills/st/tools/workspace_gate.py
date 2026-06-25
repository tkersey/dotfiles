#!/usr/bin/env python3
"""Validate st_workspace / STW-v1."""

from __future__ import annotations

import argparse

from common import (
    emit,
    list_field,
    load_document,
    normalized_repo_path,
    object_field,
    require,
    unwrap,
    valid_digest,
    valid_plan_id,
    yes,
)

PLAN_STATES = {"active", "paused", "completed", "archived"}
EDGE_TYPES = {"blocks", "validates", "implements", "documents", "related"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        ws = unwrap(load_document(args.file), "st_workspace")
    except Exception as exc:
        return emit("workspace_gate", {}, [str(exc)], [])

    if ws.get("workspace_version") != "STW-v1":
        errors.append("workspace_version")
    for key in ("workspace_id", "artifact_root", "st_root"):
        require(ws, key, errors)
    if ws.get("artifact_root") != ".ledger":
        errors.append("artifact_root:must-be-.ledger")
    if ws.get("st_root") != ".ledger/st":
        errors.append("st_root:must-be-.ledger/st")
    if not isinstance(ws.get("sequence"), int) or ws.get("sequence", -1) < 0:
        errors.append("sequence")

    repo = object_field(ws, "repository", errors)
    for key in ("root", "identity", "target_branch", "head", "working_tree_fingerprint"):
        require(repo, key, errors, "repository.")
    if not isinstance(repo.get("branch_epoch"), int) or repo.get("branch_epoch", -1) < 0:
        errors.append("repository.branch_epoch")
    if not valid_digest(repo.get("working_tree_fingerprint")):
        errors.append("repository.working_tree_fingerprint")

    plans = list_field(ws, "plans", errors)
    if not plans:
        errors.append("plans:empty")
    plan_ids: set[str] = set()
    active_count = 0
    for index, plan in enumerate(plans):
        prefix = f"plans[{index}]."
        if not isinstance(plan, dict):
            errors.append(f"plans[{index}]:must-be-object")
            continue
        plan_id = plan.get("plan_id")
        if not valid_plan_id(plan_id):
            errors.append(f"{prefix}plan_id")
        elif plan_id in plan_ids:
            errors.append(f"plans:duplicate-plan-id:{plan_id}")
        else:
            plan_ids.add(plan_id)
        require(plan, "alias", errors, prefix)
        state = plan.get("state")
        if state not in PLAN_STATES:
            errors.append(f"{prefix}state")
        elif state == "active":
            active_count += 1
        graph_ref = plan.get("graph_ref")
        if not isinstance(graph_ref, str) or not graph_ref.startswith(
            f".ledger/st/plans/{plan_id}/"
        ):
            errors.append(f"{prefix}graph_ref")
        if plan.get("target_branch") != repo.get("target_branch"):
            warnings.append(f"{prefix}target_branch:differs-from-workspace")
        if not isinstance(plan.get("plan_sequence"), int) or plan.get("plan_sequence", -1) < 0:
            errors.append(f"{prefix}plan_sequence")
        source = object_field(plan, "source", errors, prefix)
        for key in ("kind", "locator", "fingerprint"):
            require(source, key, errors, prefix + "source.")
        if source.get("fingerprint") and not valid_digest(source.get("fingerprint")):
            errors.append(f"{prefix}source.fingerprint")
        fingerprints = object_field(plan, "graph_fingerprints", errors, prefix)
        for key in ("structure", "contract", "coverage", "execution"):
            if fingerprints.get(key) and not valid_digest(fingerprints.get(key)):
                errors.append(f"{prefix}graph_fingerprints.{key}")

    edges = list_field(ws, "cross_plan_dependencies", errors)
    edge_ids: set[str] = set()
    for index, edge in enumerate(edges):
        prefix = f"cross_plan_dependencies[{index}]."
        if not isinstance(edge, dict):
            errors.append(f"cross_plan_dependencies[{index}]:must-be-object")
            continue
        edge_id = require(edge, "edge_id", errors, prefix)
        if edge_id in edge_ids:
            errors.append(f"cross_plan_dependencies:duplicate:{edge_id}")
        if isinstance(edge_id, str):
            edge_ids.add(edge_id)
        for key in ("from", "to", "reason"):
            require(edge, key, errors, prefix)
        if edge.get("type") not in EDGE_TYPES:
            errors.append(f"{prefix}type")
        for key in ("from", "to"):
            ref = edge.get(key)
            if isinstance(ref, str) and ref.startswith("plan://"):
                rest = ref[len("plan://") :]
                ref_plan = rest.split("/", 1)[0]
                if ref_plan not in plan_ids:
                    errors.append(f"{prefix}{key}:unknown-plan:{ref_plan}")
            else:
                errors.append(f"{prefix}{key}:must-be-qualified-ref")

    policy = object_field(ws, "policy", errors)
    if not yes(policy.get("plan_required_when_multiple")):
        errors.append("policy.plan_required_when_multiple")
    if policy.get("unknown_scope_mode") != "repo-exclusive":
        errors.append("policy.unknown_scope_mode")
    if policy.get("worktree_mode") != "isolated-external":
        errors.append("policy.worktree_mode")
    if policy.get("integration_mode") != "serialized-cas":
        errors.append("policy.integration_mode")
    if policy.get("proof_invalidation_mode") != "dependency-cut":
        errors.append("policy.proof_invalidation_mode")
    for key in ("max_active_plans", "max_concurrent_claims"):
        if not isinstance(policy.get(key), int) or policy.get(key, 0) < 1:
            errors.append(f"policy.{key}")
    if active_count > policy.get("max_active_plans", 0):
        errors.append("policy.max_active_plans:exceeded")

    tx = object_field(ws, "transaction", errors)
    if not isinstance(tx.get("committed_sequence"), int) or tx.get("committed_sequence", -1) < 0:
        errors.append("transaction.committed_sequence")
    if tx.get("committed_sequence") != ws.get("sequence"):
        errors.append("transaction.committed_sequence:mismatch")
    if not isinstance(tx.get("recovery_required"), bool):
        errors.append("transaction.recovery_required")

    return emit(
        "workspace_gate",
        {
            "workspace_id": ws.get("workspace_id"),
            "sequence": ws.get("sequence"),
            "plans": len(plan_ids),
            "active_plans": active_count,
            "cross_plan_dependencies": len(edges),
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
