#!/usr/bin/env python3
"""Validate session_view / SVW-v1."""

from __future__ import annotations

import argparse

from common import emit, list_field, load_document, require, unwrap, valid_digest, valid_plan_id, valid_timestamp


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        view = unwrap(load_document(args.file), "session_view")
    except Exception as exc:
        return emit("session_view_gate", {}, [str(exc)], [])

    if view.get("view_version") != "SVW-v1":
        errors.append("view_version")
    for key in (
        "session_id",
        "executor",
        "workspace_id",
        "plan_id",
        "claim_id",
        "projection_target",
        "projection_digest",
        "updated_at",
    ):
        require(view, key, errors)
    if not valid_plan_id(view.get("plan_id")):
        errors.append("plan_id")
    for key in ("fencing_token", "workspace_sequence", "plan_sequence", "branch_epoch"):
        if not isinstance(view.get(key), int) or view.get(key, -1) < 0:
            errors.append(key)
    selected = list_field(view, "selected_item_ids", errors)
    if len(selected) != len(set(selected)):
        errors.append("selected_item_ids:duplicates")
    if view.get("projection_target") not in {"codex", "opencode"}:
        errors.append("projection_target")
    if not valid_digest(view.get("projection_digest")):
        errors.append("projection_digest")
    if not valid_timestamp(view.get("updated_at")):
        errors.append("updated_at")
    return emit(
        "session_view_gate",
        {
            "session_id": view.get("session_id"),
            "plan_id": view.get("plan_id"),
            "claim_id": view.get("claim_id"),
            "selected_item_ids": selected,
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
