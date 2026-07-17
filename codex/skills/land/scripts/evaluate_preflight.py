#!/usr/bin/env python3
"""Pure, fail-closed evaluator for one $land preflight snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

RECORD_VERSION = "LAND-PREFLIGHT-v1"
IDENTITY_FIELDS = (
    "repository",
    "pr_number",
    "base_ref",
    "head_repository",
    "head_ref",
    "head_oid",
)
DELIVERY_ROUTES = {
    "immediate": "merge-now",
    "queue": "queue-and-wait",
    "auto": "auto-merge-and-wait",
}


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _block(blockers: list[dict[str, str]], code: str, detail: str) -> None:
    blockers.append({"code": code, "detail": detail})


def _gate(gates: dict[str, str], name: str, passed: bool) -> None:
    gates[name] = "pass" if passed else "fail"


def evaluate(snapshot: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    gates: dict[str, str] = {}

    expected = _mapping(snapshot.get("expected"))
    observed = _mapping(snapshot.get("observed"))
    reviews = _mapping(snapshot.get("reviews"))
    checks = _mapping(snapshot.get("checks"))
    merge = _mapping(snapshot.get("merge"))
    policy = _mapping(snapshot.get("policy"))

    if not expected:
        _block(blockers, "SCHEMA_EXPECTED_MISSING", "expected must be an object")
    if not observed:
        _block(blockers, "SCHEMA_OBSERVED_MISSING", "observed must be an object")

    identity_ok = True
    for field in IDENTITY_FIELDS:
        expected_value = expected.get(field)
        observed_value = observed.get(field)
        if expected_value in (None, ""):
            identity_ok = False
            _block(blockers, "TARGET_EXPECTED_FIELD_MISSING", f"expected.{field} is required")
        elif observed_value in (None, ""):
            identity_ok = False
            _block(blockers, "TARGET_OBSERVED_FIELD_MISSING", f"observed.{field} is required")
        elif expected_value != observed_value:
            identity_ok = False
            code = "TARGET_HEAD_MISMATCH" if field == "head_oid" else "TARGET_IDENTITY_MISMATCH"
            _block(
                blockers,
                code,
                f"{field} expected {expected_value!r} but observed {observed_value!r}",
            )
    _gate(gates, "target_identity", identity_ok)
    _gate(
        gates,
        "exact_head",
        bool(expected.get("head_oid")) and expected.get("head_oid") == observed.get("head_oid"),
    )

    state = observed.get("state")
    if state not in {"OPEN", "MERGED", "CLOSED"}:
        _block(blockers, "PR_STATE_UNKNOWN", f"unsupported observed.state: {state!r}")

    if state == "MERGED":
        merged_at = observed.get("merged_at")
        merge_commit_oid = observed.get("merge_commit_oid")
        postcondition_ok = bool(merged_at) and bool(merge_commit_oid)
        if not merged_at:
            _block(blockers, "MERGED_AT_MISSING", "MERGED state requires observed.merged_at")
        if not merge_commit_oid:
            _block(
                blockers,
                "MERGE_COMMIT_MISSING",
                "MERGED state requires observed.merge_commit_oid",
            )
        _gate(gates, "pr_state", postcondition_ok)
        result_mode = "cleanup-only" if identity_ok and postcondition_ok and not blockers else "blocked"
        return {
            "land_preflight": {
                "record_version": RECORD_VERSION,
                "verdict": "pass" if result_mode == "cleanup-only" else "block",
                "mode": result_mode,
                "expected_head_oid": expected.get("head_oid"),
                "gates": gates,
                "blockers": blockers,
            }
        }

    open_ready = state == "OPEN" and observed.get("is_draft") is False
    if state == "CLOSED":
        _block(blockers, "PR_CLOSED_UNMERGED", "closed, unmerged PRs cannot be landed")
    elif state == "OPEN" and observed.get("is_draft") is not False:
        _block(blockers, "PR_DRAFT", "draft PR must be promoted by an authorized workflow before landing")
    _gate(gates, "pr_state", open_ready)

    inventory_complete = reviews.get("inventory_complete") is True
    unresolved_threads = reviews.get("unresolved_threads")
    if unresolved_threads != 0:
        _block(
            blockers,
            "REVIEW_THREADS_UNRESOLVED",
            f"expected 0 unresolved threads, observed {unresolved_threads!r}",
        )
    if not inventory_complete:
        _block(
            blockers,
            "REVIEW_INVENTORY_INCOMPLETE",
            "complete paginated review-thread inventory is required",
        )
    review_inventory_ok = inventory_complete and unresolved_threads == 0
    _gate(gates, "review_inventory", review_inventory_ok)

    requested_changes_active = reviews.get("requested_changes_active")
    explicit_blockers = reviews.get("explicit_blockers")
    approvals_required = policy.get("approvals_required")
    review_decision = reviews.get("review_decision")

    review_decision_ok = True
    if requested_changes_active is not False:
        review_decision_ok = False
        _block(
            blockers,
            "REQUESTED_CHANGES_ACTIVE",
            "requested_changes_active must be explicitly false",
        )
    if not isinstance(explicit_blockers, int) or isinstance(explicit_blockers, bool):
        review_decision_ok = False
        _block(blockers, "EXPLICIT_BLOCKERS_INVALID", "explicit_blockers must be an integer")
    elif explicit_blockers != 0:
        review_decision_ok = False
        _block(
            blockers,
            "EXPLICIT_BLOCKERS_PRESENT",
            f"observed {explicit_blockers} explicit blocker(s)",
        )
    if approvals_required is not False and approvals_required is not True:
        review_decision_ok = False
        _block(
            blockers,
            "APPROVAL_POLICY_UNKNOWN",
            "policy.approvals_required must be true or false",
        )
    elif approvals_required is True and review_decision != "APPROVED":
        review_decision_ok = False
        _block(
            blockers,
            "APPROVAL_MISSING",
            f"approval required but review_decision is {review_decision!r}",
        )
    _gate(gates, "review_decision", review_decision_ok)

    required_expected = checks.get("required_expected")
    raw_check_items = checks.get("items")
    if not isinstance(raw_check_items, list):
        _block(blockers, "CHECK_ITEMS_INVALID", "checks.items must be a list")
    check_items = _list(raw_check_items)
    if required_expected is not False and required_expected is not True:
        _block(
            blockers,
            "REQUIRED_CHECK_POLICY_UNKNOWN",
            "checks.required_expected must be true or false",
        )
    required_items = [item for item in check_items if isinstance(item, dict) and item.get("required") is True]
    checks_ok = required_expected is True or required_expected is False
    if required_expected is True and not required_items:
        checks_ok = False
        _block(
            blockers,
            "REQUIRED_CHECKS_MISSING",
            "repository policy expects required checks but no required check items were supplied",
        )

    allow_skipping = policy.get("allow_required_skipping") is True
    allowed_buckets = {"pass"}
    if allow_skipping:
        allowed_buckets.add("skipping")

    for index, item in enumerate(check_items):
        if not isinstance(item, dict):
            checks_ok = False
            _block(blockers, "CHECK_ITEM_INVALID", f"checks.items[{index}] must be an object")
            continue
        if item.get("required") is not True:
            continue
        name = item.get("name") or f"required-check-{index}"
        bucket = item.get("bucket")
        if bucket not in allowed_buckets:
            checks_ok = False
            code = "REQUIRED_CHECK_CANCELLED" if bucket == "cancel" else "REQUIRED_CHECK_NOT_GREEN"
            _block(
                blockers,
                code,
                f"required check {name!r} has bucket {bucket!r}",
            )
    _gate(gates, "required_checks", checks_ok)

    conflict_free = merge.get("conflict_free") is True
    branch_up_to_date = merge.get("branch_up_to_date") is True
    policy_satisfied = merge.get("policy_satisfied") is True
    method_allowed = merge.get("method_allowed") is True
    admin_override = merge.get("admin_override")

    if not conflict_free:
        _block(blockers, "MERGE_CONFLICT", "merge.conflict_free must be true")
    if not branch_up_to_date:
        _block(blockers, "BRANCH_NOT_CURRENT", "merge.branch_up_to_date must be true")
    if not policy_satisfied:
        _block(blockers, "REPOSITORY_POLICY_BLOCK", "merge.policy_satisfied must be true")
    if not method_allowed:
        _block(blockers, "MERGE_METHOD_NOT_ALLOWED", "merge.method_allowed must be true")
    if admin_override is not False:
        _block(
            blockers,
            "ADMIN_OVERRIDE_NOT_AUTHORIZED",
            "merge.admin_override must be explicitly false for ordinary preflight",
        )

    _gate(gates, "conflict_free", conflict_free)
    _gate(gates, "branch_freshness", branch_up_to_date)
    _gate(
        gates,
        "repository_policy",
        policy_satisfied and method_allowed and admin_override is False,
    )

    delivery_mode = merge.get("delivery_mode")
    route = DELIVERY_ROUTES.get(delivery_mode)
    if route is None:
        _block(
            blockers,
            "DELIVERY_MODE_INVALID",
            f"merge.delivery_mode must be one of {sorted(DELIVERY_ROUTES)}, observed {delivery_mode!r}",
        )

    verdict = "pass" if not blockers else "block"
    mode = route if verdict == "pass" and route is not None else "blocked"
    return {
        "land_preflight": {
            "record_version": RECORD_VERSION,
            "verdict": verdict,
            "mode": mode,
            "expected_head_oid": expected.get("head_oid"),
            "gates": gates,
            "blockers": blockers,
        }
    }


def _load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("snapshot must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?", default="-", help="JSON file, or - for stdin")
    args = parser.parse_args(argv)

    try:
        result = evaluate(_load(args.snapshot))
    except Exception as exc:
        result = {
            "land_preflight": {
                "record_version": RECORD_VERSION,
                "verdict": "block",
                "mode": "blocked",
                "expected_head_oid": None,
                "gates": {},
                "blockers": [{"code": "SNAPSHOT_INVALID", "detail": str(exc)}],
            }
        }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["land_preflight"]["verdict"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
