#!/usr/bin/env python3
"""Validate resolve_authority_chain / RAC-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only in stripped runtimes.
    yaml = None


IN_HORIZON_RELATIONS = {
    "directly_entailed",
    "compatibility_required",
    "forbidden_state_witness",
    "contract_invalidating",
}
NON_MUTATION_DISPOSITIONS = {
    "refuted",
    "stale",
    "outside_horizon",
    "contract_invalidating",
    "unknown",
}
NON_MUTATION_VIOLATIONS = {
    "invalid_cex",
    "realization_not_allowed",
    "mutation_gate_disagrees",
    "outside_horizon",
    "unrelated_or_rejected",
}


class UnsupportedFormat(ValueError):
    pass


def load_chain(path: str) -> dict[str, Any]:
    try:
        text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise UnsupportedFormat(str(exc)) from exc

    stripped = text.lstrip()
    if not stripped:
        raise UnsupportedFormat("empty document")

    try:
        if stripped.startswith("{"):
            value = json.loads(text)
        elif "resolve_authority_chain:" in text and yaml is not None:
            value = yaml.safe_load(text)
        else:
            raise UnsupportedFormat("unsupported RAC format")
    except (json.JSONDecodeError, yaml.YAMLError if yaml is not None else ValueError) as exc:
        raise UnsupportedFormat(str(exc)) from exc

    if not isinstance(value, dict):
        raise UnsupportedFormat("document must be an object")
    body = value.get("resolve_authority_chain", value)
    if not isinstance(body, dict):
        raise UnsupportedFormat("resolve_authority_chain must be an object")
    return body


def scalar(value: Any) -> str:
    return value if isinstance(value, str) else ""


def object_field(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    return value if isinstance(value, dict) else {}


def bool_field(parent: dict[str, Any], key: str) -> bool | None:
    value = parent.get(key)
    if isinstance(value, bool):
        return value
    if value in {"yes", "true", "pass"}:
        return True
    if value in {"no", "false", "fail"}:
        return False
    return None


def yes(parent: dict[str, Any], key: str) -> bool:
    return parent.get(key) is True or parent.get(key) == "yes"


def all_strings(parent: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(isinstance(parent.get(key), str) and parent[key] for key in keys)


def facts(chain: dict[str, Any]) -> dict[str, Any]:
    artifact_state = object_field(chain, "artifact_state")
    review_claim = object_field(chain, "review_claim")
    acceptance = object_field(chain, "acceptance")
    adjudication = object_field(chain, "adjudication")
    batch = object_field(chain, "batch")
    compression = object_field(chain, "compression")
    realization = object_field(chain, "realization")
    gate = object_field(chain, "gate")

    law_refs = acceptance.get("law_refs")
    return {
        "chain_id": scalar(chain.get("chain_id")),
        "campaign_id": scalar(chain.get("campaign_id")),
        "chain_version_ok": chain.get("chain_version") == "RAC-v1",
        "artifact_state_complete": all_strings(
            artifact_state,
            ("base_sha", "head_sha", "dirty_fingerprint", "review_receipt"),
        ),
        "review_claim_present": isinstance(review_claim.get("claim_id"), str) and bool(review_claim["claim_id"]),
        "acceptance_contract_present": all_strings(
            acceptance,
            ("contract_id", "contract_fingerprint"),
        ),
        "horizon_present": isinstance(acceptance.get("horizon_fingerprint"), str) and bool(acceptance["horizon_fingerprint"]),
        "law_refs_present": isinstance(law_refs, list) and len(law_refs) > 0,
        "relation": scalar(acceptance.get("relation")),
        "cex_confirmed": adjudication.get("validity") == "confirmed",
        "adjudication_disposition": scalar(adjudication.get("disposition")),
        "batch_sealed": bool_field(batch, "sealed") is True,
        "ceb_class_present": all_strings(
            compression,
            ("ceb_id", "class_id", "class_status", "quotient_witness_ref"),
        ),
        "mbk_present": isinstance(compression.get("mbk_id"), str) and bool(compression["mbk_id"]),
        "rc_present": isinstance(compression.get("rc_id"), str) and bool(compression["rc_id"]),
        "transition_present": isinstance(compression.get("transition_ref"), str) and bool(compression["transition_ref"]),
        "proof_obligation_present": isinstance(compression.get("proof_obligation_ref"), str) and bool(compression["proof_obligation_ref"]),
        "realization_allowed": bool_field(realization, "allowed") is True,
        "gate_current_yes": yes(gate, "current_artifact_state"),
        "gate_complete_yes": yes(gate, "complete_chain"),
        "gate_mutation_yes": yes(gate, "mutation_allowed"),
    }


def validate(items: dict[str, Any]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    violations: list[str] = []

    if not items["chain_version_ok"]:
        missing.append("missing_chain_version")
    if not items["artifact_state_complete"]:
        missing.append("missing_artifact_state")
    if not items["review_claim_present"]:
        missing.append("missing_review_claim")
    if not items["acceptance_contract_present"]:
        missing.append("missing_acceptance_contract")
    if not items["horizon_present"]:
        missing.append("missing_horizon")
    if not items["law_refs_present"]:
        missing.append("missing_law_refs")

    relation = items["relation"]
    if relation == "outside_horizon":
        violations.append("outside_horizon")
    if relation in {"unrelated", "rejected", "unknown"}:
        violations.append("unrelated_or_rejected")
    if relation and relation not in IN_HORIZON_RELATIONS and relation not in {"outside_horizon", "unrelated", "rejected", "unknown"}:
        violations.append("outside_horizon")

    if not items["cex_confirmed"]:
        violations.append("invalid_cex")
    if not items["batch_sealed"]:
        violations.append("unsealed_batch")
    if not items["ceb_class_present"]:
        missing.append("missing_ceb_class")
    if not items["mbk_present"] or not items["rc_present"]:
        missing.append("missing_mbk_or_rc")
    if not items["transition_present"]:
        missing.append("missing_transition")
    if not items["proof_obligation_present"]:
        missing.append("missing_proof_obligation")
    if not items["gate_current_yes"]:
        violations.append("artifact_state_stale")
    if not items["realization_allowed"]:
        violations.append("realization_not_allowed")
    if (
        not items["gate_complete_yes"]
        or (items["realization_allowed"] and not items["gate_mutation_yes"])
        or (not items["realization_allowed"] and items["gate_mutation_yes"])
    ):
        violations.append("mutation_gate_disagrees")

    return missing, violations


def payload(items: dict[str, Any], missing: list[str], violations: list[str]) -> tuple[dict[str, Any], bool]:
    mutation_allowed = not missing and not violations
    non_mutation_valid = (
        not items["realization_allowed"]
        and not items["gate_mutation_yes"]
        and items["adjudication_disposition"] in NON_MUTATION_DISPOSITIONS
    )
    valid = mutation_allowed or (
        non_mutation_valid
        and not missing
        and all(reason in NON_MUTATION_VIOLATIONS for reason in violations)
    )
    visible_violations = [] if valid and not mutation_allowed else violations
    return (
        {
            "status": "valid" if valid else "invalid",
            "mutation_allowed": mutation_allowed,
            "missing": missing,
            "violations": visible_violations,
            "chain_id": items["chain_id"],
            "campaign_id": items["campaign_id"],
        },
        valid,
    )


def emit_text(body: dict[str, Any]) -> None:
    print(
        f"RAC-v1 {body['status']}: chain_id={body['chain_id']} "
        f"campaign_id={body['campaign_id']} mutation_allowed={str(body['mutation_allowed']).lower()}"
    )
    if body["missing"]:
        print("missing: " + json.dumps(body["missing"], separators=(",", ":")))
    if body["violations"]:
        print("violations: " + json.dumps(body["violations"], separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("chain")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        chain = load_chain(args.chain)
    except UnsupportedFormat as exc:
        body = {
            "status": "invalid",
            "mutation_allowed": False,
            "missing": [],
            "violations": [str(exc)],
            "chain_id": "",
            "campaign_id": "",
        }
        print(json.dumps(body, indent=2, sort_keys=True))
        return 3

    items = facts(chain)
    missing, violations = validate(items)
    body, valid = payload(items, missing, violations)
    if args.format == "text":
        emit_text(body)
    else:
        print(json.dumps(body, indent=2, sort_keys=True))
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
