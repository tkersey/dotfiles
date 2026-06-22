#!/usr/bin/env python3
"""Validate source_governance_gate / SGG-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

GOVERNANCE_PROVENANCE = {
    "controller_invocation",
    "controller_event",
    "controller_state",
    "controller_receipt",
    "explicit_workflow_declaration",
    "artifact_under_repair",
    "filename_or_path_mention",
    "historical_reference",
    "generic_prose",
    "ambiguous",
    "absent",
}

CLOSURE_PROVENANCE = {
    "controller_close",
    "controller_receipt",
    "campaign_bound_terminal",
    "generic_delivery_closure",
    "tool_success_only",
    "generic_prose",
    "ambiguous",
    "absent",
}

CONTROLLER_GOVERNANCE = {
    "controller_invocation",
    "controller_event",
    "controller_state",
    "controller_receipt",
}

CONTROLLER_CLOSURE = {
    "controller_close",
    "controller_receipt",
    "campaign_bound_terminal",
}

INCIDENTAL = {
    "artifact_under_repair",
    "filename_or_path_mention",
    "historical_reference",
    "generic_prose",
}

VERDICTS = {
    "authoritative",
    "declared_uncontrolled",
    "incidental",
    "ambiguous",
    "absent",
}

REPLAY_ALLOWED = {"authoritative", "declared_uncontrolled"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    body = value.get("source_governance_gate", value) if isinstance(value, dict) else value
    if not isinstance(body, dict):
        raise ValueError("source_governance_gate must be an object")
    return body


def object_field(parent: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key}:must-be-object")
        return {}
    return value


def list_field(parent: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        errors.append(f"{key}:must-be-list")
        return []
    return value


def collect_evidence_ids(evidence: dict[str, Any], errors: list[str]) -> tuple[set[str], dict[str, dict[str, Any]]]:
    ids: set[str] = set()
    rows_by_id: dict[str, dict[str, Any]] = {}
    for bucket in ("governance", "entry", "closure", "incidental"):
        rows = list_field(evidence, bucket, errors)
        for index, row in enumerate(rows):
            prefix = f"evidence.{bucket}[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{prefix}:must-be-object")
                continue
            evidence_id = row.get("evidence_id")
            if not isinstance(evidence_id, str) or not evidence_id:
                errors.append(f"{prefix}.evidence_id")
                continue
            if evidence_id in ids:
                errors.append(f"evidence:duplicate-id:{evidence_id}")
            ids.add(evidence_id)
            rows_by_id[evidence_id] = row
            if row.get("present") not in {True, False}:
                errors.append(f"{prefix}.present")
            if not row.get("source"):
                errors.append(f"{prefix}.source")
            role = row.get("provenance_role")
            if bucket == "closure":
                if role not in CLOSURE_PROVENANCE:
                    errors.append(f"{prefix}.provenance_role")
            elif role not in GOVERNANCE_PROVENANCE | CLOSURE_PROVENANCE:
                errors.append(f"{prefix}.provenance_role")
            if row.get("source") == "tool":
                if not any(row.get(key) for key in ("tool_name", "executable", "command")):
                    errors.append(f"{prefix}:tool-structure-missing")
                if not row.get("matched_cue"):
                    errors.append(f"{prefix}.matched_cue")
                if not row.get("matched_field"):
                    errors.append(f"{prefix}.matched_field")
    return ids, rows_by_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    try:
        gate = load(args.file)
    except Exception as exc:
        print(json.dumps({"source_governance_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if gate.get("gate_version") != "SGG-v1":
        errors.append("gate_version")
    if not gate.get("gate_id"):
        errors.append("gate_id")

    source = object_field(gate, "source", errors)
    for key in ("session_id", "workflow", "classifier_command", "classifier_version"):
        if not source.get(key):
            errors.append(f"source.{key}")
    if not any(source.get(key) for key in ("rollout_path", "included_row_ref")):
        warnings.append("source:no-rollout-or-included-row-ref")

    evidence = object_field(gate, "evidence", errors)
    evidence_ids, rows_by_id = collect_evidence_ids(evidence, errors)

    classification = object_field(gate, "classification", errors)
    governance = classification.get("governance_provenance")
    closure = classification.get("closure_provenance")
    if governance not in GOVERNANCE_PROVENANCE:
        errors.append("classification.governance_provenance")
    if closure not in CLOSURE_PROVENANCE:
        errors.append("classification.closure_provenance")

    governing_refs = list_field(classification, "governing_evidence_refs", errors)
    incidental_refs = list_field(classification, "incidental_evidence_refs", errors)
    list_field(classification, "absent_evidence_reasons", errors)

    for field, refs in (
        ("governing_evidence_refs", governing_refs),
        ("incidental_evidence_refs", incidental_refs),
    ):
        for ref in refs:
            if ref not in evidence_ids:
                errors.append(f"classification.{field}:unknown:{ref}")

    verdict = object_field(gate, "verdict", errors)
    state = verdict.get("state")
    replay_allowed = verdict.get("replay_allowed")
    if state not in VERDICTS:
        errors.append("verdict.state")
    if replay_allowed not in {True, False}:
        errors.append("verdict.replay_allowed")
    allowed_modes = list_field(verdict, "allowed_modes", errors)
    if not verdict.get("reason"):
        errors.append("verdict.reason")
    list_field(gate, "limitations", errors)

    if state in REPLAY_ALLOWED and replay_allowed is not True:
        errors.append("verdict:replay-state-must-allow")
    if state not in REPLAY_ALLOWED and replay_allowed is not False:
        errors.append("verdict:blocked-state-must-deny")
    if replay_allowed and not allowed_modes:
        errors.append("verdict.allowed_modes:empty")
    if not replay_allowed and allowed_modes:
        warnings.append("verdict.allowed_modes:present-while-replay-denied")

    if state == "authoritative":
        if governance not in CONTROLLER_GOVERNANCE:
            errors.append("authoritative:controller-governance-required")
        if not governing_refs:
            errors.append("authoritative:governing-evidence-required")
        if closure not in CONTROLLER_CLOSURE and any(
            row.get("present") is True for row in evidence.get("closure", []) if isinstance(row, dict)
        ):
            warnings.append("authoritative:closure-not-controller-grade")

    if state == "declared_uncontrolled":
        if governance != "explicit_workflow_declaration":
            errors.append("declared_uncontrolled:explicit-declaration-required")
        if not governing_refs:
            errors.append("declared_uncontrolled:evidence-required")

    if state == "incidental":
        if governance not in INCIDENTAL:
            errors.append("incidental:incidental-provenance-required")
        if not incidental_refs:
            errors.append("incidental:incidental-evidence-required")

    if state == "ambiguous" and governance != "ambiguous":
        warnings.append("ambiguous:governance-provenance-not-ambiguous")

    if state == "absent" and governance != "absent":
        errors.append("absent:governance-provenance-must-be-absent")

    for ref in governing_refs:
        row = rows_by_id.get(ref)
        if row and row.get("present") is not True:
            errors.append(f"governing-evidence:not-present:{ref}")
    for ref in incidental_refs:
        row = rows_by_id.get(ref)
        if row and row.get("present") is not True:
            errors.append(f"incidental-evidence:not-present:{ref}")

    result = {
        "source_governance_gate": {
            "verdict": "pass" if not errors else "fail",
            "gate_id": gate.get("gate_id"),
            "state": state,
            "replay_allowed": replay_allowed,
            "governance_provenance": governance,
            "closure_provenance": closure,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
