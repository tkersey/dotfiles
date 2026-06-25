#!/usr/bin/env -S uv run --with pyyaml python
"""Validate CBD-v2 as a closed, artifact-bound doctrine evidence graph."""

from __future__ import annotations

import argparse
from collections import Counter
from typing import Any, Iterable

from common import (
    BOOLISH,
    CONFIDENCE,
    DOCTRINE_STATUS,
    EVIDENCE_LANES,
    artifact_state_id,
    check_refs,
    dump_data,
    is_no,
    is_yes,
    load_data,
    report,
    require_id,
    require_list,
    require_object,
    require_text,
    sha256_digest,
    unique_rows,
    unwrap,
    validate_artifact_state,
)
from intent_gate import validate_cdi

DESTINATIONS = {
    "code",
    "type_or_representation",
    "test_or_property",
    "static_tool_or_linter",
    "CI_gate",
    "AGENTS_or_repository_guidance",
    "ADR_or_reference",
    "negative_ledger",
    "repository_root_skill",
    "focused_skill",
    "retain_in_doctrine",
    "reject",
}
SATURATION = {"saturated", "targeted_search_required", "blocked"}
CLAIM_KINDS = {"fact", "inference", "open_question", "recommendation"}
CLAIM_STATUSES = {"active", "contradicted", "superseded", "unresolved"}
SEARCH_STATUSES = {"answered", "no_evidence", "open", "blocked"}
FAILURE_STATUSES = {"active", "provisional", "retired"}
NEGATIVE_ROUTE_STATUSES = {"suspected", "witnessed", "canonical_projection", "retired"}
PROOF_STATUSES = {"design_only", "executed_current", "historical", "manual"}
CONTRADICTION_STATUSES = {"resolved", "preserved", "unresolved"}
CANDIDATE_STATUSES = {"rejected", "recommended_for_trial", "accepted"}
POSITIVE_CRITERIA = {
    "recurring_trigger",
    "consequential_decision",
    "stable_governing_law",
    "independent_activation",
    "standalone_workflow",
    "observable_success_and_failure",
}
NEGATIVE_CRITERIA = {
    "better_as_code",
    "better_as_test",
    "better_as_tooling",
    "better_as_docs",
}
ALL_CRITERIA = POSITIVE_CRITERIA | NEGATIVE_CRITERIA
ADDITIONAL_SEARCH_KEYS = {
    "repository_fingerprint",
    "authority_map",
    "governing_laws",
    "proof_map",
    "knowledge_routes",
    "skill_portfolio",
}


