#!/usr/bin/env python3
"""Validate codebase_doctrine_packet / CBDP-v1."""

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

WORKERS = {
    "codebase_cartographer",
    "authority_state_mapper",
    "behavioral_law_miner",
    "failure_forensics_analyst",
    "codebase_doctrine_proof_mapper",
    "doctrine_portfolio_skeptic",
    "search_saturation_auditor",
}

FINAL_CALLS = {"usable", "partial", "no_material_signal", "blocked"}
CONFIDENCE = {"high", "medium", "low"}

LEGACY_WORKER_RENAMES = {
    "proof_surface_mapper": "codebase_doctrine_proof_mapper",
}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        value = json.loads(text)
    else:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML packets")
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("packet must be an object")
    body = value.get("codebase_doctrine_packet", value)
    if not isinstance(body, dict):
        raise ValueError("codebase_doctrine_packet must be an object")
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--artifact-state-id")
    parser.add_argument("--scope")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    try:
        packet = load(args.file)
    except Exception as exc:
        print(json.dumps({"packet_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if packet.get("packet_version") != "CBDP-v1":
        errors.append("packet_version")
    worker = packet.get("worker")
    if worker in LEGACY_WORKER_RENAMES:
        errors.append(
            f"worker:renamed:{worker}->{LEGACY_WORKER_RENAMES[worker]}"
        )
    elif worker not in WORKERS:
        errors.append("worker")
    if not packet.get("artifact_state_id"):
        errors.append("artifact_state_id")
    if args.artifact_state_id and packet.get("artifact_state_id") != args.artifact_state_id:
        errors.append("artifact_state_id:mismatch")
    if not packet.get("scope"):
        errors.append("scope")
    if args.scope and packet.get("scope") != args.scope:
        errors.append("scope:mismatch")
    if packet.get("stale") not in {"yes", "no", True, False}:
        errors.append("stale")
    elif packet.get("stale") in {"yes", True}:
        errors.append("stale:true")
    if packet.get("final_call") not in FINAL_CALLS:
        errors.append("final_call")

    for field in [
        "evidence_lanes",
        "questions_addressed",
        "facts",
        "inferences",
        "contradictions",
        "open_questions",
    ]:
        if not isinstance(packet.get(field), list):
            errors.append(f"{field}:must-be-list")

    if not isinstance(packet.get("proposed_doctrine_updates"), dict):
        errors.append("proposed_doctrine_updates:must-be-object")

    claim_ids: set[str] = set()
    facts = packet.get("facts", []) if isinstance(packet.get("facts"), list) else []
    for index, fact in enumerate(facts):
        if not isinstance(fact, dict):
            errors.append(f"facts[{index}]:must-be-object")
            continue
        claim_id = fact.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            errors.append(f"facts[{index}].claim_id")
        elif claim_id in claim_ids:
            errors.append(f"facts:duplicate:{claim_id}")
        else:
            claim_ids.add(claim_id)
        if not fact.get("statement"):
            errors.append(f"facts[{index}].statement")
        refs = fact.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"facts[{index}].evidence_refs")
        if fact.get("confidence") not in CONFIDENCE:
            errors.append(f"facts[{index}].confidence")

    if packet.get("final_call") == "usable" and not facts:
        errors.append("usable:requires-facts")
    if packet.get("final_call") == "no_material_signal" and facts:
        warnings.append("no_material_signal:contains-facts")
    if not packet.get("questions_addressed"):
        warnings.append("questions_addressed:empty")

    result = {
        "packet_gate": {
            "verdict": "pass" if not errors else "fail",
            "worker": packet.get("worker"),
            "facts": len(facts),
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
