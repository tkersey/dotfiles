#!/usr/bin/env python3
"""Validate WCL-v1 claims and optionally detect conflicts."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from common import (
    emit,
    list_field,
    load_document,
    object_field,
    parse_resource_root,
    require,
    resource_modes_conflict,
    resource_overlap,
    unwrap,
    valid_plan_id,
    valid_timestamp,
)

MODES = {"read", "write", "exclusive"}
STATES = {"held", "released", "stale", "integrated"}


def parse_claim(value: dict, errors: list[str], label: str) -> dict:
    claim = value.get("workspace_claim", value)
    if not isinstance(claim, dict):
        errors.append(f"{label}:must-be-object")
        return {}
    if claim.get("claim_version") != "WCL-v1":
        errors.append(f"{label}.claim_version")
    for key in (
        "claim_id",
        "workspace_id",
        "plan_id",
        "session_id",
        "executor",
        "branch",
        "base_head",
    ):
        require(claim, key, errors, label + ".")
    if claim.get("plan_id") and not valid_plan_id(claim.get("plan_id")):
        errors.append(f"{label}.plan_id")
    for key in ("workspace_sequence", "plan_sequence", "branch_epoch", "lease_seconds", "fencing_token"):
        if not isinstance(claim.get(key), int) or claim.get(key, -1) < 0:
            errors.append(f"{label}.{key}")
    if claim.get("lease_seconds", 0) <= 0:
        errors.append(f"{label}.lease_seconds:must-be-positive")
    for key in ("claimed_at", "lease_expires_at", "heartbeat_at"):
        if not valid_timestamp(claim.get(key)):
            errors.append(f"{label}.{key}")
    if claim.get("state") not in STATES:
        errors.append(f"{label}.state")
    items = list_field(claim, "item_ids", errors, label + ".")
    if not items:
        errors.append(f"{label}.item_ids:empty")
    resources = list_field(claim, "resources", errors, label + ".")
    if not resources:
        errors.append(f"{label}.resources:empty")
    for index, resource in enumerate(resources):
        prefix = f"{label}.resources[{index}]."
        if not isinstance(resource, dict):
            errors.append(f"{label}.resources[{index}]:must-be-object")
            continue
        root = require(resource, "root", errors, prefix)
        if isinstance(root, str):
            try:
                parse_resource_root(root)
            except ValueError as exc:
                errors.append(f"{prefix}root:{exc}")
        if resource.get("mode") not in MODES:
            errors.append(f"{prefix}mode")
    return claim


def claims_conflict(left: dict, right: dict) -> list[tuple[str, str]]:
    if left.get("state") != "held" or right.get("state") != "held":
        return []
    if left.get("claim_id") == right.get("claim_id"):
        return []
    conflicts: list[tuple[str, str]] = []
    for lres in left.get("resources", []):
        if not isinstance(lres, dict):
            continue
        for rres in right.get("resources", []):
            if not isinstance(rres, dict):
                continue
            lroot, rroot = lres.get("root"), rres.get("root")
            lmode, rmode = lres.get("mode"), rres.get("mode")
            if (
                isinstance(lroot, str)
                and isinstance(rroot, str)
                and lmode in MODES
                and rmode in MODES
                and resource_overlap(lroot, rroot)
                and resource_modes_conflict(lmode, rmode)
            ):
                conflicts.append((lroot, rroot))
    return conflicts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--against")
    parser.add_argument("--now")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        claim = parse_claim(load_document(args.file), errors, "claim")
    except Exception as exc:
        return emit("claim_gate", {}, [str(exc)], [])

    if args.now:
        try:
            now = datetime.fromisoformat(args.now.replace("Z", "+00:00"))
            expiry = datetime.fromisoformat(
                str(claim.get("lease_expires_at", "")).replace("Z", "+00:00")
            )
            if expiry <= now and claim.get("state") == "held":
                errors.append("claim:held-but-expired")
        except ValueError:
            errors.append("now-or-expiry:invalid")

    conflict_rows = []
    if args.against:
        try:
            value = load_document(args.against)
            rows = value.get("workspace_claims", value.get("claims", []))
            if not isinstance(rows, list):
                errors.append("against:must-contain-list")
                rows = []
            for index, row in enumerate(rows):
                if not isinstance(row, dict):
                    errors.append(f"against[{index}]:must-be-object")
                    continue
                other = parse_claim(row, errors, f"against[{index}]")
                pairs = claims_conflict(claim, other)
                if pairs:
                    conflict_rows.append(
                        {
                            "other_claim_id": other.get("claim_id"),
                            "other_plan_id": other.get("plan_id"),
                            "resource_pairs": pairs,
                        }
                    )
        except Exception as exc:
            errors.append(f"against:{exc}")

    if conflict_rows:
        errors.append("claim:resource-conflict")

    return emit(
        "claim_gate",
        {
            "claim_id": claim.get("claim_id"),
            "plan_id": claim.get("plan_id"),
            "session_id": claim.get("session_id"),
            "fencing_token": claim.get("fencing_token"),
            "state": claim.get("state"),
            "conflicts": conflict_rows,
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
