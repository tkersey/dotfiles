#!/usr/bin/env -S uv run --with pyyaml python
"""Validate artifact-bound Codebase Doctrine specialist packets (CBDP-v2)."""

from __future__ import annotations

import argparse
import json
from typing import Any

from common import (
    CONFIDENCE,
    EVIDENCE_LANES,
    dump_data,
    is_no,
    load_data,
    report,
    require_id,
    require_list,
    require_object,
    require_text,
    sha256_digest,
    unwrap,
)

WORKER_POLICY: dict[str, dict[str, set[str]]] = {
    "codebase_cartographer": {
        "lanes": {"guidance", "static_structure", "symbols_and_references"},
        "updates": {"repository_fingerprint", "system_map"},
    },
    "authority_state_mapper": {
        "lanes": {
            "authority_and_mutation",
            "symbols_and_references",
            "behavior_and_tests",
        },
        "updates": {"authority_map", "boundary_rules", "owned_invariant_candidates"},
    },
    "behavioral_law_miner": {
        "lanes": {"behavior_and_tests", "authority_and_mutation", "static_structure"},
        "updates": {"behavioral_model", "governing_law_candidates", "owned_invariant_candidates"},
    },
    "failure_forensics_analyst": {
        "lanes": {"history_and_forensics", "agent_history", "negative_evidence"},
        "updates": {"failure_families", "negative_route_candidates", "governing_law_candidates"},
    },
    "codebase_doctrine_proof_mapper": {
        "lanes": {"behavior_and_tests", "static_structure", "runtime"},
        "updates": {"proof_map", "knowledge_route_candidates"},
    },
    "doctrine_portfolio_skeptic": {
        "lanes": {"guidance", "behavior_and_tests", "agent_history"},
        "updates": {
            "knowledge_route_challenges",
            "repository_root_skill_challenge",
            "focused_skill_challenges",
            "rejected_skill_candidates",
        },
    },
    "search_saturation_auditor": {
        "lanes": set(EVIDENCE_LANES),
        "updates": {"saturation_challenge"},
    },
}
FINAL_CALLS = {"usable", "partial", "no_material_signal", "blocked"}
CLAIM_CLASSES = {"fact", "inference"}
LEAK_MARKERS = (
    "Echo:",
    "developer_instructions",
    "system message",
    "instruction-ack",
    "<name>",
)


