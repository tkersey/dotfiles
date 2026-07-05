#!/usr/bin/env -S uv run python
"""RF-v1.3 receipt validator for $review-fold.

The gate validates JSON projections of full RF-v1.3 receipts and compact
RF-v1.3 receipts. It intentionally avoids review-backend policy: source fields
are evidence references, not validity or mutation authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


VALID_BACKENDS = {
    "cas",
    "github-comments",
    "human-review",
    "prior-artifact",
    "local-audit",
    "other",
    "unknown",
}
VALID_VALIDITY = {"valid", "invalid", "unproven", "needs-owner"}
VALID_LIABILITY = {
    "blocks-goal",
    "regression-risk",
    "style",
    "new-requirement",
    "out-of-scope",
    "proof-gap",
    "misuse-hazard",
    "invariant-gap",
    "complexity-stall",
}
VALID_INTENT = {"core", "adjacent", "unrelated", "expands-scope"}
VALID_DISPOSITIONS = {
    "reject",
    "proof-only",
    "minimal-fix",
    "refactor-kernel",
    "ask-human",
    "follow-up",
    "blocked",
}
VALID_REPAIR = {
    "none",
    "proof-only",
    "minimal-fix",
    "refactor-kernel",
    "branch-race",
    "ask-human",
    "follow-up",
    "blocked",
}
CODE_CHANGE_DISPOSITIONS = {"minimal-fix", "refactor-kernel"}
MATERIAL_DISPOSITIONS = VALID_DISPOSITIONS
VALID_CLEAN = {"yes", "no", "not-applicable"}
VALID_COUNT_EFFECT = {"increment", "reset", "none", "blocked", "unknown"}


class ReceiptGateError(ValueError):
    pass


def load_json(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ReceiptGateError("input: expected JSON object")
    return value


def unwrap_receipt(value: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if isinstance(value.get("review_fold"), dict):
        return "full", value["review_fold"]
    for key in ("rf_v13_compact", "RF-v1.3 compact", "RF-v1.3 compact:"):
        if isinstance(value.get(key), dict):
            return "compact", value[key]
    if "findings" in value or value.get("version") == "RF-v1.3":
        return "full", value
    if "validity" in value and "disposition" in value:
        return "compact", value
    raise ReceiptGateError("receipt: expected review_fold or RF-v1.3 compact object")


def as_no(value: Any) -> bool:
    return value in {"no", "false", "0", False}


def object_from(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def require_list(obj: dict[str, Any], key: str, errors: list[str], prefix: str) -> list[Any]:
    value = obj.get(key)
    if not isinstance(value, list):
        errors.append(f"{prefix}.{key}:must-be-list")
        return []
    return value


def source_ref_errors(source_ref: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    backend = source_ref.get("backend")
    if not isinstance(backend, str) or not backend:
        errors.append(f"{prefix}.backend:missing")
    elif backend not in VALID_BACKENDS:
        errors.append(f"{prefix}.backend:invalid")
    for key in ("head_sha", "target_fingerprint"):
        value = source_ref.get(key)
        if value is not None and not isinstance(value, str):
            errors.append(f"{prefix}.{key}:must-be-string")
    backend_specific = source_ref.get("backend_specific")
    if backend_specific is not None and not isinstance(backend_specific, dict):
        errors.append(f"{prefix}.backend_specific:must-be-object")
    return errors


def validate_enum(value: Any, valid: set[str], key: str, errors: list[str], prefix: str) -> str:
    if not isinstance(value, str) or not value:
        errors.append(f"{prefix}.{key}:missing")
        return ""
    if value not in valid:
        errors.append(f"{prefix}.{key}:invalid")
    return value


def mutation_authority_errors(finding: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    authority = object_from(finding.get("finding_mutation_authority"))
    if not authority:
        errors.append(f"{prefix}.finding_mutation_authority:missing")
        return errors
    if not as_no(authority.get("allowed")):
        errors.append(f"{prefix}.finding_mutation_authority.allowed:must-be-no")
    reason = authority.get("reason")
    if reason is not None and not isinstance(reason, str):
        errors.append(f"{prefix}.finding_mutation_authority.reason:must-be-string")
    return errors


def clean_run_errors(clean_run: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    if not clean_run:
        return errors
    normalized = clean_run.get("normalized_clean", "not-applicable")
    if normalized not in VALID_CLEAN:
        errors.append(f"{prefix}.clean_run.normalized_clean:invalid")
    effect = clean_run.get("count_effect", "unknown")
    if effect not in VALID_COUNT_EFFECT and not isinstance(effect, int):
        errors.append(f"{prefix}.clean_run.count_effect:invalid")
    reason = clean_run.get("reason")
    if reason is not None and not isinstance(reason, str):
        errors.append(f"{prefix}.clean_run.reason:must-be-string")
    return errors


def validate_finding(finding: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    if not finding:
        return [f"{prefix}:missing"]

    source_ref = object_from(finding.get("source_ref"))
    if not source_ref:
        errors.append(f"{prefix}.source_ref:missing")
    else:
        errors.extend(source_ref_errors(source_ref, f"{prefix}.source_ref"))

    validity = validate_enum(finding.get("validity"), VALID_VALIDITY, "validity", errors, prefix)
    validate_enum(finding.get("liability"), VALID_LIABILITY, "liability", errors, prefix)
    intent = validate_enum(finding.get("intent_relation"), VALID_INTENT, "intent_relation", errors, prefix)
    disposition = validate_enum(finding.get("disposition"), VALID_DISPOSITIONS, "disposition", errors, prefix)
    repair = validate_enum(finding.get("repair_level"), VALID_REPAIR, "repair_level", errors, prefix)

    if disposition in CODE_CHANGE_DISPOSITIONS and finding.get("code_change_candidate") not in {"yes", True}:
        errors.append(f"{prefix}.code_change_candidate:expected-yes-for-code-change-disposition")
    if disposition == "reject" and finding.get("code_change_candidate") in {"yes", True}:
        errors.append(f"{prefix}.code_change_candidate:reject-cannot-be-code-change")
    if disposition == "proof-only" and repair not in {"proof-only", "none"}:
        errors.append(f"{prefix}.repair_level:proof-only-disposition-mismatch")
    if disposition == "follow-up" and intent not in {"adjacent", "expands-scope", "unrelated"}:
        errors.append(f"{prefix}.intent_relation:follow-up-should-not-be-core")

    evidence_refs = require_list(finding, "evidence_refs", errors, prefix)
    if evidence_refs and not all(isinstance(item, str) and item for item in evidence_refs):
        errors.append(f"{prefix}.evidence_refs:must-be-strings")

    if validity in {"valid", "unproven", "needs-owner"} or disposition in MATERIAL_DISPOSITIONS:
        owner = finding.get("owner_boundary")
        law = finding.get("law_family")
        if not isinstance(owner, str) or not owner:
            errors.append(f"{prefix}.owner_boundary:missing")
        if not isinstance(law, str) or not law:
            errors.append(f"{prefix}.law_family:missing")

    errors.extend(mutation_authority_errors(finding, prefix))
    errors.extend(clean_run_errors(object_from(finding.get("clean_run")), prefix))
    return errors


def validate_compact(receipt: dict[str, Any]) -> dict[str, Any]:
    errors = validate_finding(receipt, "compact")
    clean = object_from(receipt.get("clean_run"))
    if not clean:
        errors.append("compact.clean_run:missing")
    return {
        "review_fold_receipt_gate": {
            "verdict": "pass" if not errors else "fail",
            "receipt_type": "compact",
            "errors": errors,
            "warnings": [],
        }
    }


def validate_full(receipt: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if receipt.get("version") != "RF-v1.3":
        errors.append("review_fold.version:expected-RF-v1.3")

    source = object_from(receipt.get("source"))
    if source:
        backend = source.get("backend")
        if backend is not None and backend not in VALID_BACKENDS:
            errors.append("review_fold.source.backend:invalid")
    else:
        warnings.append("review_fold.source:missing")

    findings = receipt.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("review_fold.findings:missing-or-empty")
        findings = []

    for index, finding_value in enumerate(findings):
        if not isinstance(finding_value, dict):
            errors.append(f"review_fold.findings[{index}]:must-be-object")
            continue
        errors.extend(validate_finding(finding_value, f"review_fold.findings[{index}]"))

    compression = object_from(receipt.get("compression"))
    risk = compression.get("one_patch_per_comment_risk")
    recommended = object_from(receipt.get("recommended_resolution"))
    action = object_from(receipt.get("action_plan"))
    mode = action.get("mode")
    if risk == "high" and mode not in {"refactor-kernel", "branch-race"}:
        warnings.append("compression.one_patch_per_comment_risk:high-without-kernel-or-branch-route")
    if mode == "refactor-kernel":
        owner = compression.get("repeated_kernel") or compression.get("owner_boundary")
        if not owner and not compression.get("equivalence_classes"):
            errors.append("compression.refactor-kernel:missing-equivalence-class-or-owner-boundary")

    clean = object_from(recommended.get("clean_run_accounting"))
    if clean:
        normalized = clean.get("normalized_clean_this_source", "not-applicable")
        if normalized not in VALID_CLEAN:
            errors.append("recommended_resolution.clean_run_accounting.normalized_clean_this_source:invalid")
        effect = clean.get("count_effect", "unknown")
        if effect not in VALID_COUNT_EFFECT:
            errors.append("recommended_resolution.clean_run_accounting.count_effect:invalid")

    return {
        "review_fold_receipt_gate": {
            "verdict": "pass" if not errors else "fail",
            "receipt_type": "full",
            "finding_count": len(findings),
            "errors": errors,
            "warnings": warnings,
        }
    }


def validate(value: dict[str, Any]) -> dict[str, Any]:
    receipt_type, body = unwrap_receipt(value)
    if receipt_type == "compact":
        return validate_compact(body)
    return validate_full(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate RF-v1.3 full or compact review-fold receipts")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--receipt", required=True, help="Path to JSON receipt, or '-' for stdin")
    validate_parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)

    try:
        report = validate(load_json(args.receipt))
    except (ReceiptGateError, OSError, json.JSONDecodeError) as exc:
        report = {
            "review_fold_receipt_gate": {
                "verdict": "fail",
                "receipt_type": "unknown",
                "errors": [str(exc)],
                "warnings": [],
            }
        }

    body = report["review_fold_receipt_gate"]
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"review_fold_receipt_gate: {body['verdict']}")
        for error in body.get("errors", []):
            print(f"error: {error}")
        for warning in body.get("warnings", []):
            print(f"warning: {warning}")

    return 0 if body["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
