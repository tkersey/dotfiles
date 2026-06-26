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
    selected_frontier = list_field(graph, "selected_frontier", errors, "graph.")
    unselected_ready = list_field(graph, "unselected_ready", errors, "graph.")
    list_field(graph, "critical_path", errors, "graph.")
    list_field(graph, "downstream_unlocks", errors, "graph.")
    list_field(graph, "antichain_candidates", errors, "graph.")
    list_field(graph, "high_fanout_nodes", errors, "graph.")
    list_field(graph, "articulation_nodes", errors, "graph.")
    debt = list_field(graph, "graph_debt", errors, "graph.")
    if selected_frontier != selected:
        errors.append("graph.selected_frontier:plan-selected-mismatch")
    if any(task not in ready for task in selected_frontier):
        errors.append("graph.selected_frontier:not-ready")
    expected_unselected = [task for task in ready if task not in selected_frontier]
    if unselected_ready != expected_unselected:
        errors.append("graph.unselected_ready:ready-frontier-mismatch")
    if any(task in selected_frontier for task in unselected_ready):
        errors.append("graph.unselected_ready:contains-selected")
    parallel_width = graph.get("parallel_width")
    if not isinstance(parallel_width, int) or parallel_width < 0:
        errors.append("graph.parallel_width")
    if graph.get("gate") not in {
        "draft",
        "implementation-ready",
        "execution-ready",
        "proof-complete",
    }:
        errors.append("graph.gate")
    if not isinstance(graph.get("gate_passed"), bool):
        errors.append("graph.gate_passed")

    proof = object_field(gcr, "proof", errors)
    list_field(proof, "obligations", errors, "proof.")
    missing_proof = list_field(proof, "missing", errors, "proof.")
    minimum_proof_cut = list_field(proof, "minimum_proof_cut", errors, "proof.")
    proof_cut_kind = proof.get("proof_cut_kind")
    if proof_cut_kind not in {"exact", "approximation", "unavailable"}:
        errors.append("proof.proof_cut_kind")
    if proof_cut_kind == "approximation":
        require(proof, "approximation_basis", errors, "proof.")

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

    aperture = object_field(gcr, "aperture_decision", errors)
    aperture_selected = list_field(aperture, "selected_nodes", errors, "aperture_decision.")
    why_selected = list_field(aperture, "why_selected", errors, "aperture_decision.")
    why_not_parallelized = list_field(
        aperture, "why_not_parallelized", errors, "aperture_decision."
    )
    why_unselected_ready_waits = list_field(
        aperture, "why_unselected_ready_waits", errors, "aperture_decision."
    )
    if aperture_selected != selected_frontier:
        errors.append("aperture_decision.selected_nodes:frontier-mismatch")
    if selected_frontier and not why_selected:
        errors.append("aperture_decision.why_selected:empty")
    if (
        isinstance(parallel_width, int)
        and parallel_width > len(selected_frontier)
        and not why_not_parallelized
    ):
        errors.append("aperture_decision.why_not_parallelized:empty")
    if unselected_ready and not why_unselected_ready_waits:
        errors.append("aperture_decision.why_unselected_ready_waits:empty")

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
        and proof_cut_kind != "unavailable"
        and not missing_proof
        and bool(minimum_proof_cut)
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
    if yes(allowed) and proof_cut_kind == "unavailable":
        errors.append("execution_allowed:proof-cut-unavailable")

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
