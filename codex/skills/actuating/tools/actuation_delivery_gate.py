#!/usr/bin/env -S uv run python
"""ADD-v1 delivery handoff gate.

This gate decides whether a proved actuation run should stop locally, hand the
current integrated branch to $ship, or report a delivery blocker.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
import sys
from typing import Any

YES = {"yes", "true", "1", True}
NO = {"no", "false", "0", False}
PR_MODES = {"ready", "draft", "update-existing", "promote-draft", "none"}
PR_SOURCES = {"user", "actuation_run", "source_handoff", "none"}
CROSS_STATUSES = {"clear", "blocked", "unknown"}
VERDICTS = {"handoff_to_ship", "shipping_not_requested", "blocked"}


class DeliveryError(ValueError):
    pass


def load_json(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise DeliveryError("input: expected JSON object")
    return value


def unwrap(value: dict[str, Any], key: str) -> dict[str, Any]:
    body = value.get(key, value)
    if not isinstance(body, dict):
        raise DeliveryError(f"{key}: expected object")
    return body


def context_from(value: dict[str, Any]) -> dict[str, Any]:
    return unwrap(value, "actuation_delivery_context")


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def as_yes(value: Any) -> bool:
    return value in YES or (isinstance(value, str) and value.lower() in YES)


def as_no(value: Any) -> bool:
    return value in NO or (isinstance(value, str) and value.lower() in NO)


def yes_no_string(value: Any, *, default: str = "no") -> str:
    if as_yes(value):
        return "yes"
    if as_no(value):
        return "no"
    return default


def require_str(obj: dict[str, Any], key: str, errors: list[str]) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        errors.append(f"{key}:missing")
        return ""
    return value


def list_field(obj: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = obj.get(key, [])
    if not isinstance(value, list):
        errors.append(f"{key}:must-be-list")
        return []
    return value


def make_decision(context: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    run_id = require_str(context, "run_id", errors)
    plan_id = require_str(context, "plan_id", errors)
    target_branch = require_str(context, "target_branch", errors)
    target_head = require_str(context, "target_head", errors)
    base_branch = context.get("base_branch") if isinstance(context.get("base_branch"), str) else ""
    branch_epoch = context.get("branch_epoch")
    if not isinstance(branch_epoch, int) or isinstance(branch_epoch, bool) or branch_epoch < 0:
        errors.append("branch_epoch:missing-or-invalid")
        branch_epoch = None

    proof = context.get("proof_complete_receipt") if isinstance(context.get("proof_complete_receipt"), dict) else {}
    if not proof:
        errors.append("proof_complete_receipt:must-be-object")
    integration = context.get("integration") if isinstance(context.get("integration"), dict) else {}
    if not integration:
        errors.append("integration:must-be-object")
    pr_intent = context.get("pr_intent") if isinstance(context.get("pr_intent"), dict) else {}
    if not pr_intent:
        errors.append("pr_intent:must-be-object")
    current_pr = context.get("current_pr_state") if isinstance(context.get("current_pr_state"), dict) else {"exists": "unknown", "url": "", "draft": "unknown"}
    validation = context.get("validation") if isinstance(context.get("validation"), dict) else {}
    task_state = context.get("task_state") if isinstance(context.get("task_state"), dict) else {}

    receipts = integration.get("receipts", context.get("integrated_change_set_receipts", []))
    if not isinstance(receipts, list):
        receipts = []
        errors.append("integration.receipts:must-be-list")
    do_not_ship_before = context.get("do_not_ship_before", [])
    if not isinstance(do_not_ship_before, list):
        do_not_ship_before = [str(do_not_ship_before)]

    cross_status = context.get("cross_plan_dependency_status", "unknown")
    if cross_status not in CROSS_STATUSES:
        errors.append("cross_plan_dependency_status:invalid")
        cross_status = "unknown"

    requested_mode = pr_intent.get("requested_mode", "none")
    if requested_mode not in PR_MODES:
        errors.append("pr_intent.requested_mode:invalid")
        requested_mode = "none"
    source = pr_intent.get("source", "none")
    if source not in PR_SOURCES:
        errors.append("pr_intent.source:invalid")
        source = "none"
    pr_present = yes_no_string(pr_intent.get("present"), default="no")

    blocked: list[str] = []
    if errors:
        blocked.extend(errors)
    if not as_yes(proof.get("present")):
        blocked.append("proof_complete_receipt:missing")
    if not as_yes(proof.get("current")):
        blocked.append("proof_complete_receipt:not-current")
    if not as_yes(integration.get("queue_quiescent")):
        blocked.append("integration.queue_quiescent:not-yes")
    allow_no_change = as_yes(integration.get("no_change_integrated_receipt"))
    if not receipts and not allow_no_change:
        blocked.append("integration.receipts:empty")
    if cross_status != "clear":
        blocked.append(f"cross_plan_dependency_status:{cross_status}")
    if do_not_ship_before:
        blocked.extend(f"do_not_ship_before:{x}" for x in do_not_ship_before)

    if pr_present != "yes":
        verdict = "shipping_not_requested" if not blocked else "blocked"
    elif blocked:
        verdict = "blocked"
    else:
        verdict = "handoff_to_ship"

    ship_handoff: dict[str, Any] | None = None
    if verdict == "handoff_to_ship":
        mode = requested_mode if requested_mode != "none" else "ready"
        ship_handoff = {
            "next_owner": "$ship",
            "ship_input": {
                "branch": target_branch,
                "base_branch": base_branch or "unknown",
                "head_sha": target_head,
                "existing_pr": {
                    "exists": current_pr.get("exists", "unknown"),
                    "url": current_pr.get("url", ""),
                    "state": current_pr.get("state", "unknown"),
                    "draft": current_pr.get("draft", "unknown"),
                },
                "validation": {
                    "build": validation.get("build", "missing"),
                    "lint": validation.get("lint", "missing"),
                    "tests": validation.get("tests", "missing"),
                    "language_specific": validation.get("language_specific", "missing"),
                    "acceptance": validation.get("acceptance", "missing"),
                },
                "task_state": {
                    "complete": task_state.get("complete", "yes"),
                    "blocked": task_state.get("blocked", "no"),
                    "deferred": task_state.get("deferred", "no"),
                    "open": task_state.get("open", "no"),
                },
                "proof_summary": context.get("proof_summary", "Integrated target branch has current proof-complete receipt."),
                "user_requested_pr_mode": mode,
                "repo_policy_pr_mode": context.get("repo_policy_pr_mode", "unknown"),
                "actuation": {
                    "run_id": run_id,
                    "plan_id": plan_id,
                    "branch_epoch": branch_epoch,
                    "integrated_change_set_receipts": receipts,
                    "proof_complete_receipt": proof,
                    "cross_plan_dependency_status": cross_status,
                },
            },
        }

    decision = {
        "actuation_delivery_decision": {
            "decision_version": "ADD-v1",
            "verdict": verdict,
            "issued_at": now_utc(),
            "run_id": run_id,
            "plan_id": plan_id,
            "target_branch": target_branch,
            "target_head": target_head,
            "branch_epoch": branch_epoch,
            "proof_complete_receipt": {
                "present": yes_no_string(proof.get("present")),
                "current": yes_no_string(proof.get("current"), default="unknown"),
                "ref": proof.get("ref", ""),
            },
            "integration": {
                "queue_quiescent": yes_no_string(integration.get("queue_quiescent"), default="unknown"),
                "receipts": receipts,
            },
            "integrated_change_set_receipts": receipts,
            "cross_plan_dependency_status": cross_status,
            "pr_intent": {
                "present": pr_present,
                "source": source,
                "requested_mode": requested_mode,
            },
            "current_pr_state": {
                "exists": current_pr.get("exists", "unknown"),
                "url": current_pr.get("url", ""),
                "draft": current_pr.get("draft", "unknown"),
            },
            "do_not_ship_before": do_not_ship_before,
            "blocked_reasons": blocked if verdict == "blocked" else [],
            "ship_handoff": ship_handoff,
        }
    }
    validate_decision(decision)
    return decision


def validate_decision(value: dict[str, Any]) -> dict[str, Any]:
    d = unwrap(value, "actuation_delivery_decision")
    errors: list[str] = []
    if d.get("decision_version") != "ADD-v1":
        errors.append("decision_version")
    verdict = d.get("verdict")
    if verdict not in VERDICTS:
        errors.append("verdict")
    for key in ("run_id", "plan_id", "target_branch", "target_head"):
        if not isinstance(d.get(key), str) or not d.get(key):
            errors.append(f"{key}:missing")
    branch_epoch_valid = isinstance(d.get("branch_epoch"), int) and not isinstance(d.get("branch_epoch"), bool) and d.get("branch_epoch", -1) >= 0
    receipts = list_field(d, "integrated_change_set_receipts", errors)
    blocked = list_field(d, "blocked_reasons", errors)
    if not branch_epoch_valid and d.get("verdict") != "blocked":
        errors.append("branch_epoch")
    if d.get("cross_plan_dependency_status") not in CROSS_STATUSES:
        errors.append("cross_plan_dependency_status")
    pr_intent = d.get("pr_intent") if isinstance(d.get("pr_intent"), dict) else {}
    if pr_intent.get("present") not in {"yes", "no"}:
        errors.append("pr_intent.present")
    if pr_intent.get("source") not in PR_SOURCES:
        errors.append("pr_intent.source")
    if pr_intent.get("requested_mode") not in PR_MODES:
        errors.append("pr_intent.requested_mode")
    proof = d.get("proof_complete_receipt") if isinstance(d.get("proof_complete_receipt"), dict) else {}
    if proof.get("present") not in {"yes", "no"}:
        errors.append("proof_complete_receipt.present")
    if proof.get("current") not in {"yes", "no", "unknown"}:
        errors.append("proof_complete_receipt.current")
    integration = d.get("integration") if isinstance(d.get("integration"), dict) else {}
    if integration.get("queue_quiescent") not in {"yes", "no", "unknown"}:
        errors.append("integration.queue_quiescent")

    if verdict == "handoff_to_ship":
        if blocked:
            errors.append("handoff_to_ship:blocked_reasons-present")
        if pr_intent.get("present") != "yes":
            errors.append("handoff_to_ship:pr-intent-missing")
        if proof.get("present") != "yes" or proof.get("current") != "yes":
            errors.append("handoff_to_ship:proof-not-current")
        if integration.get("queue_quiescent") != "yes":
            errors.append("handoff_to_ship:integration-not-quiescent")
        no_change = any(str(item).startswith("no-change:") for item in receipts)
        if not receipts and not no_change:
            errors.append("handoff_to_ship:receipts-empty")
        if d.get("cross_plan_dependency_status") != "clear":
            errors.append("handoff_to_ship:cross-plan-not-clear")
        handoff = d.get("ship_handoff")
        if not isinstance(handoff, dict):
            errors.append("handoff_to_ship:ship_handoff-missing")
        else:
            if handoff.get("next_owner") != "$ship":
                errors.append("ship_handoff.next_owner")
            ship_input = handoff.get("ship_input")
            if not isinstance(ship_input, dict):
                errors.append("ship_handoff.ship_input")
            else:
                if ship_input.get("branch") != d.get("target_branch"):
                    errors.append("ship_input.branch:mismatch")
                if ship_input.get("head_sha") != d.get("target_head"):
                    errors.append("ship_input.head_sha:mismatch")
                actuation = ship_input.get("actuation") if isinstance(ship_input.get("actuation"), dict) else {}
                if actuation.get("plan_id") != d.get("plan_id"):
                    errors.append("ship_input.actuation.plan_id:mismatch")
    elif verdict == "shipping_not_requested":
        if pr_intent.get("present") != "no":
            errors.append("shipping_not_requested:pr-intent-present")
        if d.get("ship_handoff") is not None:
            errors.append("shipping_not_requested:ship_handoff-present")
    elif verdict == "blocked":
        if not blocked:
            errors.append("blocked:reasons-required")
        if d.get("ship_handoff") is not None:
            errors.append("blocked:ship_handoff-present")

    result = {
        "actuation_delivery_gate": {
            "verdict": "pass" if not errors else "fail",
            "decision_verdict": verdict,
            "run_id": d.get("run_id"),
            "plan_id": d.get("plan_id"),
            "errors": errors,
        }
    }
    if errors:
        raise DeliveryError(json.dumps(result, sort_keys=True))
    return result


def emit(obj: dict[str, Any], out: str | None = None) -> None:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decide or validate ADD-v1 delivery handoff.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_decide = sub.add_parser("decide")
    p_decide.add_argument("--context", required=True)
    p_decide.add_argument("--out")
    p_check = sub.add_parser("check")
    p_check.add_argument("--decision", required=True)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "decide":
            emit(make_decision(context_from(load_json(args.context))), args.out)
        elif args.cmd == "check":
            emit(validate_decision(load_json(args.decision)))
        return 0
    except Exception as exc:
        print(json.dumps({"actuation_delivery_gate": {"verdict": "fail", "error": str(exc)}}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
