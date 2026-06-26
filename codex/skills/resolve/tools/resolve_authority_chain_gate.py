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
    if "resolve_authority_chain" not in data:
        raise ValueError("missing resolve_authority_chain wrapper")
    value = data["resolve_authority_chain"]
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
        return any(present(item) for item in value)
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

    if any(item.startswith("artifact_state.") for item in missing):
        missing.append("missing_artifact_state")
    if "chain_id" in missing or "campaign_id" in missing:
        missing.append("missing_chain_identity")
    if any(item.startswith("review_claim.") for item in missing):
        missing.append("missing_review_claim")
    if "acceptance.horizon_fingerprint" in missing:
        missing.append("missing_horizon")
    if "acceptance.law_refs" in missing:
        missing.append("missing_law_refs")
    if "compression.class_id" in missing:
        missing.append("missing_ceb_class")
    if "compression.mbk_id" in missing or "compression.rc_id" in missing:
        missing.append("missing_mbk_or_rc")
    if "compression.transition_ref" in missing:
        missing.append("missing_transition")
    if "compression.proof_obligation_ref" in missing:
        missing.append("missing_proof_obligation")

    if get(chain, "chain_version") != "RAC-v1":
        violations.append("missing_chain_version")

    relation = str(get(chain, "acceptance.relation", "")).strip()
    validity = str(get(chain, "adjudication.validity", "")).strip()

    if relation and relation not in IN_HORIZON_RELATIONS and relation not in NON_MUTATING_RELATIONS:
        violations.append(f"unknown_acceptance_relation:{relation}")
    if relation in {"unknown", "unrelated", "rejected"}:
        violations.append("unrelated_or_rejected")
    if relation in NON_MUTATING_RELATIONS:
        violations.append("outside_horizon")

    gate_mutation_allowed = truthy(get(chain, "gate.mutation_allowed"))

    if gate_mutation_allowed and validity != "confirmed":
        violations.append(f"cex_not_confirmed:{validity or 'missing'}")
    if relation in {"unknown", "unrelated", "rejected"} and validity != "confirmed":
        violations.append("invalid_cex")

    if not truthy(get(chain, "batch.sealed")):
        violations.append("unsealed_batch")

    if not truthy(get(chain, "gate.current_artifact_state")):
        violations.append("artifact_state_stale")

    if not truthy(get(chain, "gate.complete_chain")):
        violations.append("gate_complete_chain_no")
        violations.append("incomplete_chain")
    if relation in {"unknown", "unrelated", "rejected"}:
        violations.append("realization_not_allowed")

    mutation_violations: List[str] = []
    if gate_mutation_allowed:
        if relation not in IN_HORIZON_RELATIONS:
            mutation_violations.append(f"non_mutating_relation:{relation or 'missing'}")
        if str(get(chain, "compression.class_status", "")).strip() != "accepted":
            mutation_violations.append("ceb_class_not_accepted")
        if str(get(chain, "adjudication.disposition", "")).strip() not in {"enter_kernel", "accepted"}:
            mutation_violations.append("cex_disposition_not_mutating")
            mutation_violations.append("invalid_cex")
        if str(get(chain, "adjudication.liability", "")).strip() not in {
            "introduced_by_current_diff",
            "exposed_and_required_by_current_acceptance",
            "preexisting_but_blocks_current_invariant",
        }:
            mutation_violations.append("cex_liability_not_current")
        if str(get(chain, "adjudication.novelty", "")).strip() not in {
            "new_equivalence_class",
            "new_witness_existing_class",
        }:
            mutation_violations.append("cex_not_novel")
        if str(get(chain, "batch.mode", "")).strip() == "terminal_holdout":
            mutation_violations.append("terminal_holdout_not_mutation_authority")
            mutation_violations.append("unsealed_batch")
        if not truthy(get(chain, "realization.allowed")):
            mutation_violations.append("realization_not_allowed")
        if relation in NON_MUTATING_RELATIONS:
            mutation_violations.append("realization_not_allowed")
    violations.extend(mutation_violations)

    status = "valid" if not missing and not violations else "invalid"
    mutation_allowed = status == "valid" and gate_mutation_allowed and relation in IN_HORIZON_RELATIONS

    return {
        "status": status,
        "mutation_allowed": mutation_allowed,
        "missing": missing,
        "violations": violations,
        "chain_id": get(chain, "chain_id"),
        "campaign_id": get(chain, "campaign_id"),
    }


def format_text(result: Dict[str, Any]) -> str:
    lines = []
    if result["status"] == "valid":
        lines.append("RAC-v1 valid")
    lines.extend([
        f"status: {result['status']}",
        f"mutation_allowed={str(result['mutation_allowed']).lower()}",
        f"chain_id: {result.get('chain_id')}",
        f"campaign_id: {result.get('campaign_id')}",
    ])
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
    parser.add_argument("--format", choices=["text", "json"], default="json")
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
