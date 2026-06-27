#!/usr/bin/env python3
"""Validate resolve_authority_chain / RAC-v1.

Reference compatibility gate for `$resolve` v9. Native `resolve-c3` should expose
an equivalent `authority-chain check` command.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

IN_HORIZON_RELATIONS = {
    "directly_entailed",
    "compatibility_required",
    "forbidden_state_witness",
}
NON_MUTATING_RELATIONS = {
    "contract_invalidating",
    "outside_horizon",
    "unrelated",
    "unknown",
    "rejected",
}


def load_data(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    ext = os.path.splitext(path)[1].lower()
    if ext in {".yaml", ".yml"}:
        if yaml is None:
            raise ValueError("YAML input requires PyYAML; install pyyaml or pass JSON")
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if yaml is not None:
            return yaml.safe_load(text)
        raise


def unwrap(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("top-level document must be an object")
    value = data.get("resolve_authority_chain", data)
    if not isinstance(value, dict):
        raise ValueError("resolve_authority_chain must be an object")
    return value


def get(data: Dict[str, Any], dotted: str, default: Any = None) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "1", "passed", "pass", "allowed"}
    return bool(value)


def present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, list):
        return len(value) > 0
    return True


def validate(chain: Dict[str, Any]) -> Dict[str, Any]:
    missing: List[str] = []
    violations: List[str] = []

    required_paths = [
        "chain_version",
        "chain_id",
        "campaign_id",
        "artifact_state.base_sha",
        "artifact_state.head_sha",
        "artifact_state.dirty_fingerprint",
        "artifact_state.review_receipt",
        "review_claim.claim_id",
        "review_claim.source",
        "review_claim.statement",
        "acceptance.contract_id",
        "acceptance.contract_fingerprint",
        "acceptance.horizon_fingerprint",
        "acceptance.law_refs",
        "acceptance.relation",
        "adjudication.cex_id",
        "adjudication.validity",
        "adjudication.disposition",
        "adjudication.minimal_trace_ref",
        "batch.batch_id",
        "batch.sealed",
        "batch.mode",
        "compression.ceb_id",
        "compression.class_id",
        "compression.mbk_id",
        "compression.rc_id",
        "compression.transition_ref",
        "compression.proof_obligation_ref",
        "realization.allowed",
        "realization.target_owner",
        "realization.target_boundary",
        "gate.current_artifact_state",
        "gate.complete_chain",
        "gate.mutation_allowed",
    ]
    for path in required_paths:
        if not present(get(chain, path)):
            missing.append(path)

    if get(chain, "chain_version") != "RAC-v1":
        violations.append("missing_chain_version")

    relation = str(get(chain, "acceptance.relation", "")).strip()
    validity = str(get(chain, "adjudication.validity", "")).strip()

    if relation in NON_MUTATING_RELATIONS:
        violations.append(f"non_mutating_relation:{relation}")
    elif relation and relation not in IN_HORIZON_RELATIONS:
        violations.append(f"unknown_acceptance_relation:{relation}")

    if validity != "confirmed":
        violations.append(f"cex_not_confirmed:{validity or 'missing'}")

    if not truthy(get(chain, "batch.sealed")):
        violations.append("unsealed_batch")

    if not truthy(get(chain, "realization.allowed")):
        violations.append("realization_not_allowed")

    if not truthy(get(chain, "gate.current_artifact_state")):
        violations.append("artifact_state_stale")

    if not truthy(get(chain, "gate.complete_chain")):
        violations.append("gate_complete_chain_no")

    if not truthy(get(chain, "gate.mutation_allowed")):
        violations.append("gate_mutation_allowed_no")

    status = "valid" if not missing and not violations else "invalid"
    mutation_allowed = status == "valid"

    return {
        "status": status,
        "mutation_allowed": mutation_allowed,
        "missing": missing,
        "violations": violations,
        "chain_id": get(chain, "chain_id"),
        "campaign_id": get(chain, "campaign_id"),
    }


def format_text(result: Dict[str, Any]) -> str:
    lines = [
        f"status: {result['status']}",
        f"mutation_allowed: {str(result['mutation_allowed']).lower()}",
        f"chain_id: {result.get('chain_id')}",
        f"campaign_id: {result.get('campaign_id')}",
    ]
    if result["missing"]:
        lines.append("missing:")
        lines.extend(f"  - {item}" for item in result["missing"])
    if result["violations"]:
        lines.append("violations:")
        lines.extend(f"  - {item}" for item in result["violations"])
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate resolve_authority_chain / RAC-v1")
    parser.add_argument("chain", help="RAC-v1 JSON or YAML file")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    try:
        chain = unwrap(load_data(args.chain))
        result = validate(chain)
    except Exception as exc:
        result = {"status": "error", "mutation_allowed": False, "missing": [], "violations": [str(exc)]}
        if args.format == "json":
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(format_text(result), file=sys.stderr)
        return 3

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_text(result))
    return 0 if result["status"] == "valid" else 2


if __name__ == "__main__":
    raise SystemExit(main())
