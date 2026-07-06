#!/usr/bin/env -S uv run python
"""RF-v1.5 receipt validator for $review-fold.

The gate validates JSON projections of full RF-v1.5 receipts and compact
RF-v1.5 receipts. It intentionally avoids review-backend policy: source fields
are evidence references, not validity, kernel status, or mutation authority.
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
    "ask-human",
    "follow-up",
    "blocked",
}
MATERIAL_DISPOSITIONS = VALID_DISPOSITIONS
VALID_KERNEL_STATUS = {"none", "refactor-kernel", "unknown"}
VALID_KERNEL_PRESSURE = {"none", "low", "medium", "high"}
VALID_BOUNDARY_PROOF = {"proven", "not-proven", "not-applicable"}
VALID_NEXT_EVIDENCE_ACTION = {"inspect-more", "ask-human", "blocked", "branch-race", "reclassify"}
VALID_CLEAN = {"yes", "no", "not-applicable"}
VALID_COUNT_EFFECT = {"increment", "reset", "none", "blocked", "unknown"}
FORBIDDEN_FINDING_KEYS = {"repair_level", "code_change_candidate"}
FORBIDDEN_FULL_KEYS = {"action_plan"}
AUXILIARY_OWNER_LANES = {"footgun-finder", "invariant-ace", "complexity-mitigator"}
SPECIALIZED_LIABILITY_LANES = {
    "misuse-hazard": "footgun-finder",
    "invariant-gap": "invariant-ace",
    "complexity-stall": "complexity-mitigator",
}


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
    for key in ("rf_v15_compact", "RF-v1.5 compact", "RF-v1.5 compact:"):
        if isinstance(value.get(key), dict):
            return "compact", value[key]
    for key in (
        "rf_v14_compact",
        "RF-v1.4 compact",
        "RF-v1.4 compact:",
        "rf_v13_compact",
        "RF-v1.3 compact",
        "RF-v1.3 compact:",
    ):
        if isinstance(value.get(key), dict):
            raise ReceiptGateError("receipt: expected RF-v1.5 compact object")
    if "findings" in value or value.get("version") in {"RF-v1.5", "RF-v1.4", "RF-v1.3"}:
        return "full", value
    if "validity" in value and "disposition" in value:
        return "compact", value
    raise ReceiptGateError("receipt: expected review_fold or RF-v1.5 compact object")


def as_no(value: Any) -> bool:
    return value in {"no", "false", "0", False}


def object_from(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def meaningful(value: Any) -> bool:
    return isinstance(value, str) and value not in {"", "unknown", "not-applicable", "none"}


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


def clean_run_errors(clean_run: dict[str, Any], prefix: str, kernel_status: str = "") -> list[str]:
    errors: list[str] = []
    if not clean_run:
        return errors
    normalized = clean_run.get("normalized_clean", "not-applicable")
    if normalized not in VALID_CLEAN:
        errors.append(f"{prefix}.clean_run.normalized_clean:invalid")
    effect = clean_run.get("count_effect", "unknown")
    if effect not in VALID_COUNT_EFFECT and not isinstance(effect, int):
        errors.append(f"{prefix}.clean_run.count_effect:invalid")
    if kernel_status == "unknown":
        if normalized == "yes":
            errors.append(f"{prefix}.clean_run.normalized_clean:unknown-cannot-be-clean")
        if effect in {"increment"} or (isinstance(effect, int) and effect > 0):
            errors.append(f"{prefix}.clean_run.count_effect:unknown-cannot-increment-clean-run")
    reason = clean_run.get("reason")
    if reason is not None and not isinstance(reason, str):
        errors.append(f"{prefix}.clean_run.reason:must-be-string")
    return errors


def source_owner_lens(source_ref: dict[str, Any]) -> str:
    lane = source_ref.get("lane")
    role = source_ref.get("lane_role", source_ref.get("laneRole"))
    if lane in AUXILIARY_OWNER_LANES and role == "auxiliary":
        return lane
    return ""


def finding_owner_lens(finding: dict[str, Any], source_ref: dict[str, Any]) -> str:
    direct = finding.get("owner_lens", finding.get("auxiliary_owner_lens"))
    if direct in AUXILIARY_OWNER_LANES:
        return direct
    obligation = object_from(finding.get("review_obligation"))
    if obligation.get("owner_lens") in AUXILIARY_OWNER_LANES:
        return obligation["owner_lens"]
    return source_owner_lens(source_ref)


def specialized_owner_lens_errors(
    finding: dict[str, Any],
    source_ref: dict[str, Any],
    liability: str,
    disposition: str,
    prefix: str,
) -> list[str]:
    expected = SPECIALIZED_LIABILITY_LANES.get(liability)
    if not expected:
        return []
    errors: list[str] = []
    if finding_owner_lens(finding, source_ref) == expected:
        return errors

    if disposition not in {"blocked", "ask-human"}:
        errors.append(f"{prefix}.review_obligation.owner_lens:required-before-nonblocked-disposition")

    clean = object_from(finding.get("clean_run"))
    normalized = clean.get("normalized_clean", "not-applicable")
    effect = clean.get("count_effect", "unknown")
    if normalized == "yes":
        errors.append(f"{prefix}.clean_run.normalized_clean:specialized-owner-lens-required")
    if effect == "increment" or (isinstance(effect, int) and effect > 0):
        errors.append(f"{prefix}.clean_run.count_effect:specialized-owner-lens-required")
    return errors


def kernel_fold_errors(finding: dict[str, Any], prefix: str, disposition: str) -> list[str]:
    errors: list[str] = []
    kernel = object_from(finding.get("kernel_fold"))
    if not kernel:
        errors.append(f"{prefix}.kernel_fold:missing")
        return errors

    status = validate_enum(
        kernel.get("status"), VALID_KERNEL_STATUS, "kernel_fold.status", errors, prefix
    )
    pressure = validate_enum(
        kernel.get("pressure"), VALID_KERNEL_PRESSURE, "kernel_fold.pressure", errors, prefix
    )
    boundary_proof = validate_enum(
        kernel.get("boundary_proof"), VALID_BOUNDARY_PROOF, "kernel_fold.boundary_proof", errors, prefix
    )

    for key in ("equivalence_class", "owner_boundary", "law_family", "falsifier"):
        value = kernel.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{prefix}.kernel_fold.{key}:missing")

    evidence_refs = require_list(kernel, "evidence_refs", errors, f"{prefix}.kernel_fold")
    if evidence_refs and not all(isinstance(item, str) and item for item in evidence_refs):
        errors.append(f"{prefix}.kernel_fold.evidence_refs:must-be-strings")

    if status == "refactor-kernel" and not (
        meaningful(kernel.get("equivalence_class")) or meaningful(kernel.get("owner_boundary"))
    ):
        errors.append(f"{prefix}.kernel_fold.refactor-kernel:missing-equivalence-class-or-owner-boundary")
    if boundary_proof == "proven" and not evidence_refs:
        errors.append(f"{prefix}.kernel_fold.boundary_proof:proven-requires-evidence")
    if status == "unknown":
        if boundary_proof == "proven":
            errors.append(f"{prefix}.kernel_fold.boundary_proof:unknown-cannot-be-proven")
        proof_gap = kernel.get("proof_gap")
        if not meaningful(proof_gap):
            errors.append(f"{prefix}.kernel_fold.proof_gap:required-for-unknown")
        validate_enum(
            kernel.get("next_evidence_action"),
            VALID_NEXT_EVIDENCE_ACTION,
            "kernel_fold.next_evidence_action",
            errors,
            prefix,
        )

    return errors


def validate_finding(finding: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    if not finding:
        return [f"{prefix}:missing"]

    for key in FORBIDDEN_FINDING_KEYS & finding.keys():
        errors.append(f"{prefix}.{key}:forbidden-in-RF-v1.5")

    source_ref = object_from(finding.get("source_ref"))
    if not source_ref:
        errors.append(f"{prefix}.source_ref:missing")
    else:
        errors.extend(source_ref_errors(source_ref, f"{prefix}.source_ref"))

    validity = validate_enum(finding.get("validity"), VALID_VALIDITY, "validity", errors, prefix)
    liability = validate_enum(finding.get("liability"), VALID_LIABILITY, "liability", errors, prefix)
    intent = validate_enum(finding.get("intent_relation"), VALID_INTENT, "intent_relation", errors, prefix)
    disposition = validate_enum(finding.get("disposition"), VALID_DISPOSITIONS, "disposition", errors, prefix)

    kernel = object_from(finding.get("kernel_fold"))
    kernel_status = kernel.get("status")
    if kernel_status == "refactor-kernel" and disposition != "blocked":
        errors.append(f"{prefix}.disposition:refactor-kernel-requires-blocked-control")
    if kernel_status == "unknown" and disposition not in {"blocked", "ask-human"}:
        errors.append(f"{prefix}.disposition:unknown-requires-blocked-or-ask-human")
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

    errors.extend(kernel_fold_errors(finding, prefix, disposition))
    errors.extend(mutation_authority_errors(finding, prefix))
    errors.extend(clean_run_errors(object_from(finding.get("clean_run")), prefix, kernel_status))
    errors.extend(specialized_owner_lens_errors(finding, source_ref, liability, disposition, prefix))
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

    if receipt.get("version") != "RF-v1.5":
        errors.append("review_fold.version:expected-RF-v1.5")

    for key in FORBIDDEN_FULL_KEYS & receipt.keys():
        errors.append(f"review_fold.{key}:forbidden-in-RF-v1.5")

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
    has_unknown_kernel = any(
        isinstance(finding_value, dict)
        and object_from(finding_value.get("kernel_fold")).get("status") == "unknown"
        for finding_value in findings
    )

    compression = object_from(receipt.get("compression"))
    pressure = compression.get("kernel_pressure")
    if pressure is not None and pressure not in VALID_KERNEL_PRESSURE:
        errors.append("review_fold.compression.kernel_pressure:invalid")

    recommended = object_from(receipt.get("recommended_resolution"))
    clean = object_from(recommended.get("clean_run_accounting"))
    if clean:
        normalized = clean.get("normalized_clean_this_source", "not-applicable")
        if normalized not in VALID_CLEAN:
            errors.append("recommended_resolution.clean_run_accounting.normalized_clean_this_source:invalid")
        effect = clean.get("count_effect", "unknown")
        if effect not in VALID_COUNT_EFFECT:
            errors.append("recommended_resolution.clean_run_accounting.count_effect:invalid")
        if has_unknown_kernel:
            if normalized == "yes":
                errors.append("recommended_resolution.clean_run_accounting.normalized_clean_this_source:unknown-cannot-be-clean")
            if effect == "increment":
                errors.append("recommended_resolution.clean_run_accounting.count_effect:unknown-cannot-increment-clean-run")

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
    try:
        receipt_type, body = unwrap_receipt(value)
    except ReceiptGateError as exc:
        return {
            "review_fold_receipt_gate": {
                "verdict": "fail",
                "receipt_type": "unknown",
                "errors": [str(exc)],
                "warnings": [],
            }
        }
    if receipt_type == "compact":
        return validate_compact(body)
    return validate_full(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate RF-v1.5 full or compact review-fold receipts")
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
