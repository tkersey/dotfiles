#!/usr/bin/env python3
"""Validate change_set / CS-v1 and claim-scope coverage."""

from __future__ import annotations

import argparse
from pathlib import PurePosixPath

from common import (
    emit,
    list_field,
    load_document,
    normalized_repo_path,
    object_field,
    parse_resource_root,
    require,
    unwrap,
    valid_digest,
    valid_plan_id,
)


def path_covered(path: str, resources: list[dict]) -> bool:
    path_parts = PurePosixPath(path).parts
    for resource in resources:
        if not isinstance(resource, dict):
            continue
        root = resource.get("root")
        mode = resource.get("mode")
        if mode not in {"write", "exclusive"} or not isinstance(root, str):
            continue
        try:
            kind, value = parse_resource_root(root)
        except ValueError:
            continue
        if kind == "repo":
            return True
        if kind == "path":
            root_parts = PurePosixPath(value).parts
            if path_parts[: len(root_parts)] == root_parts:
                return True
        if kind == "symbol" and value.split("#", 1)[0] == path:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        cs = unwrap(load_document(args.file), "change_set")
    except Exception as exc:
        return emit("changeset_gate", {}, [str(exc)], [])

    if cs.get("change_set_version") != "CS-v1":
        errors.append("change_set_version")
    for key in (
        "change_set_id",
        "workspace_id",
        "plan_id",
        "claim_id",
        "base_branch",
        "base_head",
        "worktree_ref",
    ):
        require(cs, key, errors)
    if not valid_plan_id(cs.get("plan_id")):
        errors.append("plan_id")
    for key in ("fencing_token", "workspace_sequence", "plan_sequence", "branch_epoch"):
        if not isinstance(cs.get(key), int) or cs.get(key, -1) < 0:
            errors.append(key)

    item_ids = list_field(cs, "item_ids", errors)
    if not item_ids:
        errors.append("item_ids:empty")
    changed = list_field(cs, "changed_paths", errors)
    if not changed:
        errors.append("changed_paths:empty")
    for path in changed:
        if not normalized_repo_path(path):
            errors.append(f"changed_paths:invalid:{path}")

    resources = list_field(cs, "resource_roots", errors)
    if not resources:
        errors.append("resource_roots:empty")
    for index, resource in enumerate(resources):
        if not isinstance(resource, dict):
            errors.append(f"resource_roots[{index}]:must-be-object")
            continue
        root = resource.get("root")
        if not isinstance(root, str):
            errors.append(f"resource_roots[{index}].root")
        else:
            try:
                parse_resource_root(root)
            except ValueError as exc:
                errors.append(f"resource_roots[{index}].root:{exc}")
        if resource.get("mode") not in {"read", "write", "exclusive"}:
            errors.append(f"resource_roots[{index}].mode")

    uncovered = [path for path in changed if not path_covered(path, resources)]
    if uncovered:
        errors.append("changed_paths:outside-claim:" + ",".join(uncovered))

    for key in ("patch_digest", "resulting_tree_digest"):
        if not valid_digest(cs.get(key)):
            errors.append(key)
    list_field(cs, "focused_proof_refs", errors)
    list_field(cs, "integration_proof_required", errors)
    if cs.get("status") not in {
        "sealed",
        "queued",
        "integrated",
        "rejected",
        "superseded",
    }:
        errors.append("status")

    lineage = object_field(cs, "lineage", errors)
    for key in ("workspace_ref", "plan_ref", "claim_ref", "gcr_ref"):
        require(lineage, key, errors, "lineage.")

    return emit(
        "changeset_gate",
        {
            "change_set_id": cs.get("change_set_id"),
            "plan_id": cs.get("plan_id"),
            "claim_id": cs.get("claim_id"),
            "changed_paths": changed,
            "uncovered_paths": uncovered,
            "status": cs.get("status"),
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
