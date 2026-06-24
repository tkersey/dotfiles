#!/usr/bin/env python3
"""Fail-closed gate for intent-closed MBKC-v1."""

from __future__ import annotations

import argparse

from common import emit, list_field, load_document, object_field, require, unwrap, yes

STAGES = {
    "acceptance_sealed",
    "discovery_sealed",
    "kernel_accepted",
    "realization_verified",
    "conformance_sealed",
    "potential_certified",
    "applied",
    "committed",
    "pushed",
    "tuple_closed",
    "terminal_closed",
}

STAGE_GATE = {
    "acceptance_sealed": "acceptance_allowed",
    "discovery_sealed": "basis_allowed",
    "kernel_accepted": "kernel_allowed",
    "realization_verified": "realization_allowed",
    "conformance_sealed": "conformance_allowed",
    "potential_certified": "apply_allowed",
    "applied": "commit_allowed",
    "committed": "push_allowed",
    "pushed": "tuple_closure_allowed",
    "tuple_closed": "tuple_closure_allowed",
    "terminal_closed": "terminal_closure_allowed",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--terminal", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        mbkc = unwrap(load_document(args.file), "minimum_behavioral_kernel_certificate")
    except Exception as exc:
        return emit("mbkc_gate", {}, [str(exc)], [])

    if mbkc.get("certificate_version") != "MBKC-v1":
        errors.append("certificate_version")
    if mbkc.get("protocol_profile") != "intent-closed-cegis-v1":
        errors.append("protocol_profile")
    for key in ("certificate_id", "stage"):
        require(mbkc, key, errors)
    stage = mbkc.get("stage")
    if stage not in STAGES:
        errors.append("stage")

    campaign = object_field(mbkc, "campaign", errors)
    for key in (
        "campaign_id", "pr_number", "campaign_base_sha",
        "review_ready_baseline_sha", "current_delivery_head",
    ):
        require(campaign, key, errors, "campaign.")

    acceptance = object_field(mbkc, "acceptance", errors)
    if acceptance.get("contract_version") != "AC-v2":
        errors.append("acceptance.contract_version")
    for key in ("contract_id", "contract_fingerprint", "horizon_fingerprint"):
        require(acceptance, key, errors, "acceptance.")
    if acceptance.get("horizon_state") not in {"sealed", "rebased"}:
        errors.append("acceptance.horizon_state")
    if not yes(acceptance.get("gate_passed")):
        errors.append("acceptance.gate_passed")

    batches = object_field(mbkc, "review_batches", errors)
    discovery = object_field(batches, "discovery", errors, "review_batches.")
    if stage != "acceptance_sealed" and discovery.get("state") != "sealed":
        errors.append("review_batches.discovery:not-sealed")
    if stage not in {"acceptance_sealed", "discovery_sealed", "kernel_accepted"}:
        conformance = object_field(batches, "conformance", errors, "review_batches.")
        if conformance.get("state") != "sealed":
            errors.append("review_batches.conformance:not-sealed")
    else:
        conformance = batches.get("conformance", {})
    holdout = batches.get("terminal_holdout", {})
    open_batches = list_field(batches, "open_batch_ids", errors, "review_batches.")
    if open_batches:
        errors.append("review_batches.open_batch_ids:not-empty")

    basis = object_field(mbkc, "counterexample_basis", errors)
    if stage != "acceptance_sealed":
        if basis.get("basis_version") != "CEB-v2":
            errors.append("counterexample_basis.basis_version")
        for key in ("basis_id", "basis_fingerprint"):
            require(basis, key, errors, "counterexample_basis.")
        if not yes(basis.get("gate_passed")):
            errors.append("counterexample_basis.gate_passed")
        if basis.get("unknown_count", 0) != 0:
            errors.append("counterexample_basis.unknown_count")

    kernel = object_field(mbkc, "kernel", errors)
    if stage not in {"acceptance_sealed", "discovery_sealed"}:
        if kernel.get("kernel_version") != "MBK-v1":
            errors.append("kernel.kernel_version")
        require(kernel, "kernel_fingerprint", errors, "kernel.")
        if not yes(kernel.get("gate_passed")):
            errors.append("kernel.gate_passed")

    rc = object_field(mbkc, "reduction_certificate", errors)
    if stage not in {"acceptance_sealed", "discovery_sealed"}:
        if rc.get("certificate_version") != "RC-v1":
            errors.append("reduction_certificate.certificate_version")
        if not yes(rc.get("gate_passed")):
            errors.append("reduction_certificate.gate_passed")

    realization = object_field(mbkc, "realization", errors)
    if stage in {
        "realization_verified", "conformance_sealed", "potential_certified",
        "applied", "committed", "pushed", "tuple_closed", "terminal_closed",
    }:
        for key in ("selected_design_id", "manifest_ref", "construct_map_ref", "surface_ref"):
            require(realization, key, errors, "realization.")
        if not yes(realization.get("verified")):
            errors.append("realization.verified")
        if realization.get("new_observations"):
            errors.append("realization.new_observations")

    potential = object_field(mbkc, "review_potential", errors)
    if stage in {
        "potential_certified", "applied", "committed", "pushed",
        "tuple_closed", "terminal_closed",
    }:
        if potential.get("potential_version") != "PHI-v1":
            errors.append("review_potential.potential_version")
        require(potential, "potential_id", errors, "review_potential.")
        if not yes(potential.get("strict_progress")):
            errors.append("review_potential.strict_progress")

    conformance_result = object_field(mbkc, "conformance", errors)
    if stage in {
        "conformance_sealed", "potential_certified", "applied", "committed",
        "pushed", "tuple_closed", "terminal_closed",
    }:
        if conformance_result.get("novel_in_horizon_counterexamples", 0) != 0:
            errors.append("conformance.novel_in_horizon_counterexamples")
        if conformance_result.get("unknown_counterexamples", 0) != 0:
            errors.append("conformance.unknown_counterexamples")
        if conformance_result.get("same_class_recurrences", 0) != 0:
            errors.append("conformance.same_class_recurrences")
        if not yes(conformance_result.get("gate_passed")):
            errors.append("conformance.gate_passed")

    semantic = object_field(mbkc, "semantic_surface", errors)
    for key in ("hard_dimensions_nonincreasing", "total_description_nonincreasing"):
        if not yes(semantic.get(key)):
            errors.append(f"semantic_surface.{key}")

    proof = object_field(mbkc, "proof_basis", errors)
    if proof.get("wound_specific_tests"):
        errors.append("proof_basis.wound_specific_tests")
    if proof.get("unmapped_proof_actions"):
        errors.append("proof_basis.unmapped_proof_actions")
    if stage in {"tuple_closed", "terminal_closed"} and not yes(proof.get("all_laws_covered")):
        errors.append("proof_basis.all_laws_covered")

    delivery = object_field(mbkc, "delivery", errors)
    if stage in {"committed", "pushed", "tuple_closed", "terminal_closed"}:
        require(delivery, "commit_sha", errors, "delivery.")
    if stage in {"pushed", "tuple_closed", "terminal_closed"}:
        require(delivery, "pushed_head", errors, "delivery.")
    if stage in {"tuple_closed", "terminal_closed"}:
        require(delivery, "pr_sweep_ref", errors, "delivery.")
        if not yes(delivery.get("current_head_validation_passed")):
            errors.append("delivery.current_head_validation_passed")

    horizon = object_field(mbkc, "closure_horizon", errors)
    if stage in {"tuple_closed", "terminal_closed"}:
        for key in ("review_backend", "review_receipt", "closure_kind"):
            require(horizon, key, errors, "closure_horizon.")
        reopen = list_field(horizon, "reopen_conditions", errors, "closure_horizon.")
        if not reopen:
            errors.append("closure_horizon.reopen_conditions:empty")

    terminal_required = args.terminal or stage == "terminal_closed"
    if terminal_required:
        if stage != "terminal_closed":
            errors.append("stage:not-terminal_closed")
        if not isinstance(holdout, dict) or holdout.get("state") != "sealed":
            errors.append("review_batches.terminal_holdout:not-sealed")
        holdout_result = object_field(mbkc, "terminal_holdout", errors)
        if holdout_result.get("novel_in_horizon_counterexamples", 0) != 0:
            errors.append("terminal_holdout.novel_in_horizon_counterexamples")
        if holdout_result.get("contract_invalidating_unresolved", 0) != 0:
            errors.append("terminal_holdout.contract_invalidating_unresolved")
        if holdout_result.get("unknown_counterexamples", 0) != 0:
            errors.append("terminal_holdout.unknown_counterexamples")
        if holdout_result.get("verdict") != "clean":
            errors.append("terminal_holdout.verdict")

    gate = object_field(mbkc, "gate", errors)
    required_gate = STAGE_GATE.get(stage)
    if required_gate and not yes(gate.get(required_gate)):
        errors.append(f"gate.{required_gate}")
    if terminal_required:
        for key in (
            "acceptance_current", "no_open_review_batch", "basis_current",
            "kernel_current", "reduction_current", "realization_current",
            "strict_progress", "conformance_clean", "holdout_clean",
            "no_orphan_code_or_proof", "proof_current", "delivery_current",
            "terminal_closure_allowed",
        ):
            if not yes(gate.get(key)):
                errors.append(f"gate.{key}")

    return emit(
        "mbkc_gate",
        {
            "certificate_id": mbkc.get("certificate_id"),
            "stage": stage,
            "campaign_id": campaign.get("campaign_id"),
            "contract_id": acceptance.get("contract_id"),
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