def validate_assignment(
    value: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    body = unwrap(value, "codebase_doctrine_assignment")
    if body.get("assignment_version") != "CBDA-v1":
        errors.append("assignment_version:expected-CBDA-v1")
    assignment_id = require_id(body.get("assignment_id"), "assignment_id", errors)
    worker = body.get("worker")
    if worker not in WORKER_POLICY:
        errors.append(f"worker:invalid:{worker}")
    for field in ("artifact_state_id", "intent_id", "scope"):
        require_text(body.get(field), field, errors)
    questions = require_list(
        body.get("allowed_question_ids"),
        "allowed_question_ids",
        errors,
        nonempty=True,
    )
    if len(set(questions)) != len(questions):
        errors.append("allowed_question_ids:duplicate")
    lanes = require_list(
        body.get("allowed_evidence_lanes"),
        "allowed_evidence_lanes",
        errors,
        nonempty=True,
    )
    updates = require_list(
        body.get("allowed_update_keys"),
        "allowed_update_keys",
        errors,
    )
    if worker in WORKER_POLICY:
        policy = WORKER_POLICY[worker]
        for lane in lanes:
            if lane not in policy["lanes"]:
                errors.append(f"allowed_evidence_lanes:outside-worker-authority:{lane}")
        for key in updates:
            if key not in policy["updates"]:
                errors.append(f"allowed_update_keys:outside-worker-authority:{key}")
    require_text(body.get("objective"), "objective", errors)
    require_text(body.get("stop_condition"), "stop_condition", errors)
    return body, errors, warnings


def validate_packet(
    packet_value: dict[str, Any],
    assignment_value: dict[str, Any],
) -> tuple[list[str], list[str], dict[str, Any]]:
    assignment, assignment_errors, warnings = validate_assignment(assignment_value)
    errors = list(assignment_errors)
    packet = unwrap(packet_value, "codebase_doctrine_packet")
    if packet.get("packet_version") != "CBDP-v2":
        errors.append("packet_version:expected-CBDP-v2")
    worker = packet.get("worker")
    if worker not in WORKER_POLICY:
        errors.append(f"worker:invalid:{worker}")
    if worker != assignment.get("worker"):
        errors.append("worker:assignment-mismatch")
    if packet.get("assignment_id") != assignment.get("assignment_id"):
        errors.append("assignment_id:mismatch")
    if packet.get("artifact_state_id") != assignment.get("artifact_state_id"):
        errors.append("artifact_state_id:mismatch")
    if packet.get("intent_id") != assignment.get("intent_id"):
        errors.append("intent_id:mismatch")
    if packet.get("scope") != assignment.get("scope"):
        errors.append("scope:mismatch")
    if not is_no(packet.get("stale")):
        errors.append("stale:must-be-no")
    if packet.get("final_call") not in FINAL_CALLS:
        errors.append("final_call:invalid")

    lanes = require_list(packet.get("evidence_lanes"), "evidence_lanes", errors)
    allowed_lanes = set(assignment.get("allowed_evidence_lanes", []))
    for lane in lanes:
        if lane not in EVIDENCE_LANES:
            errors.append(f"evidence_lanes:invalid:{lane}")
        if lane not in allowed_lanes:
            errors.append(f"evidence_lanes:not-assigned:{lane}")

    addressed = require_list(
        packet.get("questions_addressed"),
        "questions_addressed",
        errors,
        nonempty=packet.get("final_call") in {"usable", "partial"},
    )
    allowed_questions = set(assignment.get("allowed_question_ids", []))
    for question_id in addressed:
        if question_id not in allowed_questions:
            errors.append(f"questions_addressed:not-assigned:{question_id}")

    claim_ids: set[str] = set()
    total_claims = 0
    for field, claim_class in (("facts", "fact"), ("inferences", "inference")):
        rows = require_list(packet.get(field), field, errors)
        for index, raw in enumerate(rows):
            prefix = f"{field}[{index}]"
            row = require_object(raw, prefix, errors)
            claim_id = require_id(row.get("claim_id"), f"{prefix}.claim_id", errors)
            if claim_id:
                if claim_id in claim_ids:
                    errors.append(f"claims:duplicate:{claim_id}")
                claim_ids.add(claim_id)
            if row.get("claim_class") != claim_class:
                errors.append(f"{prefix}.claim_class:expected-{claim_class}")
            require_text(row.get("statement"), f"{prefix}.statement", errors)
            require_list(row.get("evidence_refs"), f"{prefix}.evidence_refs", errors, nonempty=True)
            question_ids = require_list(
                row.get("question_ids"),
                f"{prefix}.question_ids",
                errors,
                nonempty=True,
            )
            for question_id in question_ids:
                if question_id not in allowed_questions:
                    errors.append(f"{prefix}.question_ids:not-assigned:{question_id}")
            if row.get("artifact_state_id") != assignment.get("artifact_state_id"):
                errors.append(f"{prefix}.artifact_state_id:mismatch")
            if row.get("confidence") not in CONFIDENCE:
                errors.append(f"{prefix}.confidence:invalid")
            total_claims += 1

    for field in ("contradictions", "open_questions"):
        rows = require_list(packet.get(field), field, errors)
        for index, raw in enumerate(rows):
            prefix = f"{field}[{index}]"
            row = require_object(raw, prefix, errors)
            require_text(row.get("statement"), f"{prefix}.statement", errors)
            require_list(row.get("evidence_refs"), f"{prefix}.evidence_refs", errors)
            qids = require_list(row.get("question_ids"), f"{prefix}.question_ids", errors)
            for question_id in qids:
                if question_id not in allowed_questions:
                    errors.append(f"{prefix}.question_ids:not-assigned:{question_id}")

    updates = require_object(
        packet.get("proposed_doctrine_updates"),
        "proposed_doctrine_updates",
        errors,
    )
    allowed_updates = set(assignment.get("allowed_update_keys", []))
    policy_updates = WORKER_POLICY.get(worker, {}).get("updates", set())
    for key in updates:
        if key not in allowed_updates:
            errors.append(f"proposed_doctrine_updates:not-assigned:{key}")
        if key not in policy_updates:
            errors.append(f"proposed_doctrine_updates:outside-worker-authority:{key}")

    serialized = json.dumps(packet, ensure_ascii=False)
    for marker in LEAK_MARKERS:
        if marker.lower() in serialized.lower():
            errors.append(f"wrapper-leakage:{marker}")

    if packet.get("final_call") == "usable" and total_claims == 0:
        errors.append("usable:requires-claims")
    if packet.get("final_call") == "no_material_signal" and total_claims:
        warnings.append("no_material_signal:contains-claims")

    receipt = {
        "assignment_id": assignment.get("assignment_id"),
        "worker": worker,
        "packet_digest": sha256_digest(packet),
        "final_call": packet.get("final_call"),
        "accepted": "yes" if not errors else "no",
    }
    return errors, warnings, receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet")
    parser.add_argument("--assignment", required=True)
    args = parser.parse_args()
    try:
        packet = load_data(args.packet)
        assignment = load_data(args.assignment)
        errors, warnings, receipt = validate_packet(packet, assignment)
    except Exception as exc:
        errors, warnings, receipt = [str(exc)], [], {}
    print(
        dump_data(
            report(
                "packet_gate",
                errors,
                warnings,
                receipt=receipt,
            ),
            "json",
        ),
        end="",
    )
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
