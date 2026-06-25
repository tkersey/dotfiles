#!/usr/bin/env -S uv run --with pyyaml python
"""Validate DIG-v2, CDI-v2, CDGH-v2, and Codebase Doctrine grill closure packets."""

from __future__ import annotations

import argparse
from typing import Any

from common import (
    BOOLISH,
    CONFIDENCE,
    deterministic_id,
    dump_data,
    is_no,
    is_yes,
    load_data,
    reject_extras,
    report,
    require_id,
    require_list,
    require_object,
    require_text,
    sha256_digest,
    unwrap,
)

POSTURES = {"descriptive", "prescriptive", "gap_analysis", "mixed"}
SOURCES = {"direct", "grill", "prior_doctrine"}
PRODUCTS = {
    "correctness_atlas",
    "knowledge_routing",
    "enforcement_recommendations",
    "repository_root_skill",
    "focused_skill_candidates",
    "existing_skill_audit",
}
LANES = {
    "target_boundary",
    "consumers",
    "posture",
    "desired_products",
    "correctness_priorities",
    "non_goals",
    "proof_bar",
    "compatibility_posture",
    "versioning_or_migration",
    "persistence",
}
HYPOTHESIS_AUTHORITIES = {"explicit_user", "repository_guidance", "provisional"}
HYPOTHESIS_STATUSES = {"normative_requirement", "hypothesis", "question"}


def intent_material(body: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in body.items() if key != "intent_id"}


def expected_intent_id(body: dict[str, Any]) -> str:
    return deterministic_id("CDI", intent_material(body))


def validate_target(value: Any, errors: list[str], prefix: str) -> dict[str, Any]:
    target = require_object(value, prefix, errors)
    for field in ("repository", "boundary_statement"):
        require_text(target.get(field), f"{prefix}.{field}", errors)
    for field in ("included_subsystems", "excluded_subsystems", "cross_cutting_flows"):
        require_list(target.get(field), f"{prefix}.{field}", errors)
    return target


def validate_hypotheses(value: Any, errors: list[str], prefix: str) -> None:
    rows = require_list(value, prefix, errors)
    seen: set[str] = set()
    for index, raw in enumerate(rows):
        row_prefix = f"{prefix}[{index}]"
        row = require_object(raw, row_prefix, errors)
        hyp_id = require_id(row.get("hypothesis_id"), f"{row_prefix}.hypothesis_id", errors)
        if hyp_id:
            if hyp_id in seen:
                errors.append(f"{prefix}:duplicate:{hyp_id}")
            seen.add(hyp_id)
        require_text(row.get("statement"), f"{row_prefix}.statement", errors)
        if row.get("authority") not in HYPOTHESIS_AUTHORITIES:
            errors.append(f"{row_prefix}.authority:invalid")
        if row.get("status") not in HYPOTHESIS_STATUSES:
            errors.append(f"{row_prefix}.status:invalid")
        require_text(row.get("source_ref"), f"{row_prefix}.source_ref", errors)


def validate_intent_seed(
    value: Any,
    errors: list[str],
    *,
    prefix: str = "intent_seed",
) -> dict[str, Any]:
    seed = require_object(value, prefix, errors, nonempty=True)
    validate_target(seed.get("target"), errors, f"{prefix}.target")
    require_list(seed.get("consumers"), f"{prefix}.consumers", errors, nonempty=True)
    if seed.get("posture") not in POSTURES:
        errors.append(f"{prefix}.posture:invalid")
    products = require_list(
        seed.get("desired_products"), f"{prefix}.desired_products", errors, nonempty=True
    )
    for product in products:
        if product not in PRODUCTS:
            errors.append(f"{prefix}.desired_products:unknown:{product}")
    require_text(
        seed.get("primary_correctness_question"),
        f"{prefix}.primary_correctness_question",
        errors,
    )
    require_text(
        seed.get("primary_risk_or_priority"),
        f"{prefix}.primary_risk_or_priority",
        errors,
    )
    validate_hypotheses(
        seed.get("user_supplied_invariant_hypotheses", []),
        errors,
        f"{prefix}.user_supplied_invariant_hypotheses",
    )
    require_list(
        seed.get("correctness_priorities"),
        f"{prefix}.correctness_priorities",
        errors,
        nonempty=True,
    )
    require_list(seed.get("non_goals"), f"{prefix}.non_goals", errors)
    for field in ("proof_bar", "compatibility_posture", "persistence_posture"):
        require_text(seed.get(field), f"{prefix}.{field}", errors)
    for field in ("skill_portfolio_requested", "enforcement_routing_requested"):
        if seed.get(field) not in BOOLISH:
            errors.append(f"{prefix}.{field}:expected-yes-or-no")
    for field in ("assumptions", "deferred_questions"):
        require_list(seed.get(field), f"{prefix}.{field}", errors)
    return seed


