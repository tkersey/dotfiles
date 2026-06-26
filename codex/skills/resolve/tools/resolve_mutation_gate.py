#!/usr/bin/env python3
"""Fail-closed mutation gate for resolve_authority_chain / RAC-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import resolve_authority_chain_gate as rac


LEGAL_NEXT_ACTIONS = [
    "adjudicate_claim",
    "seal_or_repair_batch",
    "compile_or_repair_ceb_mbk_rc",
    "rebase_ac",
    "create_followup",
    "reject_finding",
    "block",
]


def normalize(reason: str) -> str:
    if reason in {"missing_chain_version", "missing_chain_identity"}:
        return "rac_v1"
    if reason in {"missing_artifact_state", "artifact_state_stale"}:
        return "artifact_state"
    if reason == "missing_review_claim":
        return "review_claim"
    if reason in {
        "missing_acceptance_contract",
        "missing_horizon",
        "missing_law_refs",
        "outside_horizon",
        "unrelated_or_rejected",
    }:
        return "ac_horizon_relation"
    if reason == "invalid_cex":
        return "confirmed_cex"
    if reason == "unsealed_batch":
        return "sealed_batch"
    if reason in {"missing_ceb_class", "ceb_class_not_accepted"}:
        return "ceb_class"
    if reason in {"missing_mbk_or_rc", "missing_transition"}:
        return "mbk_transition"
    if reason == "missing_proof_obligation":
        return "proof_obligation"
    if reason == "realization_not_allowed":
        return "realization_allowed"
    if reason in {"mutation_gate_disagrees", "incomplete_chain"}:
        return "gate_mutation_allowed"
    return reason


def normalized_missing(missing: list[str], violations: list[str]) -> list[str]:
    result: list[str] = []
    for reason in [*missing, *violations]:
        item = normalize(reason)
        if item not in result:
            result.append(item)
    return result


def payload(items: dict, missing: list[str], violations: list[str]) -> dict:
    if not items["gate_mutation_yes"] and "mutation_gate_disagrees" not in violations:
        violations = [*violations, "mutation_gate_disagrees"]
    mutation_allowed = not missing and not violations
    return {
        "mutation_allowed": mutation_allowed,
        "reason": "compiled_review_authority" if mutation_allowed else "uncompiled_review_text",
        "missing": [] if mutation_allowed else normalized_missing(missing, violations),
        "legal_next_actions": [] if mutation_allowed else LEGAL_NEXT_ACTIONS,
        "chain_id": items["chain_id"],
        "campaign_id": items["campaign_id"],
    }


def emit_text(body: dict) -> None:
    state = "allowed" if body["mutation_allowed"] else "blocked"
    print(
        f"mutation-gate {state}: chain_id={body['chain_id']} "
        f"campaign_id={body['campaign_id']} mutation_allowed={str(body['mutation_allowed']).lower()}"
    )
    if not body["mutation_allowed"]:
        print(f"reason: {body['reason']}")
        print("missing: " + json.dumps(body["missing"], separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chain", required=True)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        chain = rac.load_chain(args.chain)
    except rac.UnsupportedFormat as exc:
        body = {
            "mutation_allowed": False,
            "reason": "could_not_evaluate_input",
            "missing": [],
            "legal_next_actions": ["block"],
            "error": str(exc),
        }
        print(json.dumps(body, indent=2, sort_keys=True))
        return 3

    items = rac.facts(chain)
    missing, violations = rac.validate(items)
    body = payload(items, missing, violations)
    if args.format == "text":
        emit_text(body)
    else:
        print(json.dumps(body, indent=2, sort_keys=True))
    return 0 if body["mutation_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
