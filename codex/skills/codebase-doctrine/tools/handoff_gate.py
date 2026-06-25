#!/usr/bin/env -S uv run --with pyyaml python
"""Validate CBSH-v2 against its source CBD-v2 and explicit user authorization."""

from __future__ import annotations

import argparse
from pathlib import PurePosixPath
from typing import Any

from common import (
    dump_data,
    is_yes,
    load_data,
    report,
    require_list,
    require_object,
    require_text,
    unwrap,
)
from doctrine_gate import validate_value as validate_doctrine_value


def find_candidate(doctrine: dict[str, Any], candidate_id: str) -> dict[str, Any] | None:
    root = doctrine.get("repository_root_skill")
    if isinstance(root, dict) and root.get("candidate_id") == candidate_id:
        return root
    for candidate in doctrine.get("focused_skill_candidates", []):
        if isinstance(candidate, dict) and candidate.get("candidate_id") == candidate_id:
            return candidate
    return None


def validate_handoff(
    handoff_value: dict[str, Any],
    doctrine_value: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    doctrine_errors, doctrine_warnings, _counts = validate_doctrine_value(doctrine_value)
    if doctrine_errors:
        errors.append("source_doctrine:invalid")
        errors.extend(f"source_doctrine:{item}" for item in doctrine_errors)
    warnings.extend(f"source_doctrine:{item}" for item in doctrine_warnings)
    doctrine = unwrap(doctrine_value, "codebase_doctrine")
    handoff = unwrap(handoff_value, "codebase_skill_handoff")
    if handoff.get("handoff_version") != "CBSH-v2":
        errors.append("handoff_version:expected-CBSH-v2")
    for field in (
        "doctrine_id",
        "intent_id",
        "artifact_state_id",
        "candidate_id",
        "candidate_status",
        "proposed_name",
        "allowed_package",
    ):
        require_text(handoff.get(field), field, errors)

    if handoff.get("doctrine_id") != doctrine.get("doctrine_id"):
        errors.append("doctrine_id:mismatch")
    intent = unwrap(doctrine.get("intent", {}), "codebase_doctrine_intent")
    if handoff.get("intent_id") != intent.get("intent_id"):
        errors.append("intent_id:mismatch")
    state = doctrine.get("artifact_state", {})
    if handoff.get("artifact_state_id") != state.get("artifact_state_id"):
        errors.append("artifact_state_id:mismatch")

    candidate = find_candidate(doctrine, str(handoff.get("candidate_id", "")))
    if candidate is None:
        errors.append("candidate_id:not-found")
    else:
        if candidate.get("status") not in {"recommended_for_trial", "accepted"}:
            errors.append("candidate:status-not-creatable")
        if handoff.get("candidate_status") != candidate.get("status"):
            errors.append("candidate_status:mismatch")
        if handoff.get("proposed_name") != candidate.get("proposed_name"):
            errors.append("proposed_name:mismatch")
        candidate_laws = set(candidate.get("governing_law_ids", []))
        handoff_laws = set(
            require_list(
                handoff.get("governing_law_ids"),
                "governing_law_ids",
                errors,
                nonempty=True,
            )
        )
        if candidate_laws != handoff_laws:
            errors.append("governing_law_ids:mismatch")
        for field in (
            "trigger_examples",
            "non_triggers",
            "consequential_decisions",
            "prohibited_route_ids",
            "required_artifacts",
            "success_signals",
            "failure_signals",
        ):
            expected = candidate.get(field, [])
            actual = require_list(handoff.get(field), field, errors)
            if actual != expected:
                errors.append(f"{field}:candidate-mismatch")

    authorization = require_object(
        handoff.get("explicit_user_authorization"),
        "explicit_user_authorization",
        errors,
    )
    if not is_yes(authorization.get("authorized")):
        errors.append("explicit_user_authorization.authorized:not-yes")
    require_text(
        authorization.get("source_ref"),
        "explicit_user_authorization.source_ref",
        errors,
    )
    require_text(
        authorization.get("authorized_scope"),
        "explicit_user_authorization.authorized_scope",
        errors,
    )
    require_text(
        authorization.get("authorized_at"),
        "explicit_user_authorization.authorized_at",
        errors,
    )

    allowed_package = str(handoff.get("allowed_package", ""))
    path = PurePosixPath(allowed_package)
    if path.is_absolute() or ".." in path.parts:
        errors.append("allowed_package:unsafe")
    if tuple(path.parts[:2]) != ("codex", "skills"):
        errors.append("allowed_package:must-be-under-codex-skills")
    if candidate and path.name != candidate.get("proposed_name"):
        errors.append("allowed_package:name-mismatch")

    protected = require_list(
        handoff.get("protected_doctrine_ids"),
        "protected_doctrine_ids",
        errors,
        nonempty=True,
    )
    known_ids: set[str] = set()
    for section, key in (
        ("governing_laws", "law_id"),
        ("owned_invariants", "invariant_id"),
        ("boundary_rules", "boundary_rule_id"),
        ("negative_routes", "route_id"),
    ):
        for row in doctrine.get(section, []):
            if isinstance(row, dict) and row.get(key):
                known_ids.add(row[key])
    for row in doctrine.get("authority_map", {}).get("authorities", []):
        if isinstance(row, dict) and row.get("authority_id"):
            known_ids.add(row["authority_id"])
    for value in protected:
        if value not in known_ids:
            errors.append(f"protected_doctrine_ids:unknown:{value}")

    require_list(handoff.get("validation"), "validation", errors, nonempty=True)
    require_list(
        handoff.get("future_evaluation"),
        "future_evaluation",
        errors,
        nonempty=True,
    )
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("handoff")
    parser.add_argument("--doctrine", required=True)
    args = parser.parse_args()
    try:
        errors, warnings = validate_handoff(
            load_data(args.handoff),
            load_data(args.doctrine),
        )
    except Exception as exc:
        errors, warnings = [str(exc)], []
    print(dump_data(report("handoff_gate", errors, warnings), "json"), end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