def validate_provisional_state(value: Any, errors: list[str], prefix: str) -> dict[str, Any]:
    state = require_object(value, prefix, errors)
    for field in (
        "repository_root",
        "repository_name",
        "branch",
        "head",
        "dirty_state",
        "tracked_diff_sha256",
        "untracked_path_digest",
        "captured_at",
    ):
        require_text(state.get(field), f"{prefix}.{field}", errors)
    return state


def validate_cdgh(
    value: Any,
    errors: list[str],
    *,
    expected_gate_id: str | None = None,
    expected_gap_ids: set[str] | None = None,
    prefix: str = "grill_handoff",
) -> dict[str, Any]:
    handoff = require_object(value, prefix, errors, nonempty=True)
    if handoff.get("handoff_version") != "CDGH-v2":
        errors.append(f"{prefix}.handoff_version:expected-CDGH-v2")
    gate_id = require_id(handoff.get("gate_id"), f"{prefix}.gate_id", errors)
    if expected_gate_id and gate_id != expected_gate_id:
        errors.append(f"{prefix}.gate_id:mismatch")
    require_text(
        handoff.get("provisional_artifact_state_digest"),
        f"{prefix}.provisional_artifact_state_digest",
        errors,
    )
    require_list(
        handoff.get("researched_fact_ids"),
        f"{prefix}.researched_fact_ids",
        errors,
    )
    gaps = require_list(
        handoff.get("material_judgment_gaps"),
        f"{prefix}.material_judgment_gaps",
        errors,
        nonempty=True,
    )
    handoff_gap_ids: set[str] = set()
    for index, raw in enumerate(gaps):
        row = require_object(raw, f"{prefix}.material_judgment_gaps[{index}]", errors)
        gap_id = require_id(
            row.get("gap_id"),
            f"{prefix}.material_judgment_gaps[{index}].gap_id",
            errors,
        )
        if gap_id:
            handoff_gap_ids.add(gap_id)
        if row.get("lane") not in LANES:
            errors.append(f"{prefix}.material_judgment_gaps[{index}].lane:invalid")
        require_text(
            row.get("question"),
            f"{prefix}.material_judgment_gaps[{index}].question",
            errors,
        )
        require_text(
            row.get("why_material"),
            f"{prefix}.material_judgment_gaps[{index}].why_material",
            errors,
        )
        require_list(
            row.get("options"),
            f"{prefix}.material_judgment_gaps[{index}].options",
            errors,
            nonempty=True,
        )
    if expected_gap_ids is not None and handoff_gap_ids != expected_gap_ids:
        errors.append(f"{prefix}.material_judgment_gaps:mismatch")
    lanes = require_list(
        handoff.get("allowed_question_lanes"),
        f"{prefix}.allowed_question_lanes",
        errors,
        nonempty=True,
    )
    for lane in lanes:
        if lane not in LANES:
            errors.append(f"{prefix}.allowed_question_lanes:invalid:{lane}")
    require_list(
        handoff.get("forbidden_questions"),
        f"{prefix}.forbidden_questions",
        errors,
        nonempty=True,
    )
    projection = require_list(
        handoff.get("closure_projection"),
        f"{prefix}.closure_projection",
        errors,
        nonempty=True,
    )
    required_projection = {
        "target",
        "consumers",
        "posture",
        "desired_products",
        "primary_correctness_question",
        "primary_risk_or_priority",
        "correctness_priorities",
        "non_goals",
        "proof_bar",
        "compatibility_posture",
        "persistence_posture",
    }
    missing = sorted(required_projection - set(projection))
    for field in missing:
        errors.append(f"{prefix}.closure_projection:missing:{field}")
    return handoff


