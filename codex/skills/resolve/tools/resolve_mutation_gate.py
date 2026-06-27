#!/usr/bin/env python3
"""Fail-closed mutation gate for review-originated `$resolve` edits."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from typing import Any, Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_PATH = os.path.join(SCRIPT_DIR, "resolve_authority_chain_gate.py")

spec = importlib.util.spec_from_file_location("resolve_authority_chain_gate", AUTH_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load resolve_authority_chain_gate.py")
auth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auth)  # type: ignore[union-attr]

LEGAL_NEXT_ACTIONS = [
    "adjudicate_claim",
    "seal_or_repair_batch",
    "compile_or_repair_ceb_mbk_rc",
    "rebase_ac",
    "create_followup",
    "reject_finding",
    "block",
]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate review-originated mutation on RAC-v1 authority")
    parser.add_argument("--chain", required=True, help="RAC-v1 JSON or YAML file")
    parser.add_argument("--review-claim-id", default=None, help="expected review claim id")
    parser.add_argument("--format", choices=["text", "json"], default="json")
    args = parser.parse_args(argv)

    try:
        chain = auth.unwrap(auth.load_data(args.chain))
        if args.review_claim_id and auth.get(chain, "review_claim.claim_id") != args.review_claim_id:
            out = {
                "mutation_allowed": False,
                "status": "blocked",
                "reason": "uncompiled_review_text",
                "missing": [],
                "violations": [f"review_claim_mismatch:expected:{args.review_claim_id}"],
                "chain_id": auth.get(chain, "chain_id"),
                "campaign_id": auth.get(chain, "campaign_id"),
                "legal_next_actions": LEGAL_NEXT_ACTIONS,
            }
            print(json.dumps(out, indent=2, sort_keys=True) if args.format == "json" else text(out))
            return 2
        result = auth.validate(chain)
    except Exception as exc:
        out = {
            "mutation_allowed": False,
            "status": "error",
            "reason": "could_not_evaluate_input",
            "missing": [],
            "violations": [str(exc)],
            "legal_next_actions": LEGAL_NEXT_ACTIONS,
        }
        rendered = json.dumps(out, indent=2, sort_keys=True) if args.format == "json" else text(out)
        print(rendered, file=sys.stderr if args.format == "text" else sys.stdout)
        return 3

    allowed = result["status"] == "valid" and result["mutation_allowed"] is True
    missing = list(result.get("missing", []))
    if "missing_artifact_state" in missing:
        missing.append("artifact_state")
    if "missing_review_claim" in missing:
        missing.append("review_claim")
    if "missing_ceb_class" in missing:
        missing.append("ceb_class")
    if "missing_mbk_or_rc" in missing or "missing_transition" in missing:
        missing.append("mbk_transition")
    if "missing_proof_obligation" in missing:
        missing.append("proof_obligation")
    if result["status"] == "valid" and not allowed:
        if auth.get(chain, "adjudication.validity") != "confirmed":
            missing.append("confirmed_cex")
        if not auth.truthy(auth.get(chain, "realization.allowed")):
            missing.append("realization_allowed")
        if not auth.truthy(auth.get(chain, "gate.mutation_allowed")):
            missing.append("gate_mutation_allowed")
    out = {
        "mutation_allowed": allowed,
        "status": "passed" if allowed else "blocked",
        "reason": "compiled_review_authority" if allowed else "uncompiled_review_text",
        "missing": missing,
        "violations": result.get("violations", []),
        "chain_id": result.get("chain_id"),
        "campaign_id": result.get("campaign_id"),
        "legal_next_actions": [] if allowed else LEGAL_NEXT_ACTIONS,
    }

    print(json.dumps(out, indent=2, sort_keys=True) if args.format == "json" else text(out))
    return 0 if allowed else 2


def text(out: Dict[str, Any]) -> str:
    lines = [
        "mutation-gate passed" if out["mutation_allowed"] else "mutation-gate blocked",
        f"status: {out['status']}",
        f"mutation_allowed: {str(out['mutation_allowed']).lower()}",
    ]
    if out.get("reason"):
        lines.append(f"reason: {out['reason']}")
    if out.get("chain_id"):
        lines.append(f"chain_id: {out['chain_id']}")
    if out.get("missing"):
        lines.append("missing:")
        lines.extend(f"  - {item}" for item in out["missing"])
    if out.get("violations"):
        lines.append("violations:")
        lines.extend(f"  - {item}" for item in out["violations"])
    if out.get("legal_next_actions"):
        lines.append("legal_next_actions:")
        lines.extend(f"  - {item}" for item in out["legal_next_actions"])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
