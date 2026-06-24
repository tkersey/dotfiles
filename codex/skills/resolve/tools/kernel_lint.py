#!/usr/bin/env python3
"""Intent and relation lint for minimum_behavioral_kernel / MBK-v1."""

from __future__ import annotations

import argparse

from common import emit, list_field, load_document, object_field, require, unique_ids, unwrap, yes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        kernel = unwrap(load_document(args.file), "minimum_behavioral_kernel")
    except Exception as exc:
        return emit("kernel_lint", {}, [str(exc)], [])

    if kernel.get("kernel_version") != "MBK-v1":
        errors.append("kernel_version")
    for key in ("campaign_id", "campaign_base_sha", "kernel_fingerprint"):
        require(kernel, key, errors)

    ac = object_field(kernel, "acceptance_contract_ref", errors)
    for key in ("contract_id", "contract_fingerprint", "horizon_fingerprint"):
        require(ac, key, errors, "acceptance_contract_ref.")
    basis = object_field(kernel, "counterexample_basis_ref", errors)
    for key in ("basis_id", "basis_fingerprint"):
        require(basis, key, errors, "counterexample_basis_ref.")

    authorities = list_field(kernel, "authorities", errors)
    carriers = list_field(kernel, "carriers", errors)
    observations = list_field(kernel, "observations", errors)
    classes = list_field(kernel, "equivalence_classes", errors)
    operations = list_field(kernel, "operations", errors)
    transitions = list_field(kernel, "transitions", errors)
    laws = list_field(kernel, "laws", errors)
    families = list_field(kernel, "counterexample_families", errors)
    list_field(kernel, "non_laws", errors)
    list_field(kernel, "forbidden_states_or_transitions", errors)
    list_field(kernel, "non_goals_preserved", errors)

    authority_ids = unique_ids(authorities, "authority_id", errors, "authorities")
    carrier_ids = unique_ids(carriers, "carrier_id", errors, "carriers")
    observation_ids = unique_ids(observations, "observation_id", errors, "observations")
    class_ids = unique_ids(classes, "class_id", errors, "equivalence_classes")
    operation_ids = unique_ids(operations, "operation_id", errors, "operations")
    transition_ids = unique_ids(transitions, "transition_id", errors, "transitions")
    law_ids = unique_ids(laws, "law_id", errors, "laws")
    family_ids = unique_ids(families, "family_id", errors, "counterexample_families")

    if not authority_ids:
        errors.append("authorities:empty")
    if not observations:
        errors.append("observations:empty")
    if not laws:
        errors.append("laws:empty")

    for index, row in enumerate(observations):
        if not isinstance(row, dict):
            continue
        prefix = f"observations[{index}]"
        cex = list_field(row, "counterexample_refs", errors, f"{prefix}.")
        anchors = []
        for key in ("acceptance_refs", "compatibility_refs", "forbidden_refs"):
            anchors += list_field(row, key, errors, f"{prefix}.")
        for key in ("observes", "expected", "proof_ref"):
            require(row, key, errors, f"{prefix}.")
        if not cex and not anchors:
            errors.append(f"{prefix}:unanchored")
        if not anchors:
            errors.append(f"{prefix}:intent-anchor-required")

    for index, row in enumerate(operations):
        if not isinstance(row, dict):
            continue
        owner = row.get("authority_id")
        if owner not in authority_ids:
            errors.append(f"operations[{index}]:unknown-authority:{owner}")
        inputs = list_field(row, "inputs", errors, f"operations[{index}].")
        outputs = list_field(row, "outputs", errors, f"operations[{index}].")
        for carrier in inputs + outputs:
            if carrier not in carrier_ids:
                errors.append(f"operations[{index}]:unknown-carrier:{carrier}")

    for index, row in enumerate(transitions):
        if not isinstance(row, dict):
            continue
        operation = row.get("operation_id")
        if operation not in operation_ids:
            errors.append(f"transitions[{index}]:unknown-operation:{operation}")
        for key in ("from_classes", "to_classes"):
            values = list_field(row, key, errors, f"transitions[{index}].")
            for value in values:
                if value not in class_ids:
                    errors.append(f"transitions[{index}].{key}:unknown:{value}")
        for obs in list_field(row, "emitted_observations", errors, f"transitions[{index}]."):
            if obs not in observation_ids:
                errors.append(f"transitions[{index}]:unknown-observation:{obs}")

    for index, row in enumerate(classes):
        if not isinstance(row, dict):
            continue
        for obs in list_field(row, "preserved_observations", errors, f"equivalence_classes[{index}]."):
            if obs not in observation_ids:
                errors.append(f"equivalence_classes[{index}]:unknown-observation:{obs}")
        distinctions = list_field(row, "distinguished_from", errors, f"equivalence_classes[{index}].")
        for distinction in distinctions:
            if not isinstance(distinction, dict):
                errors.append(f"equivalence_classes[{index}]:invalid-distinction")
                continue
            other = distinction.get("class_id")
            if other not in class_ids:
                errors.append(f"equivalence_classes[{index}]:unknown-class:{other}")
            witnesses = distinction.get("witness_observation_ids")
            if not isinstance(witnesses, list) or not witnesses:
                errors.append(f"equivalence_classes[{index}]:distinction-without-witness:{other}")
            else:
                for witness in witnesses:
                    if witness not in observation_ids:
                        errors.append(f"equivalence_classes[{index}]:unknown-witness:{witness}")

    for index, row in enumerate(laws):
        if not isinstance(row, dict):
            continue
        prefix = f"laws[{index}]"
        owner = row.get("owner")
        if owner not in authority_ids:
            errors.append(f"{prefix}:unknown-owner:{owner}")
        refs = []
        for key in ("acceptance_refs", "compatibility_refs", "forbidden_refs"):
            refs += list_field(row, key, errors, f"{prefix}.")
        if not refs:
            errors.append(f"{prefix}:intent-anchor-required")
        observations_for_law = list_field(row, "observation_ids", errors, f"{prefix}.")
        if not observations_for_law:
            errors.append(f"{prefix}:observation_ids-empty")
        for obs in observations_for_law:
            if obs not in observation_ids:
                errors.append(f"{prefix}:unknown-observation:{obs}")
        class_refs = list_field(row, "counterexample_class_refs", errors, f"{prefix}.")
        if not class_refs:
            errors.append(f"{prefix}:counterexample-class-required")
        proof = list_field(row, "proof_obligations", errors, f"{prefix}.")
        if not proof:
            errors.append(f"{prefix}:proof-obligations-empty")

    for index, row in enumerate(families):
        if not isinstance(row, dict):
            continue
        prefix = f"counterexample_families[{index}]"
        governing = list_field(row, "governing_law_ids", errors, f"{prefix}.")
        for law in governing:
            if law not in law_ids:
                errors.append(f"{prefix}:unknown-law:{law}")
        classes_for_family = list_field(row, "class_refs", errors, f"{prefix}.")
        if not classes_for_family:
            errors.append(f"{prefix}:class-refs-empty")
        list_field(row, "local_surfaces", errors, f"{prefix}.")

    quotient = object_field(kernel, "quotient", errors)
    if quotient.get("method") not in {
        "exact_partition_refinement", "exact_bisimulation",
        "witness_checked_manual", "not_applicable",
    }:
        errors.append("quotient.method")
    unresolved = list_field(quotient, "unresolved_distinctions", errors, "quotient.")
    congruence = list_field(quotient, "congruence_witnesses", errors, "quotient.")
    if unresolved:
        errors.append("quotient.unresolved_distinctions:not-empty")
    if quotient.get("method") != "not_applicable" and not congruence:
        errors.append("quotient.congruence_witnesses:empty")

    gate = object_field(kernel, "gate", errors)
    for key in (
        "all_branch_liabilities_covered",
        "every_observation_intent_anchored",
        "every_distinction_has_witness",
        "every_family_maps_to_law",
        "quotient_is_congruent",
        "non_goals_preserved",
        "recomposition_proved",
        "kernel_review_allowed",
    ):
        if not yes(gate.get(key)):
            errors.append(f"gate.{key}")

    return emit(
        "kernel_lint",
        {
            "campaign_id": kernel.get("campaign_id"),
            "kernel_fingerprint": kernel.get("kernel_fingerprint"),
            "counts": {
                "authorities": len(authority_ids),
                "carriers": len(carrier_ids),
                "observations": len(observation_ids),
                "classes": len(class_ids),
                "operations": len(operation_ids),
                "transitions": len(transition_ids),
                "laws": len(law_ids),
                "families": len(family_ids),
            },
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