def validate_dig(body: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if body.get("gate_version") != "DIG-v2":
        errors.append("gate_version:expected-DIG-v2")
    gate_id = require_id(body.get("gate_id"), "gate_id", errors)
    provisional = validate_provisional_state(
        body.get("provisional_artifact_state"),
        errors,
        "provisional_artifact_state",
    )

    facts = require_list(
        body.get("repository_facts_researched"),
        "repository_facts_researched",
        errors,
    )
    fact_ids: set[str] = set()
    for index, raw in enumerate(facts):
        prefix = f"repository_facts_researched[{index}]"
        row = require_object(raw, prefix, errors)
        fact_id = require_id(row.get("fact_id"), f"{prefix}.fact_id", errors)
        if fact_id:
            if fact_id in fact_ids:
                errors.append(f"repository_facts_researched:duplicate:{fact_id}")
            fact_ids.add(fact_id)
        require_text(row.get("statement"), f"{prefix}.statement", errors)
        require_text(row.get("evidence_ref"), f"{prefix}.evidence_ref", errors)
        if row.get("confidence") not in CONFIDENCE - {"unknown"}:
            errors.append(f"{prefix}.confidence:invalid")

    require_object(body.get("user_request"), "user_request", errors)
    defaults = require_list(body.get("working_defaults"), "working_defaults", errors)
    for index, raw in enumerate(defaults):
        prefix = f"working_defaults[{index}]"
        row = require_object(raw, prefix, errors)
        for field in ("field", "value", "consequence_if_wrong", "confidence"):
            require_text(row.get(field), f"{prefix}.{field}", errors)

    gaps = require_list(
        body.get("material_user_judgment_gaps"),
        "material_user_judgment_gaps",
        errors,
    )
    gap_ids: set[str] = set()
    for index, raw in enumerate(gaps):
        prefix = f"material_user_judgment_gaps[{index}]"
        row = require_object(raw, prefix, errors)
        gap_id = require_id(row.get("gap_id"), f"{prefix}.gap_id", errors)
        if gap_id:
            if gap_id in gap_ids:
                errors.append(f"material_user_judgment_gaps:duplicate:{gap_id}")
            gap_ids.add(gap_id)
        if row.get("lane") not in LANES:
            errors.append(f"{prefix}.lane:invalid")
        for field in ("question", "why_material"):
            require_text(row.get(field), f"{prefix}.{field}", errors)
        if not is_no(row.get("discoverable_from_artifacts")):
            errors.append(f"{prefix}.discoverable_from_artifacts:must-be-no")
        options = require_list(row.get("options"), f"{prefix}.options", errors, nonempty=True)
        if options and len(options) < 2:
            errors.append(f"{prefix}.options:need-at-least-two")

    grill_required = body.get("grill_required")
    if grill_required not in BOOLISH:
        errors.append("grill_required:expected-yes-or-no")
    require_text(body.get("reason"), "reason", errors)
    gate = require_object(body.get("gate"), "gate", errors)
    may_proceed = gate.get("doctrine_may_proceed")
    if may_proceed not in BOOLISH:
        errors.append("gate.doctrine_may_proceed:expected-yes-or-no")

    if is_yes(grill_required):
        if not gaps:
            errors.append("grill_required:requires-material-gaps")
        validate_cdgh(
            body.get("grill_handoff"),
            errors,
            expected_gate_id=gate_id or None,
            expected_gap_ids=gap_ids,
        )
        if is_yes(may_proceed):
            errors.append("gate.doctrine_may_proceed:must-be-no-before-grill")
        if body.get("direct_intent_seed") not in (None, {}):
            errors.append("direct_intent_seed:must-be-null-when-grill-required")
    elif is_no(grill_required):
        if gaps:
            errors.append("grill_not_required:material-gaps-must-be-empty")
        validate_intent_seed(body.get("direct_intent_seed"), errors)
        if not is_yes(may_proceed):
            errors.append("gate.doctrine_may_proceed:must-be-yes")
        if body.get("grill_handoff") not in (None, {}):
            errors.append("grill_handoff:must-be-null-when-direct")

    if provisional:
        expected_digest = sha256_digest(provisional)
        if body.get("provisional_artifact_state_digest") != expected_digest:
            errors.append("provisional_artifact_state_digest:mismatch")


def validate_grill(
    body: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    *,
    require_plan: bool,
) -> None:
    required = (
        "goal",
        "problem_layer",
        "target_user_or_maintainer",
        "scope",
        "non_goals",
        "success_criteria",
        "proof_bar",
        "compatibility_posture",
        "lane_status",
    )
    for field in required:
        if body.get(field) in (None, "", [], {}):
            errors.append(f"grill_decision_packet.{field}:missing")
    if body.get("plan_allowed") not in {True, False}:
        errors.append("grill_decision_packet.plan_allowed:must-be-boolean")
    if require_plan and body.get("plan_allowed") is not True:
        errors.append("grill_decision_packet.plan_allowed:not-true")
    for field in ("open_questions", "deferred_questions", "default_assumptions"):
        require_list(body.get(field), f"grill_decision_packet.{field}", errors)

    closure = require_object(
        body.get("codebase_doctrine_closure"),
        "grill_decision_packet.codebase_doctrine_closure",
        errors,
        nonempty=True,
    )
    require_id(
        closure.get("source_gate_id"),
        "grill_decision_packet.codebase_doctrine_closure.source_gate_id",
        errors,
    )
    require_text(
        closure.get("source_handoff_digest"),
        "grill_decision_packet.codebase_doctrine_closure.source_handoff_digest",
        errors,
    )
    resolved = require_list(
        closure.get("resolved_gap_ids"),
        "grill_decision_packet.codebase_doctrine_closure.resolved_gap_ids",
        errors,
    )
    deferred = require_list(
        closure.get("deferred_gap_ids"),
        "grill_decision_packet.codebase_doctrine_closure.deferred_gap_ids",
        errors,
    )
    if set(resolved) & set(deferred):
        errors.append("grill_decision_packet.codebase_doctrine_closure:gap-overlap")
    validate_intent_seed(
        closure.get("doctrine_projection"),
        errors,
        prefix="grill_decision_packet.codebase_doctrine_closure.doctrine_projection",
    )
    if body.get("plan_allowed") is True and deferred:
        errors.append("grill_decision_packet.plan_allowed:deferred-material-gaps")


def validate_cdi(body: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if body.get("intent_version") != "CDI-v2":
        errors.append("intent_version:expected-CDI-v2")
    intent_id = require_id(body.get("intent_id"), "intent_id", errors)
    source = require_object(body.get("source"), "source", errors)
    if source.get("kind") not in SOURCES:
        errors.append("source.kind:invalid")
    for field in ("intent_gate_id", "intent_gate_digest"):
        require_text(source.get(field), f"source.{field}", errors)
    if source.get("kind") == "grill":
        require_text(source.get("grill_packet_digest"), "source.grill_packet_digest", errors)
    elif source.get("grill_packet_digest") not in (None, ""):
        warnings.append("source.grill_packet_digest:ignored-for-non-grill")

    seed_view = {
        key: body.get(key)
        for key in (
            "target",
            "consumers",
            "posture",
            "desired_products",
            "primary_correctness_question",
            "primary_risk_or_priority",
            "user_supplied_invariant_hypotheses",
            "correctness_priorities",
            "non_goals",
            "proof_bar",
            "compatibility_posture",
            "persistence_posture",
            "skill_portfolio_requested",
            "enforcement_routing_requested",
            "assumptions",
            "deferred_questions",
        )
    }
    validate_intent_seed(seed_view, errors, prefix="intent")
    if not is_yes(body.get("doctrine_allowed")):
        errors.append("doctrine_allowed:not-yes")
    if intent_id:
        expected = expected_intent_id(body)
        if intent_id != expected:
            errors.append(f"intent_id:mismatch:{intent_id}:{expected}")


def validate_value(
    value: dict[str, Any],
    *,
    kind: str = "auto",
    require_plan: bool = False,
) -> tuple[str, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    selected = kind
    if selected == "auto":
        if "doctrine_intent_gate" in value:
            selected = "dig"
        elif "codebase_doctrine_intent" in value:
            selected = "cdi"
        elif "codebase_doctrine_grill_handoff" in value:
            selected = "cdgh"
        elif "grill_decision_packet" in value:
            selected = "grill"
        else:
            errors.append("wrapper:unknown")
            return selected, errors, warnings

    if selected == "dig":
        validate_dig(unwrap(value, "doctrine_intent_gate"), errors, warnings)
    elif selected == "cdi":
        validate_cdi(unwrap(value, "codebase_doctrine_intent"), errors, warnings)
    elif selected == "cdgh":
        validate_cdgh(unwrap(value, "codebase_doctrine_grill_handoff"), errors)
    elif selected == "grill":
        validate_grill(
            unwrap(value, "grill_decision_packet"),
            errors,
            warnings,
            require_plan=require_plan,
        )
    else:
        errors.append(f"kind:unsupported:{selected}")
    return selected, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument(
        "--kind",
        choices=("auto", "dig", "cdi", "cdgh", "grill"),
        default="auto",
    )
    parser.add_argument("--require-plan-allowed", action="store_true")
    args = parser.parse_args()
    try:
        value = load_data(args.file)
        selected, errors, warnings = validate_value(
            value,
            kind=args.kind,
            require_plan=args.require_plan_allowed,
        )
    except Exception as exc:
        selected, errors, warnings = args.kind, [str(exc)], []
    print(dump_data(report("intent_gate", errors, warnings, kind=selected), "json"), end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
