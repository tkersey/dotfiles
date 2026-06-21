#!/usr/bin/env python3
"""Validate codebase_doctrine / CBD-v1 and its key relational gates."""

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
YES = {"yes", True}
NO = {"no", False}
INTENT_POSTURES = {"descriptive", "prescriptive", "gap_analysis", "mixed"}
INTENT_SOURCES = {"direct", "grill", "prior_doctrine"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        value = json.loads(text)
    else:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML doctrine")
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("doctrine must be an object")
    body = value.get("codebase_doctrine", value)
    if not isinstance(body, dict):
        raise ValueError("codebase_doctrine must be an object")
    return body


def unique_ids(
    rows: Any,
    key: str,
    label: str,
    errors: list[str],
    *,
    required: bool = False,
) -> set[str]:
    if not isinstance(rows, list):
        errors.append(f"{label}:must-be-list")
        return set()
    if required and not rows:
        errors.append(f"{label}:empty")
    out: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{label}[{index}]:must-be-object")
            continue
        value = row.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{label}[{index}].{key}:missing")
            continue
        if value in out:
            errors.append(f"{label}:{key}:duplicate:{value}")
        out.add(value)
    return out


def list_refs(
    row: dict[str, Any],
    key: str,
    allowed: set[str],
    prefix: str,
    errors: list[str],
    *,
    allow_empty: bool = True,
) -> None:
    values = row.get(key, [])
    if not isinstance(values, list):
        errors.append(f"{prefix}.{key}:must-be-list")
        return
    if not allow_empty and not values:
        errors.append(f"{prefix}.{key}:empty")
    for value in values:
        if value not in allowed:
            errors.append(f"{prefix}.{key}:unknown:{value}")



def validate_intent(
    value: Any,
    artifact_state: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    *,
    required: bool,
) -> bool:
    if value is None:
        if required:
            errors.append("intent:missing")
        else:
            warnings.append("intent:missing-legacy")
        return False
    if not isinstance(value, dict):
        errors.append("intent:must-be-object")
        return False

    body = value.get("codebase_doctrine_intent", value)
    if not isinstance(body, dict):
        errors.append("intent.codebase_doctrine_intent:must-be-object")
        return False
    if body.get("intent_version") != "CDI-v1":
        errors.append("intent.intent_version:expected-CDI-v1")
    intent_id = body.get("intent_id")
    if not intent_id:
        errors.append("intent.intent_id:missing")
    elif artifact_state.get("intent_id") != intent_id:
        errors.append("artifact_state.intent_id:mismatch")

    source = body.get("source")
    if not isinstance(source, dict):
        errors.append("intent.source:must-be-object")
        source = {}
    if source.get("kind") not in INTENT_SOURCES:
        errors.append("intent.source.kind:invalid")
    if not source.get("intent_gate_id"):
        errors.append("intent.source.intent_gate_id:missing")
    if source.get("kind") == "grill" and not source.get("grill_packet_digest"):
        errors.append("intent.source.grill_packet_digest:required")

    target = body.get("target")
    if not isinstance(target, dict):
        errors.append("intent.target:must-be-object")
        target = {}
    for field in ("repository", "boundary_statement"):
        if not target.get(field):
            errors.append(f"intent.target.{field}:missing")
    for field in ("included_subsystems", "excluded_subsystems", "cross_cutting_flows"):
        if not isinstance(target.get(field), list):
            errors.append(f"intent.target.{field}:must-be-list")

    if not isinstance(body.get("consumers"), list) or not body.get("consumers"):
        errors.append("intent.consumers:empty")
    if body.get("posture") not in INTENT_POSTURES:
        errors.append("intent.posture:invalid")
    if not isinstance(body.get("desired_products"), list) or not body.get("desired_products"):
        errors.append("intent.desired_products:empty")
    for field in (
        "primary_invariant",
        "proof_bar",
        "compatibility_posture",
        "persistence_posture",
    ):
        if not body.get(field):
            errors.append(f"intent.{field}:missing")
    if not isinstance(body.get("correctness_priorities"), list) or not body.get("correctness_priorities"):
        errors.append("intent.correctness_priorities:empty")
    for field in ("non_goals", "assumptions", "deferred_questions"):
        if not isinstance(body.get(field), list):
            errors.append(f"intent.{field}:must-be-list")
    for field in ("skill_portfolio_requested", "enforcement_routing_requested"):
        if body.get(field) not in YES | NO:
            errors.append(f"intent.{field}:expected-yes-or-no")
    if body.get("doctrine_allowed") not in YES:
        errors.append("intent.doctrine_allowed:not-yes")
    return True

def candidacy_passes(candidacy: dict[str, Any]) -> bool:
    positive = [
        "recurring_trigger",
        "consequential_decision",
        "stable_governing_law",
        "independent_activation",
        "standalone_workflow",
        "observable_success_and_failure",
    ]
    negative = ["better_as_code", "better_as_test", "better_as_tooling", "better_as_docs"]
    return (
        all(candidacy.get(field) in YES for field in positive)
        and all(candidacy.get(field) in NO for field in negative)
        and candidacy.get("accepted") in YES
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--require-saturated", action="store_true")
    parser.add_argument("--require-intent", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    try:
        doctrine = load(args.file)
    except Exception as exc:
        print(json.dumps({"doctrine_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if doctrine.get("doctrine_version") != "CBD-v1":
        errors.append("doctrine_version")
    if not doctrine.get("doctrine_id"):
        errors.append("doctrine_id")

    artifact_state = doctrine.get("artifact_state")
    if not isinstance(artifact_state, dict):
        errors.append("artifact_state:must-be-object")
        artifact_state = {}
    if not artifact_state.get("artifact_state_id"):
        errors.append("artifact_state.artifact_state_id")

    intent_present = validate_intent(
        doctrine.get("intent"),
        artifact_state,
        errors,
        warnings,
        required=args.require_intent,
    )

    for field in [
        "request",
        "repository_fingerprint",
        "system_map",
        "authority_map",
        "behavioral_model",
        "proof_map",
        "repository_root_skill",
        "saturation",
        "confidence",
    ]:
        if doctrine.get(field) is None:
            errors.append(f"{field}:missing")

    for field in [
        "search_ledger",
        "evidence_index",
        "claims",
        "governing_laws",
        "owned_invariants",
        "boundary_rules",
        "failure_families",
        "negative_routes",
        "contradictions",
        "open_questions",
        "knowledge_routes",
        "focused_skill_candidates",
        "rejected_skill_candidates",
        "next_actions",
    ]:
        if not isinstance(doctrine.get(field), list):
            errors.append(f"{field}:must-be-list")

    evidence_ids = unique_ids(doctrine.get("evidence_index", []), "evidence_id", "evidence_index", errors)
    claim_ids = unique_ids(doctrine.get("claims", []), "claim_id", "claims", errors)
    law_ids = unique_ids(doctrine.get("governing_laws", []), "law_id", "governing_laws", errors, required=True)
    invariant_ids = unique_ids(doctrine.get("owned_invariants", []), "invariant_id", "owned_invariants", errors)
    family_ids = unique_ids(doctrine.get("failure_families", []), "family_id", "failure_families", errors)
    knowledge_ids = unique_ids(doctrine.get("knowledge_routes", []), "knowledge_id", "knowledge_routes", errors)

    authority_rows = doctrine.get("authority_map", {}).get("authorities", []) if isinstance(doctrine.get("authority_map"), dict) else []
    authority_ids = unique_ids(authority_rows, "authority_id", "authority_map.authorities", errors, required=True)

    for index, claim in enumerate(doctrine.get("claims", []) if isinstance(doctrine.get("claims"), list) else []):
        if not isinstance(claim, dict):
            continue
        list_refs(claim, "evidence_refs", evidence_ids, f"claims[{index}]", errors)
        list_refs(claim, "counterevidence_refs", evidence_ids, f"claims[{index}]", errors)

    for index, law in enumerate(doctrine.get("governing_laws", []) if isinstance(doctrine.get("governing_laws"), list) else []):
        if not isinstance(law, dict):
            continue
        prefix = f"governing_laws[{index}]"
        if law.get("owner") not in authority_ids:
            errors.append(f"{prefix}.owner:unknown:{law.get('owner')}")
        if not law.get("statement"):
            errors.append(f"{prefix}.statement")
        list_refs(law, "evidence_refs", evidence_ids, prefix, errors, allow_empty=False)
        if not law.get("counterexamples"):
            errors.append(f"{prefix}.counterexamples:empty")
        if not law.get("proof_obligations"):
            errors.append(f"{prefix}.proof_obligations:empty")

    for index, inv in enumerate(doctrine.get("owned_invariants", []) if isinstance(doctrine.get("owned_invariants"), list) else []):
        if not isinstance(inv, dict):
            continue
        prefix = f"owned_invariants[{index}]"
        if inv.get("owner") not in authority_ids:
            errors.append(f"{prefix}.owner:unknown:{inv.get('owner')}")
        for field in [
            "statement",
            "source_of_truth",
            "initialization",
            "enforcement_boundary",
            "exception_ownership",
        ]:
            if not inv.get(field):
                errors.append(f"{prefix}.{field}:missing")
        if not inv.get("preserving_transitions"):
            errors.append(f"{prefix}.preserving_transitions:empty")
        if not inv.get("violating_counterexamples"):
            errors.append(f"{prefix}.violating_counterexamples:empty")
        if not inv.get("proof_surface_ids"):
            errors.append(f"{prefix}.proof_surface_ids:empty")
        list_refs(inv, "evidence_refs", evidence_ids, prefix, errors, allow_empty=False)

    for index, family in enumerate(doctrine.get("failure_families", []) if isinstance(doctrine.get("failure_families"), list) else []):
        if not isinstance(family, dict):
            continue
        prefix = f"failure_families[{index}]"
        governing = family.get("governing_law_ids", [])
        provisional = family.get("status") == "provisional"
        if not governing and not provisional:
            errors.append(f"{prefix}.governing_law_ids:empty")
        list_refs(family, "governing_law_ids", law_ids, prefix, errors)
        list_refs(family, "evidence_refs", evidence_ids, prefix, errors, allow_empty=False)

    routed_claims: set[str] = set()
    for index, route in enumerate(doctrine.get("knowledge_routes", []) if isinstance(doctrine.get("knowledge_routes"), list) else []):
        if not isinstance(route, dict):
            continue
        prefix = f"knowledge_routes[{index}]"
        if route.get("primary_destination") not in DESTINATIONS:
            errors.append(f"{prefix}.primary_destination:invalid")
        if not route.get("reason"):
            errors.append(f"{prefix}.reason")
        refs = route.get("source_claim_ids", [])
        if not isinstance(refs, list) or not refs:
            errors.append(f"{prefix}.source_claim_ids:empty")
        else:
            for value in refs:
                if value not in claim_ids:
                    errors.append(f"{prefix}.source_claim_ids:unknown:{value}")
                else:
                    routed_claims.add(value)

    durable_claims = {
        row.get("claim_id")
        for row in doctrine.get("claims", [])
        if isinstance(row, dict) and row.get("durable") in YES
    }
    missing_routes = sorted(value for value in durable_claims if value not in routed_claims)
    if missing_routes:
        errors.append("durable_claims_unrouted:" + ",".join(missing_routes))

    root_skill = doctrine.get("repository_root_skill", {})
    if not isinstance(root_skill, dict):
        errors.append("repository_root_skill:must-be-object")
    else:
        for field in ["candidate_id", "proposed_name", "mission", "trigger_boundary", "accepted"]:
            if root_skill.get(field) in (None, ""):
                errors.append(f"repository_root_skill.{field}")

    accepted_focused = 0
    for index, candidate in enumerate(doctrine.get("focused_skill_candidates", []) if isinstance(doctrine.get("focused_skill_candidates"), list) else []):
        if not isinstance(candidate, dict):
            continue
        prefix = f"focused_skill_candidates[{index}]"
        for field in ["candidate_id", "proposed_name", "candidacy"]:
            if candidate.get(field) in (None, "", {}):
                errors.append(f"{prefix}.{field}")
        list_refs(candidate, "governing_law_ids", law_ids, prefix, errors, allow_empty=False)
        candidacy = candidate.get("candidacy", {})
        if not isinstance(candidacy, dict):
            errors.append(f"{prefix}.candidacy:must-be-object")
            continue
        accepted = candidacy.get("accepted") in YES
        if accepted:
            accepted_focused += 1
            if not candidacy_passes(candidacy):
                errors.append(f"{prefix}.candidacy:accepted-with-failed-gate")
    if accepted_focused > 5:
        errors.append(f"focused_skill_candidates:accepted-count:{accepted_focused}:max-5")

    saturation = doctrine.get("saturation", {})
    if not isinstance(saturation, dict):
        errors.append("saturation:must-be-object")
    else:
        verdict = saturation.get("verdict")
        if verdict not in SATURATION:
            errors.append("saturation.verdict")
        if args.require_saturated and verdict != "saturated":
            errors.append("saturation:not-saturated")
        if verdict == "targeted_search_required" and not saturation.get("next_targeted_queries"):
            errors.append("saturation.next_targeted_queries:empty")
        if verdict == "blocked" and not saturation.get("open_questions"):
            warnings.append("saturation.blocked_without_open_questions")

    result = {
        "doctrine_gate": {
            "verdict": "pass" if not errors else "fail",
            "counts": {
                "evidence": len(evidence_ids),
                "claims": len(claim_ids),
                "laws": len(law_ids),
                "invariants": len(invariant_ids),
                "failure_families": len(family_ids),
                "knowledge_routes": len(knowledge_ids),
                "accepted_focused_skills": accepted_focused,
                "intent_present": 1 if intent_present else 0,
            },
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
