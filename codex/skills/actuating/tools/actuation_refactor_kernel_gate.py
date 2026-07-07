#!/usr/bin/env -S uv run python
"""Refactor-kernel decision and outcome gate.

A refactor-kernel is not just a bigger patch.  It is a workflow decision made
when several accepted findings share one owner, invariant, proof surface, or
missing abstraction.  The decision must be recorded before mutation; the outcome
must be recorded after proof/review.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
import sys
from typing import Any

DECISION_KEY = "actuation_escalation_receipt"
OUTCOME_KEY = "refactor_kernel_outcome"
MODES = {"minimal-fix", "proof-only", "refactor-kernel", "branch-race", "remediation-plan", "blocked", "none"}
NEXT_MODES = {"minimal-fix", "refactor-kernel", "branch-race", "remediation-plan", "blocked"}
CLOSURE_STATES = {"local-proof-only", "ready-for-ship", "pushed", "cas-blocked", "complete", "regressed", "blocked", "unknown"}
ASSESSMENTS = {"effective", "overbroad", "underfit", "blocked", "unknown"}
YES = {"yes", "true", "1", True}
NO = {"no", "false", "0", False}


class RefactorKernelGateError(ValueError):
    pass


def load_json(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise RefactorKernelGateError("input: expected JSON object")
    return value


def unwrap(value: dict[str, Any], key: str) -> dict[str, Any]:
    body = value.get(key, value)
    if not isinstance(body, dict):
        raise RefactorKernelGateError(f"{key}: expected object")
    return body


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def as_yes(value: Any) -> bool:
    return value in YES or (isinstance(value, str) and value.lower() in YES)


def as_no(value: Any) -> bool:
    return value in NO or (isinstance(value, str) and value.lower() in NO)


def require_str(obj: dict[str, Any], key: str, errors: list[str]) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        errors.append(f"{key}:missing")
        return ""
    return value


def require_list(obj: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = obj.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"{key}:missing-or-empty")
        return []
    return value


def plain_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    return None


def valid_timestamp(value: str) -> bool:
    try:
        parsed = _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate_decision(value: dict[str, Any]) -> dict[str, Any]:
    d = unwrap(value, DECISION_KEY)
    errors: list[str] = []
    warnings: list[str] = []

    if d.get("version") != "AER-v1":
        errors.append("version:expected-AER-v1")
    run_id = require_str(d, "run_id", errors)
    owner_boundary = require_str(d, "owner_boundary", errors)
    repeated = require_str(d, "repeated_finding_class", errors)
    selected_route = require_str(d, "selected_route", errors)
    next_mode = require_str(d, "next_resolution_mode", errors)
    prior_mode = d.get("prior_resolution_mode")
    trigger = require_str(d, "escalation_trigger", errors)

    if selected_route != "refactor-kernel" or next_mode != "refactor-kernel":
        errors.append("refactor-kernel:selected_route-and-next_resolution_mode-required")
    if prior_mode not in MODES:
        errors.append("prior_resolution_mode:invalid")
    if next_mode not in NEXT_MODES:
        errors.append("next_resolution_mode:invalid")

    liabilities = require_list(d, "accepted_liabilities", errors)
    seen_liabilities: set[tuple[str, str, str, str]] = set()
    for index, liability in enumerate(liabilities):
        if not isinstance(liability, dict):
            errors.append(f"accepted_liabilities[{index}]:must-be-object")
            continue
        for key in ("cas_finding_id", "finding_fingerprint", "review_fold_ref", "liability"):
            require_str(liability, key, errors)
        fingerprint = (
            liability.get("cas_finding_id"),
            liability.get("finding_fingerprint"),
            liability.get("review_fold_ref"),
            liability.get("liability"),
        )
        if all(isinstance(part, str) and part for part in fingerprint):
            if fingerprint in seen_liabilities:
                errors.append(f"accepted_liabilities[{index}]:duplicate")
            seen_liabilities.add(fingerprint)

    alternatives = require_list(d, "alternatives_considered", errors)
    if alternatives and not all(isinstance(x, str) and x for x in alternatives):
        errors.append("alternatives_considered:must-be-nonempty-strings")
    for required_alt in ("minimal-fix", "branch-race", "remediation-plan"):
        if required_alt not in alternatives:
            errors.append(f"alternatives_considered:{required_alt}:missing")

    verifier = require_list(d, "verifier", errors)
    if verifier and not all(isinstance(x, str) and x for x in verifier):
        errors.append("verifier:must-be-nonempty-strings")

    scope = d.get("current_artifact_scope")
    if not isinstance(scope, dict):
        errors.append("current_artifact_scope:must-be-object")
        scope = {}
    for key in ("branch", "head_sha", "target_fingerprint"):
        require_str(scope, key, errors)

    if len(liabilities) < 2:
        warnings.append("accepted_liabilities:single-liability-kernel")
    if owner_boundary and owner_boundary.lower() in {"unknown", "none"}:
        errors.append("owner_boundary:must-name-real-boundary")
    if trigger and "repeated" not in trigger.lower() and "shared" not in trigger.lower():
        warnings.append("escalation_trigger:does-not-name-repetition-or-shared-boundary")

    return {
        "refactor_kernel_decision_gate": {
            "verdict": "pass" if not errors else "fail",
            "run_id": run_id,
            "selected_route": selected_route,
            "owner_boundary": owner_boundary,
            "liability_count": len(liabilities),
            "errors": errors,
            "warnings": warnings,
        }
    }


def validate_outcome(value: dict[str, Any], decision_value: dict[str, Any] | None = None) -> dict[str, Any]:
    outcome = unwrap(value, OUTCOME_KEY)
    errors: list[str] = []
    warnings: list[str] = []

    if outcome.get("version") != "RKO-v1":
        errors.append("version:expected-RKO-v1")
    issued_at = require_str(outcome, "issued_at", errors)
    if issued_at and not valid_timestamp(issued_at):
        errors.append("issued_at:invalid-timestamp")
    run_id = require_str(outcome, "run_id", errors)
    decision_ref = require_str(outcome, "decision_ref", errors)
    owner_boundary = require_str(outcome, "owner_boundary", errors)
    head_before = require_str(outcome, "head_before", errors)
    head_after = require_str(outcome, "head_after", errors)

    patch_calls = plain_int(outcome.get("patch_calls"))
    if patch_calls is None or patch_calls < 0:
        errors.append("patch_calls:nonnegative-int-required")
        patch_calls = 0
    files_changed = plain_int(outcome.get("files_changed"))
    if files_changed is None or files_changed < 0:
        errors.append("files_changed:nonnegative-int-required")
        files_changed = 0
    covered = plain_int(outcome.get("covered_liabilities"))
    if covered is None or covered < 0:
        errors.append("covered_liabilities:nonnegative-int-required")
        covered = 0

    local_proof = outcome.get("local_proof")
    if not isinstance(local_proof, dict):
        errors.append("local_proof:must-be-object")
        local_proof = {}
    for key in ("passed", "failed"):
        if not isinstance(local_proof.get(key), list):
            errors.append(f"local_proof.{key}:must-be-list")
    passed_proofs = local_proof.get("passed") if isinstance(local_proof.get("passed"), list) else []

    review_after = outcome.get("review_after")
    if not isinstance(review_after, dict):
        errors.append("review_after:must-be-object")
        review_after = {}
    new_liabilities = plain_int(review_after.get("new_liabilities"))
    clean_runs = plain_int(review_after.get("clean_runs"))
    if new_liabilities is None or new_liabilities < 0:
        errors.append("review_after.new_liabilities:nonnegative-int-required")
        new_liabilities = 0
    if clean_runs is None or clean_runs < 0:
        errors.append("review_after.clean_runs:nonnegative-int-required")
        clean_runs = 0
    blocked_reason = review_after.get("blocked_reason", "")
    if blocked_reason is not None and not isinstance(blocked_reason, str):
        errors.append("review_after.blocked_reason:must-be-string")

    closure_state = require_str(outcome, "closure_state", errors)
    assessment = require_str(outcome, "assessment", errors)
    if closure_state not in CLOSURE_STATES:
        errors.append("closure_state:invalid")
    if assessment not in ASSESSMENTS:
        errors.append("assessment:invalid")
    if closure_state in {"complete", "ready-for-ship", "pushed"} and local_proof.get("failed"):
        errors.append("closure_state:cannot-be-ready-with-failed-local-proof")
    if closure_state in {"cas-blocked", "blocked"} and not blocked_reason:
        warnings.append("blocked_outcome:blocked_reason-empty")
    if assessment == "effective" and closure_state not in {"complete", "ready-for-ship", "pushed"}:
        errors.append("assessment:effective-requires-terminal-or-ready-state")
    if assessment == "effective" and new_liabilities:
        errors.append("assessment:effective-with-new-liabilities")
    if assessment == "effective" and not passed_proofs:
        errors.append("assessment:effective-without-local-proof")

    governance = outcome.get("governance")
    if not isinstance(governance, dict):
        errors.append("governance:must-be-object")
        governance = {}
    graph_bypass = governance.get("graph_bypass")
    if "graph_bypass" not in governance:
        errors.append("governance.graph_bypass:missing")
    elif not as_yes(graph_bypass) and not as_no(graph_bypass):
        errors.append("governance.graph_bypass:yes-or-no-required")
    mutations_without_control = plain_int(governance.get("mutations_without_graph_control_receipt"))
    if "mutations_without_graph_control_receipt" not in governance:
        errors.append("governance.mutations_without_graph_control_receipt:missing")
    if as_yes(graph_bypass):
        errors.append("governance.graph_bypass:yes")
    if mutations_without_control is None or mutations_without_control < 0:
        errors.append("governance.mutations_without_graph_control_receipt:nonnegative-int-required")
        mutations_without_control = 0
    elif mutations_without_control > 0:
        errors.append("governance.mutations_without_graph_control_receipt:nonzero")

    expected_liabilities = 0
    if decision_value is None:
        errors.append("decision_ref:decision-required")
    else:
        decision_report = validate_decision(decision_value)["refactor_kernel_decision_gate"]
        if decision_report["verdict"] != "pass":
            errors.append("decision_ref:decision-invalid")
        decision = unwrap(decision_value, DECISION_KEY)
        expected_liabilities = len(decision.get("accepted_liabilities", []))
        if run_id != decision.get("run_id"):
            errors.append("decision_ref:run_id-mismatch")
        if decision_ref not in {decision.get("run_id"), f"AER-v1:{decision.get('run_id')}"}:
            errors.append("decision_ref:does-not-reference-AER-run")
        if owner_boundary != decision.get("owner_boundary"):
            errors.append("owner_boundary:mismatch")
        scope = decision.get("current_artifact_scope") if isinstance(decision.get("current_artifact_scope"), dict) else {}
        if head_before != scope.get("head_sha"):
            errors.append("head_before:mismatch-current-artifact-scope")
        if covered < expected_liabilities and assessment == "effective":
            errors.append("assessment:effective-with-uncovered-liabilities")
        elif covered < expected_liabilities:
            warnings.append("covered_liabilities:below-decision-liability-count")

    unresolved_terminal_blocker = 1 if closure_state in {"cas-blocked", "blocked", "regressed", "unknown"} else 0
    graph_bypass_penalty = 1 if as_yes(graph_bypass) or mutations_without_control else 0
    effectiveness_score = covered - new_liabilities - unresolved_terminal_blocker - graph_bypass_penalty

    return {
        "refactor_kernel_outcome_gate": {
            "verdict": "pass" if not errors else "fail",
            "run_id": run_id,
            "decision_ref": decision_ref,
            "closure_state": closure_state,
            "assessment": assessment,
            "patch_calls": patch_calls,
            "files_changed": files_changed,
            "covered_liabilities": covered,
            "expected_liabilities": expected_liabilities,
            "new_liabilities": new_liabilities,
            "clean_runs": clean_runs,
            "effectiveness_score": effectiveness_score,
            "errors": errors,
            "warnings": warnings,
        }
    }


def make_outcome(context: dict[str, Any], decision_value: dict[str, Any]) -> dict[str, Any]:
    decision_report = validate_decision(decision_value)["refactor_kernel_decision_gate"]
    if decision_report["verdict"] != "pass":
        raise RefactorKernelGateError("decision:invalid")
    decision = unwrap(decision_value, DECISION_KEY)
    scope = decision.get("current_artifact_scope") if isinstance(decision.get("current_artifact_scope"), dict) else {}
    outcome = {
        OUTCOME_KEY: {
            "version": "RKO-v1",
            "issued_at": now_utc(),
            "run_id": decision.get("run_id"),
            "decision_ref": f"AER-v1:{decision.get('run_id')}",
            "owner_boundary": decision.get("owner_boundary"),
            "head_before": scope.get("head_sha", ""),
            "head_after": context.get("head_after", ""),
            "patch_calls": context.get("patch_calls", 0),
            "files_changed": context.get("files_changed", 0),
            "covered_liabilities": context.get("covered_liabilities", 0),
            "local_proof": context.get("local_proof", {"passed": [], "failed": []}),
            "review_after": context.get("review_after", {"new_liabilities": 0, "clean_runs": 0, "blocked_reason": ""}),
            "closure_state": context.get("closure_state", "unknown"),
            "assessment": context.get("assessment", "unknown"),
            "governance": context.get("governance", {"graph_bypass": "no", "mutations_without_graph_control_receipt": 0}),
        }
    }
    report = validate_outcome(outcome, decision_value)["refactor_kernel_outcome_gate"]
    if report["verdict"] != "pass":
        outcome[OUTCOME_KEY]["gate_errors"] = report["errors"]
        outcome[OUTCOME_KEY]["gate_warnings"] = report["warnings"]
    return outcome


def emit(obj: dict[str, Any], out: str | None = None) -> None:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    if out:
        Path(out).write_text(text, encoding="utf-8")
    print(text, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p_decision = sub.add_parser("check-decision")
    p_decision.add_argument("--receipt", required=True)
    p_decision.add_argument("--out")
    p_outcome = sub.add_parser("check-outcome")
    p_outcome.add_argument("--outcome", required=True)
    p_outcome.add_argument("--decision")
    p_outcome.add_argument("--out")
    p_make = sub.add_parser("make-outcome")
    p_make.add_argument("--context", required=True)
    p_make.add_argument("--decision", required=True)
    p_make.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        if args.command == "check-decision":
            result = validate_decision(load_json(args.receipt))
        elif args.command == "check-outcome":
            decision = load_json(args.decision) if args.decision else None
            result = validate_outcome(load_json(args.outcome), decision)
        elif args.command == "make-outcome":
            result = make_outcome(load_json(args.context), load_json(args.decision))
        else:
            raise RefactorKernelGateError(f"unknown command: {args.command}")
    except Exception as exc:
        print(json.dumps({"refactor_kernel_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 2
    emit(result, args.out)
    body = next(iter(result.values())) if result else {}
    return 0 if body.get("verdict", "pass") == "pass" and not body.get("gate_errors") else 2


if __name__ == "__main__":
    raise SystemExit(main())
