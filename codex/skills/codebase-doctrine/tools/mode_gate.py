#!/usr/bin/env -S uv run --with pyyaml python
"""Validate mode-specific Codebase Doctrine artifacts."""

from __future__ import annotations

import argparse
from typing import Any

from common import (
    BOOLISH,
    dump_data,
    is_yes,
    load_data,
    report,
    require_id,
    require_list,
    require_object,
    require_text,
    unwrap,
    validate_artifact_state,
)


def validate_survey(body: dict[str, Any], errors: list[str]) -> None:
    if body.get("survey_version") != "CBS-v1":
        errors.append("survey_version:expected-CBS-v1")
    require_id(body.get("survey_id"), "survey_id", errors)
    state = require_object(body.get("provisional_artifact_state"), "provisional_artifact_state", errors)
    for field in (
        "repository_root",
        "repository_name",
        "branch",
        "head",
        "dirty_state",
        "captured_at",
    ):
        require_text(state.get(field), f"provisional_artifact_state.{field}", errors)
    require_text(body.get("intent_gate_id"), "intent_gate_id", errors)
    require_object(body.get("repository_fingerprint"), "repository_fingerprint", errors, nonempty=True)
    require_object(body.get("provisional_system_map"), "provisional_system_map", errors, nonempty=True)
    require_list(body.get("evidence_refs"), "evidence_refs", errors, nonempty=True)
    require_list(body.get("exact_next_questions"), "exact_next_questions", errors, nonempty=True)
    require_list(body.get("open_user_judgments"), "open_user_judgments", errors)
    if not is_yes(body.get("no_committed_portfolio")):
        errors.append("no_committed_portfolio:must-be-yes")


def validate_portfolio(body: dict[str, Any], errors: list[str]) -> None:
    if body.get("portfolio_version") != "CBP-v1":
        errors.append("portfolio_version:expected-CBP-v1")
    require_id(body.get("portfolio_id"), "portfolio_id", errors)
    for field in ("doctrine_id", "intent_id", "artifact_state_id"):
        require_text(body.get(field), field, errors)
    require_list(
        body.get("knowledge_route_decisions"),
        "knowledge_route_decisions",
        errors,
        nonempty=True,
    )
    root = body.get("repository_root_skill_decision")
    if root is not None:
        root = require_object(root, "repository_root_skill_decision", errors)
        require_text(root.get("candidate_id"), "repository_root_skill_decision.candidate_id", errors)
        require_text(root.get("decision"), "repository_root_skill_decision.decision", errors)
        require_list(root.get("evidence_refs"), "repository_root_skill_decision.evidence_refs", errors, nonempty=True)
    focused = require_list(body.get("focused_skill_decisions"), "focused_skill_decisions", errors)
    active = 0
    for index, raw in enumerate(focused):
        prefix = f"focused_skill_decisions[{index}]"
        row = require_object(raw, prefix, errors)
        require_text(row.get("candidate_id"), f"{prefix}.candidate_id", errors)
        decision = require_text(row.get("decision"), f"{prefix}.decision", errors)
        if decision in {"recommended_for_trial", "accepted"}:
            active += 1
        require_list(row.get("evidence_refs"), f"{prefix}.evidence_refs", errors, nonempty=True)
    if active > 5:
        errors.append("focused_skill_decisions:active-count:max-5")
    require_list(body.get("rejected_skill_decisions"), "rejected_skill_decisions", errors)
    require_list(body.get("evidence_refs"), "evidence_refs", errors, nonempty=True)
    require_text(body.get("recommendation"), "recommendation", errors)


def validate_audit(body: dict[str, Any], errors: list[str]) -> None:
    if body.get("audit_version") != "CBA-v1":
        errors.append("audit_version:expected-CBA-v1")
    require_id(body.get("audit_id"), "audit_id", errors)
    for field in ("doctrine_id", "intent_id", "artifact_state_id", "audited_at"):
        require_text(body.get(field), field, errors)
    require_list(body.get("audited_surfaces"), "audited_surfaces", errors, nonempty=True)
    for field in ("conforming", "drift", "stale_guidance", "remediation"):
        require_list(body.get(field), field, errors)
    require_list(body.get("evidence_refs"), "evidence_refs", errors, nonempty=True)
    require_text(body.get("verdict"), "verdict", errors)


def validate_delta(body: dict[str, Any], errors: list[str]) -> None:
    if body.get("delta_version") != "CBDD-v1":
        errors.append("delta_version:expected-CBDD-v1")
    require_id(body.get("delta_id"), "delta_id", errors)
    for field in (
        "prior_doctrine_id",
        "prior_artifact_state_id",
        "new_artifact_state_id",
        "resulting_doctrine_id",
    ):
        require_text(body.get(field), field, errors)
    for field in (
        "changed_paths",
        "invalidated_ids",
        "retained_ids",
        "added_ids",
        "modified_ids",
        "proof_rechecks",
    ):
        require_list(body.get(field), field, errors)
    intent_drift = require_object(body.get("intent_drift"), "intent_drift", errors)
    if intent_drift.get("detected") not in BOOLISH:
        errors.append("intent_drift.detected:expected-yes-or-no")
    require_text(intent_drift.get("resolution"), "intent_drift.resolution", errors)
    sets = [
        set(body.get("invalidated_ids", [])),
        set(body.get("retained_ids", [])),
        set(body.get("added_ids", [])),
        set(body.get("modified_ids", [])),
    ]
    labels = ["invalidated", "retained", "added", "modified"]
    for i, left in enumerate(sets):
        for j in range(i + 1, len(sets)):
            overlap = sorted(left & sets[j])
            if overlap:
                errors.append(f"id-partitions:overlap:{labels[i]}:{labels[j]}:{','.join(overlap)}")


def validate_value(value: dict[str, Any], kind: str = "auto") -> tuple[str, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    selected = kind
    if selected == "auto":
        if "codebase_survey" in value:
            selected = "survey"
        elif "codebase_portfolio" in value:
            selected = "portfolio"
        elif "codebase_doctrine_audit" in value:
            selected = "audit"
        elif "codebase_doctrine_delta" in value:
            selected = "delta"
        else:
            errors.append("wrapper:unknown")
            return selected, errors, warnings
    if selected == "survey":
        validate_survey(unwrap(value, "codebase_survey"), errors)
    elif selected == "portfolio":
        validate_portfolio(unwrap(value, "codebase_portfolio"), errors)
    elif selected == "audit":
        validate_audit(unwrap(value, "codebase_doctrine_audit"), errors)
    elif selected == "delta":
        validate_delta(unwrap(value, "codebase_doctrine_delta"), errors)
    else:
        errors.append(f"kind:unsupported:{selected}")
    return selected, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument(
        "--kind",
        choices=("auto", "survey", "portfolio", "audit", "delta"),
        default="auto",
    )
    args = parser.parse_args()
    try:
        selected, errors, warnings = validate_value(load_data(args.file), args.kind)
    except Exception as exc:
        selected, errors, warnings = args.kind, [str(exc)], []
    print(dump_data(report("mode_gate", errors, warnings, kind=selected), "json"), end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
