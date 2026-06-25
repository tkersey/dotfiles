#!/usr/bin/env python3
"""Validate ETR-v1 against EPG-v1, EPS-v1, and EPD-v1."""

from __future__ import annotations

import argparse
from typing import Any

from common import (
    apply_potential_delta,
    canonical_digest,
    compare_potential,
    emit,
    load_epg,
    load_wrapped,
)
from execution_policy_gate import validate_policy
from policy_select import validate_state

RESULTS = {
    "success",
    "failure",
    "return_to_policy",
    "return_to_spec",
    "rollback",
    "blocked",
}
SURPRISE = {
    "none",
    "expected_variance",
    "new_branch",
    "model_failure",
    "intent_failure",
}
PROOF_STATUS = {"pass", "fail", "blocked", "missing", "stale"}
PROOF_REQUIRED_ACTIONS = {"mutate", "stabilize", "deploy", "rollback", "prove"}


def _as_set(value: Any, path: str, errors: list[str]) -> set[str]:
    if not isinstance(value, list):
        errors.append(f"{path}:must-be-list")
        return set()
    result = {str(item) for item in value}
    if len(result) != len(value):
        errors.append(f"{path}:duplicates")
    return result


def _dimensions(epg: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    rows = epg.get("potential", {}).get("dimensions", [])
    dimensions = {
        str(row.get("dimension_id")): row
        for row in rows
        if isinstance(row, dict) and row.get("dimension_id")
    }
    order = [str(item) for item in epg.get("potential", {}).get("lexicographic_order", [])]
    return dimensions, order


def validate_transition(
    epg: dict[str, Any],
    state: dict[str, Any],
    decision: dict[str, Any],
    receipt: dict[str, Any],
    *,
    policy_digest: str | None = None,
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    digest = policy_digest or canonical_digest(epg)

    actions = {
        str(row.get("action_id")): row
        for row in epg.get("actions", [])
        if isinstance(row, dict) and row.get("action_id")
    }
    observations = {
        str(row.get("observation_id")): row
        for row in epg.get("observations", [])
        if isinstance(row, dict) and row.get("observation_id")
    }
    facts = {
        str(row.get("fact_id"))
        for row in epg.get("belief", {}).get("facts", [])
        if isinstance(row, dict) and row.get("fact_id")
    }
    unknowns = {
        str(row.get("unknown_id"))
        for row in epg.get("belief", {}).get("unknowns", [])
        if isinstance(row, dict) and row.get("unknown_id")
    }
    obligations = {
        str(row.get("obligation_id"))
        for row in epg.get("goal", {}).get("obligations", [])
        if isinstance(row, dict) and row.get("obligation_id")
    }
    dimensions, potential_order = _dimensions(epg)

    if decision.get("decision_version") != "EPD-v1":
        errors.append("decision.decision_version")
    expected_identity = {
        "policy_id": epg.get("policy_id"),
        "policy_revision": epg.get("revision"),
        "policy_digest": digest,
        "state_id": state.get("state_id"),
        "state_digest": state.get("state_digest"),
    }
    for key, expected in expected_identity.items():
        if decision.get(key) != expected:
            errors.append(f"decision.{key}:mismatch")
    if decision.get("terminal") not in (None, ""):
        errors.append("decision.terminal:receipt-requires-action")
    if decision.get("mutation_authority") != "no":
        errors.append("decision.mutation_authority:must-be-no")

    action_id = decision.get("selected_action_id")
    action = actions.get(str(action_id)) if action_id else None
    if not action:
        errors.append("decision.selected_action_id:unknown-or-empty")

    if receipt.get("receipt_version") != "ETR-v1":
        errors.append("receipt_version")
    receipt_identity = {
        "policy_id": epg.get("policy_id"),
        "policy_revision": epg.get("revision"),
        "policy_digest": digest,
        "action_id": action_id,
        "decision_ref": decision.get("decision_id"),
    }
    for key, expected in receipt_identity.items():
        if receipt.get(key) != expected:
            errors.append(f"{key}:mismatch")
    if not receipt.get("transition_id"):
        errors.append("transition_id")

    before = receipt.get("state_before")
    if not isinstance(before, dict):
        errors.append("state_before:must-be-object")
        before = {}
    if before.get("state_id") != state.get("state_id"):
        errors.append("state_before.state_id:mismatch")
    if before.get("state_digest") != state.get("state_digest"):
        errors.append("state_before.state_digest:mismatch")
    if before.get("potential") != state.get("current_potential"):
        errors.append("state_before.potential:mismatch")

    artifact_before = receipt.get("artifact_state_before")
    if not isinstance(artifact_before, dict) or not artifact_before:
        errors.append("artifact_state_before:must-be-nonempty-object")
    elif artifact_before != state.get("artifact_state"):
        errors.append("artifact_state_before:mismatch")
    artifact_after = receipt.get("artifact_state_after")
    if not isinstance(artifact_after, dict) or not artifact_after:
        errors.append("artifact_state_after:must-be-nonempty-object")

    expected_effects = action.get("expected_effects", {}) if action else {}
    decision_effects = decision.get("expected_effects")
    if action and decision_effects != expected_effects:
        errors.append("decision.expected_effects:mismatch")
    if action and sorted(decision.get("expected_observation_refs", [])) != sorted(
        action.get("expected_observation_refs", [])
    ):
        errors.append("decision.expected_observation_refs:mismatch")
    if action and sorted(decision.get("failure_observation_refs", [])) != sorted(
        action.get("failure_observation_refs", [])
    ):
        errors.append("decision.failure_observation_refs:mismatch")

    predicted = receipt.get("predicted")
    if not isinstance(predicted, dict):
        errors.append("predicted:must-be-object")
        predicted = {}
    for key in ("facts_added", "unknowns_resolved", "obligations_closed"):
        if sorted(predicted.get(key, [])) != sorted(expected_effects.get(key, [])):
            errors.append(f"predicted.{key}:mismatch")
    expected_observation_refs = action.get("expected_observation_refs", []) if action else []
    if sorted(predicted.get("observation_refs", [])) != sorted(expected_observation_refs):
        errors.append("predicted.observation_refs:mismatch")

    potential_before = state.get("current_potential", {})
    expected_delta = expected_effects.get("potential_delta", {}) if action else {}
    try:
        expected_potential_after = apply_potential_delta(
            potential_before, expected_delta, set(dimensions)
        )
    except ValueError as exc:
        expected_potential_after = {}
        errors.append(f"predicted.potential_after:{exc}")
    if predicted.get("potential_after") != expected_potential_after:
        errors.append("predicted.potential_after:mismatch")

    observed = receipt.get("observed")
    if not isinstance(observed, dict):
        errors.append("observed:must-be-object")
        observed = {}
    observed_facts = _as_set(observed.get("facts_added"), "observed.facts_added", errors)
    observed_unknowns = _as_set(
        observed.get("unknowns_resolved"), "observed.unknowns_resolved", errors
    )
    observed_obligations = _as_set(
        observed.get("obligations_closed"), "observed.obligations_closed", errors
    )
    for fact_id in sorted(observed_facts - facts):
        errors.append(f"observed.facts_added:unknown:{fact_id}")
    for unknown_id in sorted(observed_unknowns - unknowns):
        errors.append(f"observed.unknowns_resolved:unknown:{unknown_id}")
    for obligation_id in sorted(observed_obligations - obligations):
        errors.append(f"observed.obligations_closed:unknown:{obligation_id}")

    observation_rows = observed.get("observations")
    if not isinstance(observation_rows, list):
        errors.append("observed.observations:must-be-list")
        observation_rows = []
    observed_observation_ids: list[str] = []
    observed_outcomes: list[str] = []
    for index, row in enumerate(observation_rows):
        prefix = f"observed.observations[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}:must-be-object")
            continue
        observation_id = row.get("observation_id")
        outcome = row.get("outcome")
        observation = observations.get(str(observation_id))
        if not observation:
            errors.append(f"{prefix}.observation_id:unknown:{observation_id}")
            continue
        valid_outcomes = {
            item.get("outcome")
            for item in observation.get("outcomes", [])
            if isinstance(item, dict)
        }
        if outcome not in valid_outcomes:
            errors.append(f"{prefix}.outcome:unknown:{outcome}")
        if not row.get("evidence_ref"):
            errors.append(f"{prefix}.evidence_ref")
        observed_observation_ids.append(str(observation_id))
        observed_outcomes.append(f"{observation_id}={outcome}")

    proof = receipt.get("proof")
    if not isinstance(proof, dict):
        errors.append("proof:must-be-object")
        proof = {}
    if proof.get("status") not in PROOF_STATUS:
        errors.append("proof.status")
    proof_obligations = _as_set(proof.get("obligations"), "proof.obligations", errors)
    proof_evidence = proof.get("evidence_refs")
    if not isinstance(proof_evidence, list):
        errors.append("proof.evidence_refs:must-be-list")
        proof_evidence = []
    required_proofs = {
        str(item.get("proof_id"))
        for item in (action.get("proof_obligations", []) if action else [])
        if isinstance(item, dict) and item.get("proof_id")
    }

    surprise = receipt.get("surprise")
    if not isinstance(surprise, dict):
        errors.append("surprise:must-be-object")
        surprise = {}
    classification = surprise.get("classification")
    present = surprise.get("present")
    if classification not in SURPRISE:
        errors.append("surprise.classification")
    if not isinstance(present, bool):
        errors.append("surprise.present")
    if present is False and classification != "none":
        errors.append("surprise:false-but-classification-not-none")
    if present is True and classification == "none":
        errors.append("surprise:true-but-classification-none")
    if not surprise.get("statement"):
        errors.append("surprise.statement")

    result = receipt.get("result")
    if result not in RESULTS:
        errors.append("result")
    if classification == "model_failure" and result not in {
        "return_to_policy",
        "blocked",
        "rollback",
    }:
        errors.append("model_failure:invalid-result")
    if classification == "intent_failure" and result != "return_to_spec":
        errors.append("intent_failure:must-return-to-spec")
    if result == "return_to_policy" and classification not in {
        "new_branch",
        "model_failure",
        "expected_variance",
    }:
        errors.append("return_to_policy:surprise-classification-required")

    if result == "success":
        expected_facts = set(expected_effects.get("facts_added", []))
        expected_unknowns = set(expected_effects.get("unknowns_resolved", []))
        expected_obligations = set(expected_effects.get("obligations_closed", []))
        if observed_facts != expected_facts:
            errors.append("observed.facts_added:not-exactly-predicted")
        if observed_unknowns != expected_unknowns:
            errors.append("observed.unknowns_resolved:not-exactly-predicted")
        if observed_obligations != expected_obligations:
            errors.append("observed.obligations_closed:not-exactly-predicted")
        if action and action.get("kind") in PROOF_REQUIRED_ACTIONS:
            if proof.get("status") != "pass":
                errors.append("proof.status:must-pass-on-success")
        if not required_proofs.issubset(proof_obligations):
            errors.append("proof.obligations:missing")
        if proof.get("status") == "pass" and not proof_evidence:
            errors.append("proof.evidence_refs:empty-for-pass")
    elif result == "failure":
        failure_refs = set(action.get("failure_observation_refs", []) if action else [])
        if failure_refs and not (set(observed_observation_ids) & failure_refs):
            errors.append("failure:missing-failure-observation")

    observed_potential_after = observed.get("potential_after")
    if not isinstance(observed_potential_after, dict):
        errors.append("observed.potential_after:must-be-object")
        observed_potential_after = {}
    if set(observed_potential_after) != set(dimensions):
        errors.append("observed.potential_after:dimension-set-mismatch")

    state_after = receipt.get("state_after")
    if not isinstance(state_after, dict):
        errors.append("state_after:must-be-object")
        state_after = {}
    if not state_after.get("state_id"):
        errors.append("state_after.state_id")
    if state_after.get("state_id") == state.get("state_id"):
        errors.append("state_after.state_id:must-advance")
    if state_after.get("potential") != observed_potential_after:
        errors.append("state_after.potential:mismatch")

    predicted_comparison: dict[str, Any] = {}
    observed_comparison: dict[str, Any] = {}
    try:
        predicted_comparison = compare_potential(
            potential_before, expected_potential_after, dimensions, potential_order
        )
        observed_comparison = compare_potential(
            potential_before, observed_potential_after, dimensions, potential_order
        )
    except ValueError as exc:
        errors.append(f"potential:{exc}")
    if predicted_comparison and predicted_comparison.get("relation") != "improved":
        errors.append("predicted.potential:not-strictly-improving")
    if result == "success" and observed_comparison.get("relation") != "improved":
        errors.append("observed.potential:not-strictly-improving-on-success")
    if (
        predicted.get("potential_after") != observed_potential_after
        and classification == "none"
    ):
        errors.append("potential-surprise:not-classified")
    if (
        observed_comparison.get("relation") == "worsened"
        and result not in {"return_to_policy", "return_to_spec", "rollback", "blocked"}
    ):
        errors.append("observed.potential:worsened-without-control-return")

    evidence_refs = receipt.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        errors.append("evidence_refs:empty")

    details = {
        "transition_id": receipt.get("transition_id"),
        "action_id": action_id,
        "result": result,
        "observations": observed_outcomes,
        "predicted_potential_relation": predicted_comparison.get("relation"),
        "observed_potential_relation": observed_comparison.get("relation"),
        "first_observed_potential_difference": observed_comparison.get(
            "first_difference"
        ),
    }
    return errors, warnings, details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        epg, _ = load_epg(args.policy)
        policy_errors, policy_warnings, derived = validate_policy(epg)
        errors.extend(f"policy:{item}" for item in policy_errors)
        warnings.extend(f"policy:{item}" for item in policy_warnings)
        digest = canonical_digest(epg)
        state = load_wrapped(args.state, "execution_policy_state")
        errors.extend(
            f"state:{item}"
            for item in validate_state(state, epg, digest, derived)
        )
        decision = load_wrapped(args.decision, "execution_policy_decision")
        receipt = load_wrapped(args.receipt, "execution_transition_receipt")
    except Exception as exc:
        return emit("transition_receipt_gate", {}, [str(exc)], [])

    transition_errors, transition_warnings, details = validate_transition(
        epg,
        state,
        decision,
        receipt,
        policy_digest=digest,
    )
    errors.extend(transition_errors)
    warnings.extend(transition_warnings)
    return emit("transition_receipt_gate", details, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
