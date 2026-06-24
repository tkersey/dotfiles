#!/usr/bin/env python3
"""Validate counterexample_basis / CEB-v2."""

from __future__ import annotations

import argparse

from common import emit, list_field, load_document, object_field, require, unique_ids, unwrap, yes

STATUS = {"open", "satisfied", "invalidated"}
NOVELTY = {"new", "existing"}
METHODS = {
    "exact_partition_refinement",
    "exact_bisimulation",
    "witness_checked_manual",
    "not_applicable",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        basis = unwrap(load_document(args.file), "counterexample_basis")
    except Exception as exc:
        return emit("counterexample_basis_gate", {}, [str(exc)], [])

    if basis.get("basis_version") != "CEB-v2":
        errors.append("basis_version")
    for key in (
        "basis_id", "campaign_id", "contract_id", "contract_fingerprint",
        "horizon_fingerprint",
    ):
        require(basis, key, errors)
    batches = list_field(basis, "batch_ids", errors)
    if not batches:
        errors.append("batch_ids:empty")
    object_field(basis, "artifact_state", errors)

    accepted = list_field(basis, "accepted_counterexamples", errors)
    if not accepted:
        errors.append("accepted_counterexamples:empty")
    if len(accepted) != len(set(accepted)):
        errors.append("accepted_counterexamples:duplicates")

    excluded = list_field(basis, "excluded_counterexamples", errors)
    for index, row in enumerate(excluded):
        if not isinstance(row, dict) or not row.get("counterexample_id") or not row.get("disposition") or not row.get("reason"):
            errors.append(f"excluded_counterexamples[{index}]")

    classes = list_field(basis, "equivalence_classes", errors)
    class_ids = unique_ids(classes, "class_id", errors, "equivalence_classes")
    members_seen: set[str] = set()
    for index, row in enumerate(classes):
        if not isinstance(row, dict):
            continue
        prefix = f"equivalence_classes[{index}]"
        laws = list_field(row, "governing_law_refs", errors, f"{prefix}.")
        anchors = list_field(row, "acceptance_refs", errors, f"{prefix}.")
        members = list_field(row, "member_counterexamples", errors, f"{prefix}.")
        for key in ("representative_counterexample", "minimal_observation", "canonical_owner", "proof_obligation"):
            require(row, key, errors, f"{prefix}.")
        if not laws or not anchors or not members:
            errors.append(f"{prefix}:law-anchor-members-required")
        representative = row.get("representative_counterexample")
        if representative not in members:
            errors.append(f"{prefix}:representative-not-member")
        for member in members:
            if member not in accepted:
                errors.append(f"{prefix}:unknown-accepted-member:{member}")
            if member in members_seen:
                errors.append(f"counterexample:member-in-multiple-classes:{member}")
            members_seen.add(member)
        if row.get("novelty") not in NOVELTY:
            errors.append(f"{prefix}.novelty")
        if row.get("status") not in STATUS:
            errors.append(f"{prefix}.status")
    missing = set(accepted) - members_seen
    for cex in sorted(missing):
        errors.append(f"accepted-counterexample-unclassified:{cex}")

    quotient = object_field(basis, "quotient", errors)
    require(quotient, "relation", errors, "quotient.")
    if quotient.get("method") not in METHODS:
        errors.append("quotient.method")
    list_field(quotient, "merged_counterexample_ids", errors, "quotient.")
    retained = list_field(quotient, "retained_class_ids", errors, "quotient.")
    for cid in retained:
        if cid not in class_ids:
            errors.append(f"quotient.retained_class_ids:unknown:{cid}")
    list_field(quotient, "congruence_witnesses", errors, "quotient.")
    unresolved = list_field(quotient, "unresolved", errors, "quotient.")

    gate = object_field(basis, "gate", errors)
    for key in (
        "every_claim_classified", "every_accepted_cex_in_horizon",
        "every_cex_has_intent_anchor", "duplicates_quotiented",
        "no_unknown_novelty", "batch_sealed", "basis_allowed",
    ):
        if not yes(gate.get(key)):
            errors.append(f"gate.{key}")
    if unresolved and yes(gate.get("basis_allowed")):
        errors.append("quotient.unresolved:basis-cannot-be-allowed")

    return emit(
        "counterexample_basis_gate",
        {
            "basis_id": basis.get("basis_id"),
            "accepted_counterexamples": len(accepted),
            "classes": len(class_ids),
            "excluded_counterexamples": len(excluded),
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
