#!/usr/bin/env python3
"""Validate PHI-v1 and derive strict monotone review progress."""

from __future__ import annotations

import argparse

from common import emit, load_document, object_field, require, unwrap, yes, no

PRIMARY = (
    "unclassified_in_horizon_counterexamples",
    "unsatisfied_laws",
    "open_counterexample_classes",
    "orphan_realization_constructs",
)
SURFACE = (
    "truth_owners",
    "public_symbols",
    "state_variants",
    "protocol_cases",
    "fallback_or_compatibility_paths",
    "control_flow_branches",
    "helpers_or_wrappers",
    "test_families",
)
PROOF = ("missing_law_proofs", "unmapped_proof_actions", "wound_specific_tests")


def nonnegative_ints(parent: dict, keys: tuple[str, ...], prefix: str, errors: list[str]) -> list[int]:
    result: list[int] = []
    for key in keys:
        value = parent.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"{prefix}.{key}")
            value = 0
        result.append(value)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        phi = unwrap(load_document(args.file), "review_potential")
    except Exception as exc:
        return emit("review_potential_gate", {}, [str(exc)], [])

    if phi.get("potential_version") != "PHI-v1":
        errors.append("potential_version")
    for key in (
        "potential_id", "campaign_id", "cycle_id", "contract_fingerprint",
        "kernel_fingerprint", "artifact_state_before", "artifact_state_after",
    ):
        require(phi, key, errors)

    before = object_field(phi, "before", errors)
    after = object_field(phi, "after", errors)
    primary_before = nonnegative_ints(before, PRIMARY, "before", errors)
    primary_after = nonnegative_ints(after, PRIMARY, "after", errors)

    surface_before_obj = object_field(before, "hard_semantic_surface", errors, "before.")
    surface_after_obj = object_field(after, "hard_semantic_surface", errors, "after.")
    surface_before = nonnegative_ints(surface_before_obj, SURFACE, "before.hard_semantic_surface", errors)
    surface_after = nonnegative_ints(surface_after_obj, SURFACE, "after.hard_semantic_surface", errors)

    proof_before_obj = object_field(before, "proof_debt", errors, "before.")
    proof_after_obj = object_field(after, "proof_debt", errors, "after.")
    proof_before = nonnegative_ints(proof_before_obj, PROOF, "before.proof_debt", errors)
    proof_after = nonnegative_ints(proof_after_obj, PROOF, "after.proof_debt", errors)

    comparison = object_field(phi, "comparison", errors)
    if comparison.get("primary_before") != primary_before:
        errors.append("comparison.primary_before:mismatch")
    if comparison.get("primary_after") != primary_after:
        errors.append("comparison.primary_after:mismatch")

    derived_primary = tuple(primary_after) < tuple(primary_before)
    derived_surface = all(a <= b for a, b in zip(surface_after, surface_before))
    derived_proof = sum(proof_after) <= sum(proof_before)
    rebase = comparison.get("contract_rebase_ref")

    if rebase:
        warnings.append("contract-rebase:old-potential-not-delivery-authority")
        if yes(comparison.get("strict_progress")):
            errors.append("contract-rebase:strict-progress-forbidden")
    else:
        if yes(comparison.get("primary_lexicographic_decrease")) != derived_primary:
            errors.append("comparison.primary_lexicographic_decrease:mismatch")
        if yes(comparison.get("hard_surface_componentwise_nonincreasing")) != derived_surface:
            errors.append("comparison.hard_surface_componentwise_nonincreasing:mismatch")
        if yes(comparison.get("proof_debt_nonincreasing")) != derived_proof:
            errors.append("comparison.proof_debt_nonincreasing:mismatch")
        derived_strict = derived_primary and derived_surface and derived_proof
        if yes(comparison.get("strict_progress")) != derived_strict:
            errors.append("comparison.strict_progress:mismatch")
        if not derived_strict:
            errors.append("strict-progress-gate:fail")

    evidence = phi.get("evidence_refs")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence_refs:empty")

    return emit(
        "review_potential_gate",
        {
            "potential_id": phi.get("potential_id"),
            "cycle_id": phi.get("cycle_id"),
            "primary_before": primary_before,
            "primary_after": primary_after,
            "hard_surface_nonincreasing": derived_surface,
            "proof_debt_nonincreasing": derived_proof,
            "strict_progress": (not rebase and derived_primary and derived_surface and derived_proof),
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