def validate_enum(value: Any, allowed: set[str], label: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{label}:invalid:{value}")


def validate_ref_list(
    row: dict[str, Any],
    field: str,
    allowed: set[str],
    prefix: str,
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    return check_refs(
        row.get(field),
        allowed,
        f"{prefix}.{field}",
        errors,
        nonempty=nonempty,
    )


def validate_evidence_refs(
    row: dict[str, Any],
    evidence_ids: set[str],
    prefix: str,
    errors: list[str],
    *,
    nonempty: bool = True,
) -> list[str]:
    return validate_ref_list(
        row,
        "evidence_refs",
        evidence_ids,
        prefix,
        errors,
        nonempty=nonempty,
    )


def validate_statused_doctrine_row(
    row: dict[str, Any],
    prefix: str,
    errors: list[str],
) -> None:
    validate_enum(row.get("doctrine_status"), DOCTRINE_STATUS, f"{prefix}.doctrine_status", errors)
    require_text(row.get("normative_authority"), f"{prefix}.normative_authority", errors)
    if row.get("doctrine_status") in {"observed_current", "documented_intent"}:
        require_list(
            row.get("current_evidence_refs"),
            f"{prefix}.current_evidence_refs",
            errors,
            nonempty=True,
        )
    if row.get("doctrine_status") in {"explicit_target", "proposed"}:
        require_list(
            row.get("target_authority_refs"),
            f"{prefix}.target_authority_refs",
            errors,
            nonempty=True,
        )
        require_text(row.get("gap_statement"), f"{prefix}.gap_statement", errors)


def validate_verification(
    verification: Any,
    artifact_state: dict[str, Any],
    prefix: str,
    errors: list[str],
) -> None:
    value = require_object(verification, prefix, errors)
    status = value.get("status")
    validate_enum(status, PROOF_STATUSES, f"{prefix}.status", errors)
    if status == "executed_current":
        for field in ("command", "result_ref", "toolchain", "target", "verified_at"):
            require_text(value.get(field), f"{prefix}.{field}", errors)
        if value.get("exit_code") != 0:
            errors.append(f"{prefix}.exit_code:must-be-zero")
        if value.get("artifact_state_id") != artifact_state.get("artifact_state_id"):
            errors.append(f"{prefix}.artifact_state_id:mismatch")
    elif status in {"historical", "manual"}:
        require_text(value.get("result_ref"), f"{prefix}.result_ref", errors)
        require_text(value.get("artifact_state_id"), f"{prefix}.artifact_state_id", errors)
    elif status == "design_only":
        require_text(value.get("reason_not_executed"), f"{prefix}.reason_not_executed", errors)


def validate_candidacy_criterion(
    value: Any,
    criterion: str,
    evidence_ids: set[str],
    prefix: str,
    errors: list[str],
) -> str | None:
    row = require_object(value, prefix, errors)
    verdict = row.get("verdict")
    if verdict not in {"yes", "no", "unknown"}:
        errors.append(f"{prefix}.verdict:invalid")
        verdict = None
    refs = validate_ref_list(
        row,
        "evidence_refs",
        evidence_ids,
        prefix,
        errors,
        nonempty=verdict in {"yes", "no"},
    )
    validate_ref_list(
        row,
        "counterevidence_refs",
        evidence_ids,
        prefix,
        errors,
    )
    require_text(row.get("rationale"), f"{prefix}.rationale", errors)
    return verdict


def validate_candidate(
    candidate: dict[str, Any],
    prefix: str,
    *,
    candidate_type: str,
    law_ids: set[str],
    claim_ids: set[str],
    evidence_ids: set[str],
    canonical_negative_routes: set[str],
    errors: list[str],
) -> str | None:
    require_id(candidate.get("candidate_id"), f"{prefix}.candidate_id", errors)
    require_text(candidate.get("proposed_name"), f"{prefix}.proposed_name", errors)
    if candidate.get("candidate_type") != candidate_type:
        errors.append(f"{prefix}.candidate_type:expected-{candidate_type}")
    require_text(candidate.get("mission"), f"{prefix}.mission", errors)
    validate_ref_list(
        candidate,
        "governing_law_ids",
        law_ids,
        prefix,
        errors,
        nonempty=True,
    )
    validate_ref_list(
        candidate,
        "source_claim_ids",
        claim_ids,
        prefix,
        errors,
        nonempty=True,
    )
    for field in (
        "trigger_examples",
        "non_triggers",
        "consequential_decisions",
        "required_artifacts",
        "success_signals",
        "failure_signals",
        "standalone_use_cases",
    ):
        require_list(
            candidate.get(field),
            f"{prefix}.{field}",
            errors,
            nonempty=field
            in {
                "trigger_examples",
                "non_triggers",
                "consequential_decisions",
                "required_artifacts",
                "success_signals",
                "failure_signals",
            },
        )
    prohibited = validate_ref_list(
        candidate,
        "prohibited_route_ids",
        canonical_negative_routes,
        prefix,
        errors,
    )
    candidacy = require_object(candidate.get("candidacy"), f"{prefix}.candidacy", errors)
    for extra in sorted(set(candidacy) - ALL_CRITERIA):
        errors.append(f"{prefix}.candidacy:unexpected:{extra}")
    verdicts: dict[str, str | None] = {}
    for criterion in sorted(ALL_CRITERIA):
        verdicts[criterion] = validate_candidacy_criterion(
            candidacy.get(criterion),
            criterion,
            evidence_ids,
            f"{prefix}.candidacy.{criterion}",
            errors,
        )
    status = candidate.get("status")
    validate_enum(status, CANDIDATE_STATUSES, f"{prefix}.status", errors)
    pass_gate = all(verdicts.get(key) == "yes" for key in POSITIVE_CRITERIA) and all(
        verdicts.get(key) == "no" for key in NEGATIVE_CRITERIA
    )
    if status in {"recommended_for_trial", "accepted"} and not pass_gate:
        errors.append(f"{prefix}.status:{status}-with-failed-candidacy")
    empirical = validate_ref_list(
        candidate,
        "empirical_evidence_refs",
        evidence_ids,
        prefix,
        errors,
    )
    if status == "accepted" and not empirical:
        errors.append(f"{prefix}.status:accepted-requires-empirical-evidence")
    if status == "rejected":
        require_text(candidate.get("rejection_reason"), f"{prefix}.rejection_reason", errors)
        if prohibited:
            errors.append(f"{prefix}.prohibited_route_ids:not-allowed-when-rejected")
    return status


def validate_doctrine(
    body: dict[str, Any],
    *,
    require_saturated: bool = False,
) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {}

    if body.get("doctrine_version") != "CBD-v2":
        errors.append("doctrine_version:expected-CBD-v2")
    require_id(body.get("doctrine_id"), "doctrine_id", errors)

    intent_wrapper = require_object(body.get("intent"), "intent", errors)
    intent = unwrap(intent_wrapper, "codebase_doctrine_intent") if intent_wrapper else {}
    validate_cdi(intent, errors, warnings)
    artifact_state = validate_artifact_state(body.get("artifact_state"), errors)
    if intent:
        if artifact_state.get("intent_id") != intent.get("intent_id"):
            errors.append("artifact_state.intent_id:mismatch")
        expected_intent_digest = sha256_digest(intent)
        if artifact_state.get("intent_digest") != expected_intent_digest:
            errors.append("artifact_state.intent_digest:mismatch")

    request = require_object(body.get("request"), "request", errors)
    if request.get("mode") not in {"doctrine", "deep"}:
        errors.append("request.mode:expected-doctrine-or-deep")
    for field in ("scope", "depth"):
        require_text(request.get(field), f"request.{field}", errors)
    if request.get("scope") and artifact_state.get("scope"):
        if request.get("scope") != artifact_state.get("scope"):
            errors.append("request.scope:artifact-state-mismatch")

    search_ids, search_by_id = unique_rows(
        body.get("search_ledger"),
        "question_id",
        "search_ledger",
        errors,
        required=True,
    )
    evidence_ids, evidence_by_id = unique_rows(
        body.get("evidence_index"),
        "evidence_id",
        "evidence_index",
        errors,
        required=True,
    )
    claim_ids, claim_by_id = unique_rows(
        body.get("claims"),
        "claim_id",
        "claims",
        errors,
        required=True,
    )

    for question_id, row in search_by_id.items():
        prefix = f"search_ledger[{question_id}]"
        require_text(row.get("question"), f"{prefix}.question", errors)
        require_text(row.get("why_it_matters"), f"{prefix}.why_it_matters", errors)
        lanes = require_list(row.get("lanes"), f"{prefix}.lanes", errors, nonempty=True)
        for lane in lanes:
            if lane not in EVIDENCE_LANES:
                errors.append(f"{prefix}.lanes:invalid:{lane}")
        require_list(row.get("search_methods"), f"{prefix}.search_methods", errors, nonempty=True)
        check_refs(row.get("evidence_found"), evidence_ids, f"{prefix}.evidence_found", errors)
        status = row.get("status")
        validate_enum(status, SEARCH_STATUSES, f"{prefix}.status", errors)
        require_text(row.get("model_change"), f"{prefix}.model_change", errors)
        actual = {
            evidence_id
            for evidence_id, evidence in evidence_by_id.items()
            if evidence.get("question_id") == question_id
        }
        declared = set(row.get("evidence_found") or [])
        if declared != actual:
            errors.append(
                f"{prefix}.evidence_found:reverse-mismatch:"
                f"declared={sorted(declared)}:actual={sorted(actual)}"
            )
        if status == "answered" and not actual:
            errors.append(f"{prefix}.status:answered-without-evidence")
        if status == "no_evidence" and actual:
            warnings.append(f"{prefix}.status:no_evidence-with-evidence")

    for evidence_id, row in evidence_by_id.items():
        prefix = f"evidence_index[{evidence_id}]"
        if row.get("lane") not in EVIDENCE_LANES:
            errors.append(f"{prefix}.lane:invalid")
        question_id = row.get("question_id")
        if question_id not in search_ids:
            errors.append(f"{prefix}.question_id:unknown:{question_id}")
        require_text(row.get("observation"), f"{prefix}.observation", errors)
        require_text(row.get("evidence_ref"), f"{prefix}.evidence_ref", errors)
        if row.get("artifact_state_id") != artifact_state.get("artifact_state_id"):
            errors.append(f"{prefix}.artifact_state_id:mismatch")
        require_text(row.get("scope"), f"{prefix}.scope", errors)
        validate_enum(row.get("confidence"), CONFIDENCE, f"{prefix}.confidence", errors)
        supports = check_refs(
            row.get("supports_claim_ids"),
            claim_ids,
            f"{prefix}.supports_claim_ids",
            errors,
        )
        contradicts = check_refs(
            row.get("contradicts_claim_ids"),
            claim_ids,
            f"{prefix}.contradicts_claim_ids",
            errors,
        )
        if set(supports) & set(contradicts):
            errors.append(f"{prefix}:same-claim-supported-and-contradicted")
        require_text(row.get("provenance"), f"{prefix}.provenance", errors)

    for claim_id, row in claim_by_id.items():
        prefix = f"claims[{claim_id}]"
        validate_enum(row.get("kind"), CLAIM_KINDS, f"{prefix}.kind", errors)
        require_text(row.get("statement"), f"{prefix}.statement", errors)
        refs = validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)
        counterrefs = validate_ref_list(
            row,
            "counterevidence_refs",
            evidence_ids,
            prefix,
            errors,
        )
        validate_enum(row.get("confidence"), CONFIDENCE, f"{prefix}.confidence", errors)
        validate_enum(row.get("status"), CLAIM_STATUSES, f"{prefix}.status", errors)
        if row.get("durable") not in BOOLISH:
            errors.append(f"{prefix}.durable:expected-yes-or-no")
        for evidence_id in refs:
            if claim_id not in set(evidence_by_id[evidence_id].get("supports_claim_ids") or []):
                errors.append(f"{prefix}.evidence_refs:reverse-missing:{evidence_id}")
        for evidence_id in counterrefs:
            if claim_id not in set(
                evidence_by_id[evidence_id].get("contradicts_claim_ids") or []
            ):
                errors.append(f"{prefix}.counterevidence_refs:reverse-missing:{evidence_id}")

    fingerprint = require_object(body.get("repository_fingerprint"), "repository_fingerprint", errors)
    for field in (
        "repository_kind",
        "deployment_or_distribution",
        "dominant_architecture",
        "dependency_direction",
        "repository_dialect",
        "confidence",
    ):
        require_text(fingerprint.get(field), f"repository_fingerprint.{field}", errors)
    for field in (
        "primary_languages",
        "build_and_test_systems",
        "top_level_subsystems",
        "public_contract_roots",
        "entrypoint_classes",
        "evidence_refs",
    ):
        require_list(fingerprint.get(field), f"repository_fingerprint.{field}", errors)
    check_refs(
        fingerprint.get("evidence_refs"),
        evidence_ids,
        "repository_fingerprint.evidence_refs",
        errors,
        nonempty=True,
    )

    system_map = require_object(body.get("system_map"), "system_map", errors)
    for field in (
        "components",
        "connections",
        "representative_flows",
        "external_boundaries",
        "configuration_roots",
        "persistence_roots",
        "feedback_loops",
        "delays_and_async_boundaries",
        "evidence_refs",
    ):
        require_list(system_map.get(field), f"system_map.{field}", errors)
    check_refs(
        system_map.get("evidence_refs"),
        evidence_ids,
        "system_map.evidence_refs",
        errors,
        nonempty=True,
    )

    authority_map = require_object(body.get("authority_map"), "authority_map", errors)
    authority_ids, authority_by_id = unique_rows(
        authority_map.get("authorities"),
        "authority_id",
        "authority_map.authorities",
        errors,
        required=True,
    )
    for authority_id, row in authority_by_id.items():
        prefix = f"authority_map.authorities[{authority_id}]"
        require_text(row.get("owner"), f"{prefix}.owner", errors)
        validate_statused_doctrine_row(row, prefix, errors)
        for field in (
            "owned_state",
            "creation_paths",
            "transition_paths",
            "readers",
            "certificates_or_witnesses",
            "authority_transfers",
            "shadow_owners",
            "late_validations",
        ):
            require_list(row.get(field), f"{prefix}.{field}", errors)
        require_text(row.get("enforcement_boundary"), f"{prefix}.enforcement_boundary", errors)
        refs = validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)
        check_refs(
            row.get("current_evidence_refs"),
            evidence_ids,
            f"{prefix}.current_evidence_refs",
            errors,
        )

    law_ids, law_by_id = unique_rows(
        body.get("governing_laws"),
        "law_id",
        "governing_laws",
        errors,
        required=True,
    )
    for law_id, row in law_by_id.items():
        prefix = f"governing_laws[{law_id}]"
        require_text(row.get("statement"), f"{prefix}.statement", errors)
        if row.get("owner") not in authority_ids:
            errors.append(f"{prefix}.owner:unknown:{row.get('owner')}")
        validate_statused_doctrine_row(row, prefix, errors)
        for field in ("observations", "counterexamples", "proof_obligations"):
            require_list(row.get(field), f"{prefix}.{field}", errors, nonempty=True)
        validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)
        check_refs(
            row.get("current_evidence_refs"),
            evidence_ids,
            f"{prefix}.current_evidence_refs",
            errors,
        )
        require_list(row.get("target_authority_refs"), f"{prefix}.target_authority_refs", errors)

    behavioral = require_object(body.get("behavioral_model"), "behavioral_model", errors)
    for field in (
        "carriers",
        "operations",
        "observations",
        "state_classes",
        "transitions",
        "non_laws",
        "forbidden_states_or_transitions",
        "interpreters_or_projections",
        "evidence_refs",
    ):
        require_list(behavioral.get(field), f"behavioral_model.{field}", errors)
    check_refs(behavioral.get("laws"), law_ids, "behavioral_model.laws", errors)
    check_refs(
        behavioral.get("evidence_refs"),
        evidence_ids,
        "behavioral_model.evidence_refs",
        errors,
        nonempty=True,
    )

    proof_map = require_object(body.get("proof_map"), "proof_map", errors)
    proof_ids, proof_by_id = unique_rows(
        proof_map.get("proof_surfaces"),
        "proof_surface_id",
        "proof_map.proof_surfaces",
        errors,
        required=True,
    )

    invariant_ids, invariant_by_id = unique_rows(
        body.get("owned_invariants"),
        "invariant_id",
        "owned_invariants",
        errors,
    )
    for invariant_id, row in invariant_by_id.items():
        prefix = f"owned_invariants[{invariant_id}]"
        if row.get("owner") not in authority_ids:
            errors.append(f"{prefix}.owner:unknown:{row.get('owner')}")
        validate_statused_doctrine_row(row, prefix, errors)
        for field in (
            "statement",
            "source_of_truth",
            "initialization",
            "enforcement_boundary",
            "exception_ownership",
        ):
            require_text(row.get(field), f"{prefix}.{field}", errors)
        for field in (
            "preserving_transitions",
            "violating_counterexamples",
            "current_enforcement",
            "missing_or_late_enforcement",
        ):
            require_list(
                row.get(field),
                f"{prefix}.{field}",
                errors,
                nonempty=field in {"preserving_transitions", "violating_counterexamples"},
            )
        validate_ref_list(
            row,
            "proof_surface_ids",
            proof_ids,
            prefix,
            errors,
            nonempty=True,
        )
        validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)
        check_refs(
            row.get("current_evidence_refs"),
            evidence_ids,
            f"{prefix}.current_evidence_refs",
            errors,
        )
        require_list(row.get("target_authority_refs"), f"{prefix}.target_authority_refs", errors)

    doctrine_subject_ids = law_ids | invariant_ids
    for proof_id, row in proof_by_id.items():
        prefix = f"proof_map.proof_surfaces[{proof_id}]"
        check_refs(
            row.get("law_or_invariant_ids"),
            doctrine_subject_ids,
            f"{prefix}.law_or_invariant_ids",
            errors,
            nonempty=True,
        )
        require_text(row.get("kind"), f"{prefix}.kind", errors)
        require_list(row.get("artifact_refs"), f"{prefix}.artifact_refs", errors, nonempty=True)
        require_text(row.get("strength"), f"{prefix}.strength", errors)
        require_list(row.get("gaps"), f"{prefix}.gaps", errors)
        validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)
        validate_verification(row.get("verification"), artifact_state, f"{prefix}.verification", errors)

    for law_id, row in law_by_id.items():
        prefix = f"governing_laws[{law_id}]"
        linked = validate_ref_list(
            row,
            "proof_surface_ids",
            proof_ids,
            prefix,
            errors,
        )
        if not linked and not row.get("proof_gap"):
            errors.append(f"{prefix}:needs-proof-surface-or-proof-gap")

    boundary_ids, boundary_by_id = unique_rows(
        body.get("boundary_rules"),
        "boundary_rule_id",
        "boundary_rules",
        errors,
    )
    for boundary_id, row in boundary_by_id.items():
        prefix = f"boundary_rules[{boundary_id}]"
        validate_statused_doctrine_row(row, prefix, errors)
        for field in (
            "statement",
            "accepted_input",
            "rejected_input",
            "authority_before",
            "authority_after",
            "transferred_state_or_evidence",
        ):
            require_text(row.get(field), f"{prefix}.{field}", errors)
        validate_ref_list(
            row,
            "governing_law_ids",
            law_ids,
            prefix,
            errors,
            nonempty=True,
        )
        validate_ref_list(
            row,
            "proof_surface_ids",
            proof_ids,
            prefix,
            errors,
            nonempty=True,
        )
        validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)
        check_refs(
            row.get("current_evidence_refs"),
            evidence_ids,
            f"{prefix}.current_evidence_refs",
            errors,
        )
        require_list(row.get("target_authority_refs"), f"{prefix}.target_authority_refs", errors)

    failure_ids, failure_by_id = unique_rows(
        body.get("failure_families"),
        "family_id",
        "failure_families",
        errors,
    )
    for family_id, row in failure_by_id.items():
        prefix = f"failure_families[{family_id}]"
        validate_enum(row.get("status"), FAILURE_STATUSES, f"{prefix}.status", errors)
        governing = validate_ref_list(
            row,
            "governing_law_ids",
            law_ids,
            prefix,
            errors,
        )
        if not governing and row.get("status") != "provisional":
            errors.append(f"{prefix}.governing_law_ids:empty")
        for field in (
            "local_surfaces",
            "independent_witnesses",
            "recurring_signatures",
            "historical_repairs",
            "routes_that_failed",
        ):
            require_list(row.get(field), f"{prefix}.{field}", errors)
        require_text(row.get("unresolved_risk"), f"{prefix}.unresolved_risk", errors)
        validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)

    negative_ids, negative_by_id = unique_rows(
        body.get("negative_routes"),
        "route_id",
        "negative_routes",
        errors,
    )
    canonical_negative_routes: set[str] = set()
    for route_id, row in negative_by_id.items():
        prefix = f"negative_routes[{route_id}]"
        status = row.get("status")
        validate_enum(status, NEGATIVE_ROUTE_STATUSES, f"{prefix}.status", errors)
        require_text(row.get("route_family"), f"{prefix}.route_family", errors)
        require_text(row.get("reason"), f"{prefix}.reason", errors)
        validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)
        require_list(
            row.get("applicability_conditions"),
            f"{prefix}.applicability_conditions",
            errors,
            nonempty=status == "canonical_projection",
        )
        require_list(
            row.get("reopening_criteria"),
            f"{prefix}.reopening_criteria",
            errors,
            nonempty=status == "canonical_projection",
        )
        if status == "canonical_projection":
            canonical_negative_routes.add(route_id)
            require_text(row.get("ledger_id"), f"{prefix}.ledger_id", errors)
            require_text(
                row.get("projection_fingerprint"),
                f"{prefix}.projection_fingerprint",
                errors,
            )
        elif row.get("ledger_id") or row.get("projection_fingerprint"):
            warnings.append(f"{prefix}:noncanonical-route-has-ledger-fields")

    contradiction_ids, contradiction_by_id = unique_rows(
        body.get("contradictions"),
        "contradiction_id",
        "contradictions",
        errors,
    )
    unresolved_material: set[str] = set()
    for contradiction_id, row in contradiction_by_id.items():
        prefix = f"contradictions[{contradiction_id}]"
        validate_ref_list(
            row,
            "claim_refs",
            claim_ids,
            prefix,
            errors,
            nonempty=True,
        )
        validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)
        status = row.get("resolution_status")
        validate_enum(status, CONTRADICTION_STATUSES, f"{prefix}.resolution_status", errors)
        if row.get("material") not in BOOLISH:
            errors.append(f"{prefix}.material:expected-yes-or-no")
        require_text(row.get("resolution"), f"{prefix}.resolution", errors)
        require_text(
            row.get("residual_uncertainty"),
            f"{prefix}.residual_uncertainty",
            errors,
        )
        if is_yes(row.get("material")) and status == "unresolved":
            unresolved_material.add(contradiction_id)

    knowledge_ids, knowledge_by_id = unique_rows(
        body.get("knowledge_routes"),
        "knowledge_id",
        "knowledge_routes",
        errors,
    )
    routed_counter: Counter[str] = Counter()
    for knowledge_id, row in knowledge_by_id.items():
        prefix = f"knowledge_routes[{knowledge_id}]"
        refs = validate_ref_list(
            row,
            "source_claim_ids",
            claim_ids,
            prefix,
            errors,
            nonempty=True,
        )
        for claim_id in refs:
            routed_counter[claim_id] += 1
        validate_enum(
            row.get("primary_destination"),
            DESTINATIONS,
            f"{prefix}.primary_destination",
            errors,
        )
        destinations = require_list(
            row.get("secondary_destinations"),
            f"{prefix}.secondary_destinations",
            errors,
        )
        for destination in destinations:
            if destination not in DESTINATIONS:
                errors.append(f"{prefix}.secondary_destinations:invalid:{destination}")
        require_text(row.get("statement"), f"{prefix}.statement", errors)
        require_text(row.get("reason"), f"{prefix}.reason", errors)
        require_text(row.get("enforcement_strength"), f"{prefix}.enforcement_strength", errors)
        require_text(row.get("owner"), f"{prefix}.owner", errors)
        require_text(row.get("status"), f"{prefix}.status", errors)

    durable_active_claims = {
        claim_id
        for claim_id, row in claim_by_id.items()
        if is_yes(row.get("durable")) and row.get("status") == "active"
    }
    for claim_id in sorted(durable_active_claims):
        count = routed_counter[claim_id]
        if count == 0:
            errors.append(f"durable_claim:unrouted:{claim_id}")
        elif count > 1:
            errors.append(f"durable_claim:multiple-primary-routes:{claim_id}:{count}")

    root_candidate = body.get("repository_root_skill")
    active_candidate_count = 0
    if root_candidate is not None:
        root = require_object(root_candidate, "repository_root_skill", errors)
        status = validate_candidate(
            root,
            "repository_root_skill",
            candidate_type="root",
            law_ids=law_ids,
            claim_ids=claim_ids,
            evidence_ids=evidence_ids,
            canonical_negative_routes=canonical_negative_routes,
            errors=errors,
        )
        if status in {"recommended_for_trial", "accepted"}:
            active_candidate_count += 1

    focused = require_list(
        body.get("focused_skill_candidates"),
        "focused_skill_candidates",
        errors,
    )
    focused_ids: set[str] = set()
    active_focused = 0
    for index, raw in enumerate(focused):
        prefix = f"focused_skill_candidates[{index}]"
        candidate = require_object(raw, prefix, errors)
        candidate_id = require_id(candidate.get("candidate_id"), f"{prefix}.candidate_id", errors)
        if candidate_id:
            if candidate_id in focused_ids:
                errors.append(f"focused_skill_candidates:duplicate:{candidate_id}")
            focused_ids.add(candidate_id)
        status = validate_candidate(
            candidate,
            prefix,
            candidate_type="focused",
            law_ids=law_ids,
            claim_ids=claim_ids,
            evidence_ids=evidence_ids,
            canonical_negative_routes=canonical_negative_routes,
            errors=errors,
        )
        if status in {"recommended_for_trial", "accepted"}:
            active_focused += 1
    if active_focused > 5:
        errors.append(f"focused_skill_candidates:active-count:{active_focused}:max-5")

    rejected = require_list(
        body.get("rejected_skill_candidates"),
        "rejected_skill_candidates",
        errors,
    )
    for index, raw in enumerate(rejected):
        prefix = f"rejected_skill_candidates[{index}]"
        row = require_object(raw, prefix, errors)
        require_id(row.get("candidate_id"), f"{prefix}.candidate_id", errors)
        require_text(row.get("proposed_name"), f"{prefix}.proposed_name", errors)
        require_text(row.get("reason"), f"{prefix}.reason", errors)
        validate_enum(
            row.get("primary_destination"),
            DESTINATIONS,
            f"{prefix}.primary_destination",
            errors,
        )
        validate_evidence_refs(row, evidence_ids, prefix, errors, nonempty=True)

    if intent and is_no(intent.get("skill_portfolio_requested")):
        if active_candidate_count or active_focused:
            errors.append("skill_portfolio:not-requested-but-active-candidates-present")

    specialist_receipts = require_list(
        body.get("specialist_receipts"),
        "specialist_receipts",
        errors,
    )
    if request.get("mode") == "deep" and not specialist_receipts:
        errors.append("specialist_receipts:required-for-deep-mode")
    for index, raw in enumerate(specialist_receipts):
        prefix = f"specialist_receipts[{index}]"
        row = require_object(raw, prefix, errors)
        for field in ("assignment_id", "worker", "packet_digest", "final_call"):
            require_text(row.get(field), f"{prefix}.{field}", errors)
        if row.get("accepted") not in BOOLISH:
            errors.append(f"{prefix}.accepted:expected-yes-or-no")

    open_questions = require_list(body.get("open_questions"), "open_questions", errors)
    next_actions = require_list(body.get("next_actions"), "next_actions", errors)
    require_list(body.get("boundary_rules"), "boundary_rules", errors)
    require_list(body.get("failure_families"), "failure_families", errors)
    require_list(body.get("negative_routes"), "negative_routes", errors)

    saturation = require_object(body.get("saturation"), "saturation", errors)
    required_lanes = set(
        require_list(
            saturation.get("lanes_required"),
            "saturation.lanes_required",
            errors,
            nonempty=True,
        )
    )
    covered_lanes = set(
        require_list(
            saturation.get("lanes_covered"),
            "saturation.lanes_covered",
            errors,
        )
    )
    for lane in required_lanes | covered_lanes:
        if lane not in EVIDENCE_LANES:
            errors.append(f"saturation.lane:invalid:{lane}")
    missing_lanes = sorted(required_lanes - covered_lanes)
    verdict = saturation.get("verdict")
    validate_enum(verdict, SATURATION, "saturation.verdict", errors)
    sat_open = require_list(saturation.get("open_questions"), "saturation.open_questions", errors)
    sat_contradictions = check_refs(
        saturation.get("contradictions_remaining"),
        contradiction_ids,
        "saturation.contradictions_remaining",
        errors,
    )
    require_text(
        saturation.get("last_material_model_change_ref"),
        "saturation.last_material_model_change_ref",
        errors,
    )
    additional = require_object(
        saturation.get("additional_search_would_change"),
        "saturation.additional_search_would_change",
        errors,
    )
    for key in sorted(ADDITIONAL_SEARCH_KEYS):
        if additional.get(key) not in BOOLISH:
            errors.append(f"saturation.additional_search_would_change.{key}:expected-yes-or-no")
    extra_keys = sorted(set(additional) - ADDITIONAL_SEARCH_KEYS)
    for key in extra_keys:
        errors.append(f"saturation.additional_search_would_change:unexpected:{key}")
    targeted = require_list(
        saturation.get("next_targeted_queries"),
        "saturation.next_targeted_queries",
        errors,
    )

    if verdict == "saturated":
        if missing_lanes:
            errors.append("saturation:saturated-with-uncovered-lanes:" + ",".join(missing_lanes))
        if sat_open or open_questions:
            errors.append("saturation:saturated-with-open-questions")
        if unresolved_material:
            errors.append(
                "saturation:saturated-with-material-contradictions:"
                + ",".join(sorted(unresolved_material))
            )
        if set(sat_contradictions) != unresolved_material:
            errors.append("saturation.contradictions_remaining:reverse-mismatch")
        if any(is_yes(value) for value in additional.values()):
            errors.append("saturation:saturated-but-additional-search-may-change")
        open_search = [
            qid
            for qid, row in search_by_id.items()
            if row.get("status") in {"open", "blocked"}
        ]
        if open_search:
            errors.append("saturation:saturated-with-open-search:" + ",".join(open_search))
    elif verdict == "targeted_search_required":
        if not targeted:
            errors.append("saturation.next_targeted_queries:empty")
    elif verdict == "blocked":
        if not sat_open and not open_questions:
            warnings.append("saturation:blocked-without-open-questions")
    if require_saturated and verdict != "saturated":
        errors.append("saturation:not-saturated")

    confidence = require_object(body.get("confidence"), "confidence", errors)
    validate_enum(confidence.get("overall"), CONFIDENCE, "confidence.overall", errors)
    require_list(
        confidence.get("high_confidence_sections"),
        "confidence.high_confidence_sections",
        errors,
    )
    require_list(
        confidence.get("low_confidence_sections"),
        "confidence.low_confidence_sections",
        errors,
    )

    counts.update(
        {
            "search_questions": len(search_ids),
            "evidence": len(evidence_ids),
            "claims": len(claim_ids),
            "authorities": len(authority_ids),
            "laws": len(law_ids),
            "invariants": len(invariant_ids),
            "proof_surfaces": len(proof_ids),
            "failure_families": len(failure_ids),
            "negative_routes": len(negative_ids),
            "knowledge_routes": len(knowledge_ids),
            "active_root_skills": active_candidate_count,
            "active_focused_skills": active_focused,
            "specialist_receipts": len(specialist_receipts),
        }
    )
    return errors, warnings, counts


def validate_value(
    value: dict[str, Any],
    *,
    require_saturated: bool = False,
) -> tuple[list[str], list[str], dict[str, int]]:
    body = unwrap(value, "codebase_doctrine")
    return validate_doctrine(body, require_saturated=require_saturated)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--require-saturated", action="store_true")
    args = parser.parse_args()
    try:
        value = load_data(args.file)
        errors, warnings, counts = validate_value(
            value,
            require_saturated=args.require_saturated,
        )
    except Exception as exc:
        errors, warnings, counts = [str(exc)], [], {}
    print(
        dump_data(
            report("doctrine_gate", errors, warnings, counts=counts),
            "json",
        ),
        end="",
    )
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
