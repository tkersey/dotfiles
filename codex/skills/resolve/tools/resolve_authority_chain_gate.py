#!/usr/bin/env python3
"""Validate resolve_authority_chain / RAC-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


IN_HORIZON_RELATIONS = {
    "directly_entailed",
    "compatibility_required",
    "forbidden_state_witness",
}
MUTATION_LIABILITIES = {
    "introduced_by_current_diff",
    "exposed_and_required_by_current_acceptance",
    "preexisting_but_blocks_current_invariant",
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
    "ceb_class_not_accepted",
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
        elif "resolve_authority_chain:" in text:
            value = load_simple_yaml(text)
        else:
            raise UnsupportedFormat("unsupported RAC format")
    except (json.JSONDecodeError, ValueError) as exc:
        raise UnsupportedFormat(str(exc)) from exc

    if not isinstance(value, dict):
        raise UnsupportedFormat("document must be an object")
    body = value.get("resolve_authority_chain")
    if not isinstance(body, dict):
        raise UnsupportedFormat("resolve_authority_chain must be an object")
    return body


def strip_comment(value: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(value):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return value[:index].rstrip()
    return value.strip()


def yaml_scalar(value: str) -> Any:
    value = strip_comment(value)
    if value == "[]":
        return []
    if value in {"true", "yes"}:
        return True
    if value in {"false", "no"}:
        return False
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_simple_yaml(text: str) -> dict[str, Any]:
    rows: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        rows.append((indent, strip_comment(raw.strip())))
    if not rows:
        raise ValueError("empty YAML document")

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(rows):
            return {}, index
        if rows[index][1].startswith("- "):
            out: list[Any] = []
            while index < len(rows) and rows[index][0] == indent and rows[index][1].startswith("- "):
                out.append(yaml_scalar(rows[index][1][2:].strip()))
                index += 1
            return out, index

        out: dict[str, Any] = {}
        while index < len(rows):
            row_indent, content = rows[index]
            if row_indent < indent:
                break
            if row_indent > indent:
                raise ValueError("unexpected YAML indentation")
            if content.startswith("- "):
                break
            key, sep, raw_value = content.partition(":")
            if not sep:
                raise ValueError("unsupported YAML row")
            key = key.strip()
            raw_value = raw_value.strip()
            index += 1
            if raw_value:
                out[key] = yaml_scalar(raw_value)
            elif index < len(rows) and rows[index][0] > row_indent:
                out[key], index = parse_block(index, rows[index][0])
            else:
                out[key] = {}
        return out, index

    value, index = parse_block(0, rows[0][0])
    if index != len(rows) or not isinstance(value, dict):
        raise ValueError("unsupported YAML document")
    return value


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


def string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and bool(item) for item in value)


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
        "review_claim_present": all_strings(review_claim, ("claim_id", "source", "statement")),
        "acceptance_contract_present": all_strings(
            acceptance,
            ("contract_id", "contract_fingerprint"),
        ),
        "horizon_present": isinstance(acceptance.get("horizon_fingerprint"), str) and bool(acceptance["horizon_fingerprint"]),
        "law_refs_present": string_list(law_refs),
        "relation": scalar(acceptance.get("relation")),
        "cex_confirmed": (
            adjudication.get("validity") == "confirmed"
            and adjudication.get("disposition") == "accepted"
            and scalar(adjudication.get("liability")) in MUTATION_LIABILITIES
            and adjudication.get("novelty") == "new_equivalence_class"
            and all_strings(adjudication, ("cex_id", "minimal_trace_ref"))
        ),
        "adjudication_disposition": scalar(adjudication.get("disposition")),
        "batch_sealed": bool_field(batch, "sealed") is True and all_strings(batch, ("batch_id",)) and scalar(batch.get("mode")) in {"discovery", "conformance"},
        "ceb_class_present": all_strings(
            compression,
            ("ceb_id", "class_id", "class_status", "quotient_witness_ref"),
        ),
        "ceb_class_accepted": compression.get("class_status") == "accepted",
        "mbk_present": isinstance(compression.get("mbk_id"), str) and bool(compression["mbk_id"]),
        "rc_present": isinstance(compression.get("rc_id"), str) and bool(compression["rc_id"]),
        "transition_present": isinstance(compression.get("transition_ref"), str) and bool(compression["transition_ref"]),
        "proof_obligation_present": isinstance(compression.get("proof_obligation_ref"), str) and bool(compression["proof_obligation_ref"]),
        "realization_allowed": bool_field(realization, "allowed") is True and all_strings(realization, ("target_owner", "target_boundary")),
        "gate_current_yes": yes(gate, "current_artifact_state"),
        "gate_complete_yes": yes(gate, "complete_chain"),
        "gate_mutation_yes": yes(gate, "mutation_allowed"),
    }


def validate(items: dict[str, Any]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    violations: list[str] = []

    if not items["chain_version_ok"]:
        missing.append("missing_chain_version")
    if not items["chain_id"] or not items["campaign_id"]:
        missing.append("missing_chain_identity")
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
    elif not items["ceb_class_accepted"]:
        violations.append("ceb_class_not_accepted")
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
    if not items["gate_complete_yes"]:
        violations.append("incomplete_chain")
    if (items["realization_allowed"] and not items["gate_mutation_yes"]) or (
        not items["realization_allowed"] and items["gate_mutation_yes"]
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
