#!/usr/bin/env -S uv run --with pyyaml python
"""Generate a CBDD-v1 identity-level delta between two valid CBD-v2 artifacts."""

from __future__ import annotations

import argparse
from typing import Any

from common import deterministic_id, dump_data, load_data, sha256_digest, unwrap

SECTIONS = {
    "claims": "claim_id",
    "governing_laws": "law_id",
    "owned_invariants": "invariant_id",
    "boundary_rules": "boundary_rule_id",
    "failure_families": "family_id",
    "negative_routes": "route_id",
    "knowledge_routes": "knowledge_id",
    "focused_skill_candidates": "candidate_id",
}


def indexed(body: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for section, key in SECTIONS.items():
        for row in body.get(section, []):
            if isinstance(row, dict) and row.get(key):
                out[f"{section}:{row[key]}"] = row
    root = body.get("repository_root_skill")
    if isinstance(root, dict) and root.get("candidate_id"):
        out[f"repository_root_skill:{root['candidate_id']}"] = root
    for row in body.get("authority_map", {}).get("authorities", []):
        if isinstance(row, dict) and row.get("authority_id"):
            out[f"authority_map:{row['authority_id']}"] = row
    for row in body.get("proof_map", {}).get("proof_surfaces", []):
        if isinstance(row, dict) and row.get("proof_surface_id"):
            out[f"proof_map:{row['proof_surface_id']}"] = row
    return out


def compile_delta(
    prior_value: dict[str, Any],
    new_value: dict[str, Any],
    changed_paths: list[str],
) -> dict[str, Any]:
    prior = unwrap(prior_value, "codebase_doctrine")
    new = unwrap(new_value, "codebase_doctrine")
    old_index = indexed(prior)
    new_index = indexed(new)
    old_ids = set(old_index)
    new_ids = set(new_index)
    retained: list[str] = []
    modified: list[str] = []
    for item_id in sorted(old_ids & new_ids):
        if sha256_digest(old_index[item_id]) == sha256_digest(new_index[item_id]):
            retained.append(item_id)
        else:
            modified.append(item_id)
    invalidated = sorted(old_ids - new_ids)
    added = sorted(new_ids - old_ids)

    old_intent = unwrap(prior.get("intent", {}), "codebase_doctrine_intent")
    new_intent = unwrap(new.get("intent", {}), "codebase_doctrine_intent")
    drift = old_intent.get("intent_id") != new_intent.get("intent_id")
    proof_rechecks = [
        item_id
        for item_id in modified + added
        if item_id.startswith("proof_map:")
        or item_id.startswith("governing_laws:")
        or item_id.startswith("owned_invariants:")
    ]
    material = {
        "prior_doctrine_id": prior.get("doctrine_id"),
        "new_doctrine_id": new.get("doctrine_id"),
        "prior_artifact_state_id": prior.get("artifact_state", {}).get("artifact_state_id"),
        "new_artifact_state_id": new.get("artifact_state", {}).get("artifact_state_id"),
        "invalidated_ids": invalidated,
        "retained_ids": retained,
        "added_ids": added,
        "modified_ids": modified,
    }
    body = {
        "delta_version": "CBDD-v1",
        "delta_id": deterministic_id("CBDD", material),
        "prior_doctrine_id": prior.get("doctrine_id"),
        "prior_artifact_state_id": prior.get("artifact_state", {}).get("artifact_state_id"),
        "new_artifact_state_id": new.get("artifact_state", {}).get("artifact_state_id"),
        "changed_paths": changed_paths,
        "invalidated_ids": invalidated,
        "retained_ids": retained,
        "added_ids": added,
        "modified_ids": modified,
        "proof_rechecks": proof_rechecks,
        "intent_drift": {
            "detected": "yes" if drift else "no",
            "resolution": (
                "User resolution or an explicitly accepted new CDI-v2 is required."
                if drift
                else "No intent drift detected."
            ),
        },
        "resulting_doctrine_id": new.get("doctrine_id"),
    }
    return {"codebase_doctrine_delta": body}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prior")
    parser.add_argument("new")
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--format", choices=("yaml", "json"), default="yaml")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        delta = compile_delta(
            load_data(args.prior),
            load_data(args.new),
            list(args.changed_path),
        )
        rendered = dump_data(delta, args.format)
        if args.output:
            from pathlib import Path

            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except Exception as exc:
        print(dump_data({"doctrine_diff": {"verdict": "fail", "error": str(exc)}}, "json"), end="")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
