#!/usr/bin/env python3
"""Validate counterexample / CEX-v1 and its deterministic disposition."""

from __future__ import annotations

import argparse

from common import emit, list_field, load_document, object_field, require, unwrap, no

VALIDITY = {"confirmed", "refuted", "stale", "unknown"}
LIABILITY = {
    "introduced_by_current_diff",
    "exposed_and_required_by_current_acceptance",
    "preexisting_but_blocks_current_invariant",
    "adjacent_preexisting",
    "reviewer_preference",
    "unknown",
}
RELATION = {
    "directly_entailed",
    "compatibility_required",
    "forbidden_state_witness",
    "contract_invalidating",
    "outside_horizon",
    "unrelated",
    "unknown",
}
SCOPE = {"none", "narrows", "expands", "invalidates_contract"}
NOVELTY = {
    "new_equivalence_class",
    "new_witness_existing_class",
    "duplicate",
    "refuted",
    "stale",
    "unknown",
}
IMPACT = {
    "existing_law_violation",
    "additional_witness",
    "missing_semantic_distinction",
    "missing_proof",
    "orphan_realization",
    "stale_artifact_state",
    "no_kernel_impact",
    "unknown",
}
DISPOSITION = {
    "enter_kernel",
    "attach_witness",
    "invalidate_realization",
    "return_to_contract",
    "capture_followup",
    "reject",
    "blocked",
}


def expected_disposition(cex: dict) -> set[str]:
    validity = cex.get("validity")
    liability = cex.get("liability")
    intent = cex.get("intent", {})
    relation = intent.get("relation")
    scope = intent.get("scope_effect")
    novelty = cex.get("novelty")
    impact = cex.get("kernel_impact")

    if validity in {"refuted", "stale"}:
        return {"reject"}
    if validity == "unknown" or liability == "unknown" or relation == "unknown" or novelty == "unknown" or impact == "unknown":
        return {"blocked"}
    if liability == "reviewer_preference" or relation == "unrelated":
        return {"reject"}
    if relation == "outside_horizon":
        return {"capture_followup"}
    if relation == "contract_invalidating" or scope in {"expands", "invalidates_contract"}:
        return {"return_to_contract"}
    if novelty == "new_equivalence_class" or impact == "missing_semantic_distinction":
        return {"enter_kernel"}
    if impact in {"existing_law_violation", "orphan_realization"}:
        return {"invalidate_realization"}
    if novelty == "new_witness_existing_class" or impact in {"additional_witness", "missing_proof"}:
        return {"attach_witness"}
    if novelty == "duplicate" or impact in {"stale_artifact_state", "no_kernel_impact"}:
        return {"reject", "attach_witness"}
    return {"blocked"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        cex = unwrap(load_document(args.file), "counterexample")
    except Exception as exc:
        return emit("counterexample_gate", {}, [str(exc)], [])

    if cex.get("counterexample_version") != "CEX-v1":
        errors.append("counterexample_version")
    for key in ("counterexample_id", "campaign_id", "batch_id", "review_mode"):
        require(cex, key, errors)
    if cex.get("review_mode") not in {"discovery", "kernel_review", "conformance", "terminal_holdout"}:
        errors.append("review_mode")

    artifact = object_field(cex, "artifact_state", errors)
    for key in ("base", "head", "review_receipt"):
        require(artifact, key, errors, "artifact_state.")

    claim = object_field(cex, "claim", errors)
    require(claim, "statement", errors, "claim.")
    list_field(claim, "source_refs", errors, "claim.")

    observation = object_field(cex, "observation", errors)
    for key in ("actor", "operation", "pre_state", "expected", "actual", "externally_visible_difference", "reproduction_or_proof"):
        require(observation, key, errors, "observation.")
    trace = list_field(observation, "minimal_trace", errors, "observation.")
    if not trace:
        errors.append("observation.minimal_trace:empty")

    if cex.get("validity") not in VALIDITY:
        errors.append("validity")
    if cex.get("liability") not in LIABILITY:
        errors.append("liability")

    intent = object_field(cex, "intent", errors)
    for key in ("contract_id", "contract_fingerprint", "horizon_fingerprint", "witness"):
        require(intent, key, errors, "intent.")
    ref_fields = ("acceptance_refs", "compatibility_refs", "forbidden_refs", "non_goal_refs", "kernel_law_refs")
    refs = {key: list_field(intent, key, errors, "intent.") for key in ref_fields}
    relation = intent.get("relation")
    scope = intent.get("scope_effect")
    if relation not in RELATION:
        errors.append("intent.relation")
    if scope not in SCOPE:
        errors.append("intent.scope_effect")
    if relation == "directly_entailed" and not refs["acceptance_refs"]:
        errors.append("intent.directly_entailed:acceptance-ref-required")
    if relation == "compatibility_required" and not refs["compatibility_refs"]:
        errors.append("intent.compatibility_required:compatibility-ref-required")
    if relation == "forbidden_state_witness" and not refs["forbidden_refs"]:
        errors.append("intent.forbidden_state_witness:forbidden-ref-required")
    if relation == "outside_horizon" and not (refs["non_goal_refs"] or intent.get("witness")):
        errors.append("intent.outside_horizon:witness-required")
    if relation in {"directly_entailed", "compatibility_required", "forbidden_state_witness"} and scope in {"expands", "invalidates_contract"}:
        errors.append("intent:entailed-relation-cannot-expand")

    novelty = cex.get("novelty")
    if novelty not in NOVELTY:
        errors.append("novelty")
    existing = cex.get("existing_class_ref")
    if novelty in {"new_witness_existing_class", "duplicate"} and not existing:
        errors.append("existing_class_ref:required")
    if novelty == "new_equivalence_class" and existing:
        errors.append("existing_class_ref:forbidden-for-new-class")

    if cex.get("kernel_impact") not in IMPACT:
        errors.append("kernel_impact")
    disposition = cex.get("disposition")
    if disposition not in DISPOSITION:
        errors.append("disposition")

    expected = expected_disposition(cex)
    if disposition not in expected:
        errors.append(f"disposition:{disposition}:expected-one-of:{','.join(sorted(expected))}")

    authority = object_field(cex, "mutation_authority", errors)
    if not no(authority.get("allowed")):
        errors.append("mutation_authority.allowed:must-be-no")
    require(authority, "reason", errors, "mutation_authority.")

    if cex.get("review_mode") == "conformance" and not cex.get("aperture_id"):
        errors.append("conformance:aperture_id-required")
    if cex.get("validity") == "confirmed" and cex.get("novelty") in {"refuted", "stale"}:
        errors.append("confirmed:novelty-contradiction")

    return emit(
        "counterexample_gate",
        {
            "counterexample_id": cex.get("counterexample_id"),
            "review_mode": cex.get("review_mode"),
            "validity": cex.get("validity"),
            "intent_relation": relation,
            "novelty": novelty,
            "disposition": disposition,
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
