#!/usr/bin/env python3
"""Validate review_batch / RB-v1 including RAP-v1 aperture rules."""

from __future__ import annotations

import argparse

from common import emit, list_field, load_document, object_field, require, unwrap, yes

MODES = {"discovery", "kernel_review", "conformance", "terminal_holdout"}
STATES = {"open", "sealed", "invalidated"}


def validate_aperture(row: object, index: int, mode: str, errors: list[str]) -> str | None:
    prefix = f"apertures[{index}]"
    if not isinstance(row, dict):
        errors.append(f"{prefix}:must-be-object")
        return None
    if row.get("aperture_version") != "RAP-v1":
        errors.append(f"{prefix}.aperture_version")
    aperture_id = row.get("aperture_id")
    if not aperture_id:
        errors.append(f"{prefix}.aperture_id")
    if row.get("review_mode") != mode:
        errors.append(f"{prefix}.review_mode:mismatch")
    target = object_field(row, "target", errors, f"{prefix}.")
    total_targets = 0
    for key in (
        "law_refs", "owner_refs", "operation_refs", "transition_refs",
        "proof_refs", "existing_class_refs",
    ):
        total_targets += len(list_field(target, key, errors, f"{prefix}.target."))
    list_field(row, "requested_counterexample_kinds", errors, f"{prefix}.")
    list_field(row, "excluded_scope", errors, f"{prefix}.")
    list_field(row, "overlap_with", errors, f"{prefix}.")
    list_field(row, "evidence_refs", errors, f"{prefix}.")
    if not row.get("risk"):
        errors.append(f"{prefix}.risk")
    whole = row.get("whole_diff_allowed")
    if whole not in {True, False, "yes", "no"}:
        errors.append(f"{prefix}.whole_diff_allowed")
    if mode == "conformance":
        if total_targets == 0:
            errors.append(f"{prefix}:conformance-target-empty")
        if whole in {True, "yes"}:
            errors.append(f"{prefix}:conformance-whole-diff-forbidden")
    if mode == "kernel_review" and total_targets == 0:
        errors.append(f"{prefix}:kernel-target-empty")
    gate = object_field(row, "gate", errors, f"{prefix}.")
    for key in ("target_nonempty", "conformance_is_targeted", "overlap_explained", "aperture_allowed"):
        if not yes(gate.get(key)):
            errors.append(f"{prefix}.gate.{key}")
    return aperture_id if isinstance(aperture_id, str) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        batch = unwrap(load_document(args.file), "review_batch")
    except Exception as exc:
        return emit("review_batch_gate", {}, [str(exc)], [])

    if batch.get("batch_version") != "RB-v1":
        errors.append("batch_version")
    for key in ("batch_id", "campaign_id"):
        require(batch, key, errors)
    mode = batch.get("review_mode")
    state = batch.get("state")
    if mode not in MODES:
        errors.append("review_mode")
    if state not in STATES:
        errors.append("state")

    artifact = object_field(batch, "artifact_state", errors)
    for key in ("base", "head", "dirty_fingerprint"):
        require(artifact, key, errors, "artifact_state.")

    contract = object_field(batch, "contract", errors)
    for key in ("contract_id", "contract_fingerprint", "horizon_fingerprint"):
        require(contract, key, errors, "contract.")

    apertures = list_field(batch, "apertures", errors)
    ids: set[str] = set()
    for index, row in enumerate(apertures):
        aid = validate_aperture(row, index, mode, errors)
        if aid:
            if aid in ids:
                errors.append(f"apertures:duplicate:{aid}")
            ids.add(aid)
    if not apertures:
        errors.append("apertures:empty")

    list_field(batch, "reviewer_receipts", errors)
    cex_refs = list_field(batch, "counterexample_refs", errors)
    if len(cex_refs) != len(set(cex_refs)):
        errors.append("counterexample_refs:duplicates")

    classification = object_field(batch, "classification", errors)
    numeric_fields = (
        "claims_total", "confirmed", "refuted_or_stale", "in_horizon",
        "outside_horizon", "contract_invalidating", "unknown",
        "new_classes", "existing_class_witnesses", "duplicates",
    )
    for key in numeric_fields:
        if not isinstance(classification.get(key), int) or classification.get(key, -1) < 0:
            errors.append(f"classification.{key}")
    if isinstance(classification.get("claims_total"), int):
        if classification.get("confirmed", 0) + classification.get("refuted_or_stale", 0) + classification.get("unknown", 0) != classification["claims_total"]:
            errors.append("classification:validity-counts-do-not-sum")
    if classification.get("confirmed", 0) != len(cex_refs):
        warnings.append("classification.confirmed:differs-from-counterexample-ref-count")

    mutations = list_field(batch, "mutation_events_while_open", errors)
    if mutations:
        errors.append("mutation_events_while_open:not-empty")

    gate = object_field(batch, "gate", errors)
    for key in (
        "apertures_complete", "receipts_terminal", "every_claim_classified",
        "no_unknown_intent_relation", "no_mutation_while_open",
        "counterexamples_valid", "batch_allowed_to_seal",
    ):
        if not yes(gate.get(key)):
            errors.append(f"gate.{key}")

    if state == "sealed":
        if classification.get("unknown") != 0:
            errors.append("sealed:unknown-claims")
        if not yes(gate.get("batch_allowed_to_seal")):
            errors.append("sealed:gate-not-allowed")
    elif state == "open" and yes(gate.get("batch_allowed_to_seal")):
        warnings.append("open:batch-gate-already-pass")
    elif state == "invalidated":
        warnings.append("batch:invalidated")

    return emit(
        "review_batch_gate",
        {
            "batch_id": batch.get("batch_id"),
            "review_mode": mode,
            "state": state,
            "apertures": len(ids),
            "counterexamples": len(cex_refs),
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
