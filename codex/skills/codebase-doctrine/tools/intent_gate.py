#!/usr/bin/env python3
"""Validate DIG-v1, CDI-v1, or a `$grill-me` decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

YES = {"yes", True}
NO = {"no", False}
LANES = {
    "target_boundary",
    "consumers",
    "posture",
    "desired_products",
    "correctness_priorities",
    "non_goals",
    "proof_bar",
    "persistence",
}
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


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        value = json.loads(text)
    else:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML intent artifacts")
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("intent artifact must be an object")
    return value


def as_list(value: Any, label: str, errors: list[str], *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{label}:must-be-list")
        return []
    if nonempty and not value:
        errors.append(f"{label}:empty")
    return value


def validate_dig(body: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if body.get("gate_version") != "DIG-v1":
        errors.append("gate_version:expected-DIG-v1")
    if not body.get("gate_id"):
        errors.append("gate_id:missing")

    provisional = body.get("provisional_artifact_state")
    if not isinstance(provisional, dict):
        errors.append("provisional_artifact_state:must-be-object")
    else:
        for field in ("repository_root", "repository_name", "head"):
            if not provisional.get(field):
                errors.append(f"provisional_artifact_state.{field}:missing")

    facts = as_list(body.get("repository_facts_researched"), "repository_facts_researched", errors)
    fact_ids: set[str] = set()
    for index, fact in enumerate(facts):
        prefix = f"repository_facts_researched[{index}]"
        if not isinstance(fact, dict):
            errors.append(f"{prefix}:must-be-object")
            continue
        fact_id = fact.get("fact_id")
        if not fact_id:
            errors.append(f"{prefix}.fact_id:missing")
        elif fact_id in fact_ids:
            errors.append(f"{prefix}.fact_id:duplicate:{fact_id}")
        else:
            fact_ids.add(str(fact_id))
        for field in ("statement", "evidence_ref", "confidence"):
            if not fact.get(field):
                errors.append(f"{prefix}.{field}:missing")

    if not isinstance(body.get("user_request"), dict):
        errors.append("user_request:must-be-object")
    as_list(body.get("working_defaults"), "working_defaults", errors)

    gaps = as_list(body.get("material_user_judgment_gaps"), "material_user_judgment_gaps", errors)
    gap_ids: set[str] = set()
    for index, gap in enumerate(gaps):
        prefix = f"material_user_judgment_gaps[{index}]"
        if not isinstance(gap, dict):
            errors.append(f"{prefix}:must-be-object")
            continue
        gap_id = gap.get("gap_id")
        if not gap_id:
            errors.append(f"{prefix}.gap_id:missing")
        elif gap_id in gap_ids:
            errors.append(f"{prefix}.gap_id:duplicate:{gap_id}")
        else:
            gap_ids.add(str(gap_id))
        if gap.get("lane") not in LANES:
            errors.append(f"{prefix}.lane:invalid")
        for field in ("question", "why_material"):
            if not gap.get(field):
                errors.append(f"{prefix}.{field}:missing")
        if gap.get("discoverable_from_artifacts") not in NO:
            errors.append(f"{prefix}.discoverable_from_artifacts:must-be-no")
        options = as_list(gap.get("options"), f"{prefix}.options", errors, nonempty=True)
        if options and len(options) < 2:
            errors.append(f"{prefix}.options:need-at-least-two")

    grill_required = body.get("grill_required")
    if grill_required not in YES | NO:
        errors.append("grill_required:expected-yes-or-no")
    if not body.get("reason"):
        errors.append("reason:missing")

    gate = body.get("gate")
    if not isinstance(gate, dict):
        errors.append("gate:must-be-object")
        may_proceed = None
    else:
        may_proceed = gate.get("doctrine_may_proceed")
        if may_proceed not in YES | NO:
            errors.append("gate.doctrine_may_proceed:expected-yes-or-no")

    if grill_required in YES:
        if not gaps:
            errors.append("grill_required:requires-material-gaps")
        handoff = body.get("grill_handoff")
        if not isinstance(handoff, dict) or not handoff:
            errors.append("grill_handoff:required")
        elif handoff.get("handoff_version") != "CDGH-v1":
            errors.append("grill_handoff.handoff_version:expected-CDGH-v1")
        if may_proceed in YES:
            errors.append("gate.doctrine_may_proceed:must-be-no-before-grill")
    elif grill_required in NO:
        if gaps:
            errors.append("grill_not_required:material-gaps-must-be-empty")
        candidate = body.get("direct_intent_candidate")
        if not isinstance(candidate, dict) or not candidate:
            errors.append("direct_intent_candidate:required")
        if may_proceed not in YES:
            errors.append("gate.doctrine_may_proceed:must-be-yes")


def validate_cdi(body: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if body.get("intent_version") != "CDI-v1":
        errors.append("intent_version:expected-CDI-v1")
    if not body.get("intent_id"):
        errors.append("intent_id:missing")

    source = body.get("source")
    if not isinstance(source, dict):
        errors.append("source:must-be-object")
        source = {}
    if source.get("kind") not in SOURCES:
        errors.append("source.kind:invalid")
    if not source.get("intent_gate_id"):
        errors.append("source.intent_gate_id:missing")
    if source.get("kind") == "grill" and not source.get("grill_packet_digest"):
        errors.append("source.grill_packet_digest:required-for-grill")

    target = body.get("target")
    if not isinstance(target, dict):
        errors.append("target:must-be-object")
        target = {}
    for field in ("repository", "boundary_statement"):
        if not target.get(field):
            errors.append(f"target.{field}:missing")
    for field in ("included_subsystems", "excluded_subsystems", "cross_cutting_flows"):
        as_list(target.get(field), f"target.{field}", errors)

    as_list(body.get("consumers"), "consumers", errors, nonempty=True)
    if body.get("posture") not in POSTURES:
        errors.append("posture:invalid")
    products = as_list(body.get("desired_products"), "desired_products", errors, nonempty=True)
    for product in products:
        if product not in PRODUCTS:
            warnings.append(f"desired_products:unknown:{product}")
    if not body.get("primary_invariant"):
        errors.append("primary_invariant:missing")
    as_list(body.get("correctness_priorities"), "correctness_priorities", errors, nonempty=True)
    as_list(body.get("non_goals"), "non_goals", errors)
    for field in ("proof_bar", "compatibility_posture", "persistence_posture"):
        if not body.get(field):
            errors.append(f"{field}:missing")
    for field in ("skill_portfolio_requested", "enforcement_routing_requested", "doctrine_allowed"):
        if body.get(field) not in YES | NO:
            errors.append(f"{field}:expected-yes-or-no")
    as_list(body.get("assumptions"), "assumptions", errors)
    as_list(body.get("deferred_questions"), "deferred_questions", errors)


def validate_grill(body: dict[str, Any], errors: list[str], warnings: list[str], require_plan: bool) -> None:
    required = (
        "goal",
        "problem_layer",
        "target_user_or_maintainer",
        "scope",
        "non_goals",
        "primary_invariant",
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
        if not isinstance(body.get(field), list):
            errors.append(f"grill_decision_packet.{field}:must-be-list")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--kind", choices=("auto", "dig", "cdi", "grill"), default="auto")
    parser.add_argument("--require-plan-allowed", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        value = load(args.file)
    except Exception as exc:
        print(json.dumps({"intent_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    kind = args.kind
    if kind == "auto":
        if "doctrine_intent_gate" in value:
            kind = "dig"
        elif "codebase_doctrine_intent" in value:
            kind = "cdi"
        elif "grill_decision_packet" in value:
            kind = "grill"
        else:
            errors.append("wrapper:unknown")

    if kind == "dig":
        body = value.get("doctrine_intent_gate", value)
        if not isinstance(body, dict):
            errors.append("doctrine_intent_gate:must-be-object")
        else:
            validate_dig(body, errors, warnings)
    elif kind == "cdi":
        body = value.get("codebase_doctrine_intent", value)
        if not isinstance(body, dict):
            errors.append("codebase_doctrine_intent:must-be-object")
        else:
            validate_cdi(body, errors, warnings)
    elif kind == "grill":
        body = value.get("grill_decision_packet", value)
        if not isinstance(body, dict):
            errors.append("grill_decision_packet:must-be-object")
        else:
            validate_grill(body, errors, warnings, args.require_plan_allowed)

    result = {
        "intent_gate": {
            "verdict": "pass" if not errors else "fail",
            "kind": kind,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
