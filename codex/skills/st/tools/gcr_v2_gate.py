#!/usr/bin/env python3
"""Validate graph_control_receipt / GCR-v2."""

from __future__ import annotations

import argparse

from common import (
    emit,
    list_field,
    load_document,
    object_field,
    parse_resource_root,
    require,
    unwrap,
    valid_digest,
    valid_plan_id,
    yes,
    no,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        gcr = unwrap(load_document(args.file), "graph_control_receipt")
    except Exception as exc:
        return emit("gcr_v2_gate", {}, [str(exc)], [])

    if gcr.get("receipt_version") != "GCR-v2":
        errors.append("receipt_version")
    require(gcr, "gcr_id", errors)

    workspace = object_field(gcr, "workspace", errors)
    for key in (
        "workspace_id",
        "target_branch",
        "head",
        "working_tree_fingerprint",
    ):
        require(workspace, key, errors, "workspace.")
    for key in ("workspace_sequence", "branch_epoch"):
        if not isinstance(workspace.get(key), int) or workspace.get(key, -1) < 0:
            errors.append(f"workspace.{key}")
    if not valid_digest(workspace.get("working_tree_fingerprint")):
        errors.append("workspace.working_tree_fingerprint")

    plan = object_field(gcr, "plan", errors)
    for key in ("plan_id", "plan_sequence"):
        require(plan, key, errors, "plan.")
    if not valid_plan_id(plan.get("plan_id")):
        errors.append("plan.plan_id")
    if not isinstance(plan.get("plan_sequence"), int) or plan.get("plan_sequence", -1) < 0:
        errors.append("plan.plan_sequence")
    selected = list_field(plan, "selected_task_ids", errors, "plan.")
    fingerprints = object_field(plan, "graph_fingerprints", errors, "plan.")
    for key in ("structure", "contract", "coverage", "execution"):
        if not valid_digest(fingerprints.get(key)):
            errors.append(f"plan.graph_fingerprints.{key}")

    coordination = object_field(gcr, "coordination", errors)
    for key in ("claim_id", "session_id", "executor"):
        require(coordination, key, errors, "coordination.")
    for key in ("fencing_token", "workspace_sequence", "plan_sequence", "branch_epoch"):
        if not isinstance(coordination.get(key), int) or coordination.get(key, -1) < 0:
            errors.append(f"coordination.{key}")
    resources = list_field(coordination, "resources", errors, "coordination.")
    for index, resource in enumerate(resources):
        if not isinstance(resource, dict):
            errors.append(f"coordination.resources[{index}]:must-be-object")
            continue
        root = resource.get("root")
        if not isinstance(root, str):
            errors.append(f"coordination.resources[{index}].root")
        else:
            try:
                parse_resource_root(root)
            except ValueError as exc:
                errors.append(f"coordination.resources[{index}].root:{exc}")
        if resource.get("mode") not in {"read", "write", "exclusive"}:
            errors.append(f"coordination.resources[{index}].mode")
    conflicts = list_field(coordination, "conflicting_claims", errors, "coordination.")
    if not isinstance(coordination.get("lease_current"), bool):
        errors.append("coordination.lease_current")
    if not isinstance(coordination.get("fencing_current"), bool):
        errors.append("coordination.fencing_current")

    graph = object_field(gcr, "graph", errors)
    ready = list_field(graph, "ready_frontier", errors, "graph.")
    blocked = list_field(graph, "blocked_frontier", errors, "graph.")
    list_field(graph, "critical_path", errors, "graph.")
    list_field(graph, "proof_cut", errors, "graph.")
    debt = list_field(graph, "graph_debt", errors, "graph.")
    if graph.get("gate") not in {
        "draft",
        "implementation-ready",
        "execution-ready",
        "proof-complete",
    }:
        errors.append("graph.gate")
    if not isinstance(graph.get("gate_passed"), bool):
        errors.append("graph.gate_passed")

    projection = object_field(gcr, "projection", errors)
    for key in ("view_id", "projection_digest"):
        require(projection, key, errors, "projection.")
    if not valid_digest(projection.get("projection_digest")):
        errors.append("projection.projection_digest")
    if projection.get("session_id") != coordination.get("session_id"):
        errors.append("projection.session_id:mismatch")
    projected = list_field(projection, "selected_task_ids", errors, "projection.")
    if projected != selected:
        errors.append("projection.selected_task_ids:mismatch")

    allowed = gcr.get("execution_allowed")
    if not (yes(allowed) or no(allowed)):
        errors.append("execution_allowed")
    denial = list_field(gcr, "denial_reasons", errors)

    prerequisites = (
        bool(selected)
        and not conflicts
        and coordination.get("lease_current") is True
        and coordination.get("fencing_current") is True
        and coordination.get("workspace_sequence") == workspace.get("workspace_sequence")
        and coordination.get("plan_sequence") == plan.get("plan_sequence")
        and coordination.get("branch_epoch") == workspace.get("branch_epoch")
        and graph.get("gate_passed") is True
        and not debt
    )

    if yes(allowed) and not prerequisites:
        errors.append("execution_allowed:prerequisites-fail")
    if yes(allowed) and denial:
        errors.append("execution_allowed:denial-reasons-present")
    if no(allowed) and not denial:
        errors.append("execution_denied:reason-required")
    if prerequisites and no(allowed):
        warnings.append("execution_allowed:no-despite-prerequisites")
    if not selected and yes(allowed):
        errors.append("execution_allowed:no-selected-tasks")

    return emit(
        "gcr_v2_gate",
        {
            "gcr_id": gcr.get("gcr_id"),
            "workspace_id": workspace.get("workspace_id"),
            "plan_id": plan.get("plan_id"),
            "session_id": coordination.get("session_id"),
            "claim_id": coordination.get("claim_id"),
            "selected_tasks": selected,
            "execution_allowed": allowed,
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
