#!/usr/bin/env python3
"""Pure, fail-closed evaluator for one $land preflight snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VERSION = "LAND-PREFLIGHT-v2"
IDENTITY = ("repository", "pr_number", "base_ref", "head_repository", "head_ref", "head_oid")
ROUTES = {"immediate": "merge-now", "queue": "queue-and-wait", "auto": "auto-merge-and-wait"}
DISPOSITIONS = {
    "fixed-and-evidenced", "already-satisfied-and-evidenced",
    "obsolete-and-evidenced", "reviewer-withdrawn", "nonblocking-by-authority",
}
AUTHORITIES = {"entailed", "strengthening", "preference", "new-requirement", "underdetermined"}
APPLICABILITY = {"still-present", "transformed-applicable", "already-excluded", "not-comparable", "unknown"}
NA_GATES = ("required_checks", "conflict_free", "branch_freshness", "repository_policy")


def issue(dst: list[dict[str, str]], code: str, detail: str) -> None:
    dst.append({"code": code, "detail": detail})


def gate(gates: dict[str, str], name: str, value: bool | str) -> None:
    gates[name] = ("pass" if value else "fail") if isinstance(value, bool) else value


def result(verdict: str, status: str, admission: str, mode: str, head: Any,
           gates: dict[str, str], reasons: list[dict[str, str]],
           blockers: list[dict[str, str]]) -> dict[str, Any]:
    return {"land_preflight": {
        "record_version": VERSION, "verdict": verdict, "workflow_status": status,
        "merge_admission": admission, "mode": mode, "expected_head_oid": head,
        "gates": gates, "reasons": reasons, "blockers": blockers,
    }}


def strings(value: Any, field: str, blockers: list[dict[str, str]]) -> tuple[list[str], bool]:
    if not isinstance(value, list):
        issue(blockers, "FIELD_LIST_INVALID", f"{field} must be a list")
        return [], False
    valid = True
    out: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str) or not item:
            valid = False
            issue(blockers, "FIELD_LIST_ITEM_INVALID", f"{field}[{i}] must be a non-empty string")
        else:
            out.append(item)
    if len(out) != len(set(out)):
        valid = False
        issue(blockers, "FIELD_LIST_DUPLICATE", f"{field} must contain unique values")
    return out, valid


def resolution_records(reviews: dict[str, Any], head: Any,
                       blockers: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    reconciliation = reviews.get("reconciliation")
    if not isinstance(reconciliation, dict):
        issue(blockers, "REVIEW_RECONCILIATION_MISSING", "reviews.reconciliation must be an object")
        return [], []
    initial, _ = strings(
        reconciliation.get("initial_unresolved_thread_ids"),
        "reviews.reconciliation.initial_unresolved_thread_ids", blockers,
    )
    raw = reconciliation.get("records")
    if not isinstance(raw, list):
        issue(blockers, "REVIEW_RESOLUTION_RECORDS_INVALID", "reviews.reconciliation.records must be a list")
        return initial, []

    ids: list[str] = []
    for i, record in enumerate(raw):
        if not isinstance(record, dict):
            issue(blockers, "REVIEW_RESOLUTION_RECORD_INVALID", f"resolution record {i} must be an object")
            continue
        tid = record.get("thread_id")
        concern = record.get("concern_ref")
        observed = record.get("observed_head_oid")
        resolved = record.get("resolved_head_oid")
        authority = record.get("law_authority")
        applicability = record.get("current_applicability")
        disposition = record.get("disposition")
        evidence = record.get("evidence_refs")

        if not isinstance(tid, str) or not tid:
            issue(blockers, "REVIEW_RESOLUTION_THREAD_ID_INVALID", f"resolution record {i} requires thread_id")
        else:
            ids.append(tid)
        if not isinstance(concern, str) or not concern:
            issue(blockers, "REVIEW_RESOLUTION_CONCERN_REF_INVALID", f"thread {tid!r} requires concern_ref")
        if not isinstance(observed, str) or not observed:
            issue(blockers, "REVIEW_RESOLUTION_OBSERVED_HEAD_INVALID", f"thread {tid!r} requires observed_head_oid")
        if not isinstance(resolved, str) or not resolved:
            issue(blockers, "REVIEW_RESOLUTION_RESOLVED_HEAD_INVALID", f"thread {tid!r} requires resolved_head_oid")
        elif resolved != head:
            issue(blockers, "REVIEW_RESOLUTION_STALE_HEAD", f"thread {tid!r} was evidenced at {resolved!r}, not {head!r}")
        if authority not in AUTHORITIES:
            issue(blockers, "REVIEW_RESOLUTION_AUTHORITY_INVALID", f"thread {tid!r} has invalid law_authority {authority!r}")
        if applicability not in APPLICABILITY:
            issue(blockers, "REVIEW_RESOLUTION_APPLICABILITY_INVALID", f"thread {tid!r} has invalid applicability {applicability!r}")
        if disposition not in DISPOSITIONS:
            issue(blockers, "REVIEW_RESOLUTION_DISPOSITION_INVALID", f"thread {tid!r} has invalid disposition {disposition!r}")
        if disposition == "fixed-and-evidenced" and observed == resolved:
            issue(blockers, "FIXED_THREAD_HEAD_UNCHANGED", f"thread {tid!r} claims a fix without a successor head")
        if disposition in {"fixed-and-evidenced", "already-satisfied-and-evidenced"} and applicability != "already-excluded":
            issue(blockers, "REVIEW_RESOLUTION_APPLICABILITY_CONTRADICTION", f"thread {tid!r} is not already excluded")
        if disposition == "obsolete-and-evidenced" and applicability not in {"already-excluded", "not-comparable"}:
            issue(blockers, "REVIEW_RESOLUTION_APPLICABILITY_CONTRADICTION", f"thread {tid!r} is not obsolete")
        if disposition == "nonblocking-by-authority" and authority not in {"strengthening", "preference", "new-requirement"}:
            issue(blockers, "REVIEW_RESOLUTION_AUTHORITY_CONTRADICTION", f"thread {tid!r} cannot be nonblocking with {authority!r}")
        if not isinstance(evidence, list) or not evidence or any(not isinstance(x, str) or not x for x in evidence):
            issue(blockers, "REVIEW_RESOLUTION_EVIDENCE_MISSING", f"thread {tid!r} requires evidence_refs")
        if record.get("resolution_readback") is not True:
            issue(blockers, "REVIEW_RESOLUTION_READBACK_MISSING", f"thread {tid!r} requires live resolution readback")

    if len(ids) != len(set(ids)):
        issue(blockers, "REVIEW_RESOLUTION_RECORD_DUPLICATE", "resolution records must contain unique thread IDs")
    return initial, ids


def evaluate(snapshot: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    reasons: list[dict[str, str]] = []
    gates: dict[str, str] = {}
    expected = snapshot.get("expected") if isinstance(snapshot.get("expected"), dict) else {}
    observed = snapshot.get("observed") if isinstance(snapshot.get("observed"), dict) else {}

    if not expected:
        issue(blockers, "SCHEMA_EXPECTED_MISSING", "expected must be an object")
    if not observed:
        issue(blockers, "SCHEMA_OBSERVED_MISSING", "observed must be an object")
    identity_ok = True
    for field in IDENTITY:
        want, got = expected.get(field), observed.get(field)
        if want in (None, ""):
            identity_ok = False
            issue(blockers, "TARGET_EXPECTED_FIELD_MISSING", f"expected.{field} is required")
        elif got in (None, ""):
            identity_ok = False
            issue(blockers, "TARGET_OBSERVED_FIELD_MISSING", f"observed.{field} is required")
        elif want != got:
            identity_ok = False
            code = "TARGET_HEAD_MISMATCH" if field == "head_oid" else "TARGET_IDENTITY_MISMATCH"
            issue(blockers, code, f"{field} expected {want!r} but observed {got!r}")
    gate(gates, "target_identity", identity_ok)
    gate(gates, "exact_head", bool(expected.get("head_oid")) and expected.get("head_oid") == observed.get("head_oid"))

    state = observed.get("state")
    if state not in {"OPEN", "MERGED", "CLOSED"}:
        issue(blockers, "PR_STATE_UNKNOWN", f"unsupported observed.state: {state!r}")
    if state == "MERGED":
        post = bool(observed.get("merged_at")) and bool(observed.get("merge_commit_oid"))
        if not observed.get("merged_at"):
            issue(blockers, "MERGED_AT_MISSING", "MERGED state requires observed.merged_at")
        if not observed.get("merge_commit_oid"):
            issue(blockers, "MERGE_COMMIT_MISSING", "MERGED state requires observed.merge_commit_oid")
        gate(gates, "pr_state", post)
        for name in ("review_inventory", "review_reconciliation", "review_decision", *NA_GATES):
            gate(gates, name, "not-applicable")
        ok = identity_ok and post and not blockers
        return result("pass" if ok else "block", "ready" if ok else "obstructed",
                      "not-applicable", "cleanup-only" if ok else "obstructed",
                      expected.get("head_oid"), gates, reasons, blockers)

    open_ready = state == "OPEN" and observed.get("is_draft") is False
    if state == "CLOSED":
        issue(blockers, "PR_CLOSED_UNMERGED", "closed, unmerged PRs cannot be landed")
    elif state == "OPEN" and observed.get("is_draft") is not False:
        issue(blockers, "PR_DRAFT", "draft PR must be promoted before landing")
    gate(gates, "pr_state", open_ready)

    reviews = snapshot.get("reviews") if isinstance(snapshot.get("reviews"), dict) else {}
    policy = snapshot.get("policy") if isinstance(snapshot.get("policy"), dict) else {}
    if not reviews:
        issue(blockers, "SCHEMA_REVIEWS_MISSING", "reviews must be an object")
    inventory = reviews.get("inventory_complete") is True
    if not inventory:
        issue(blockers, "REVIEW_INVENTORY_INCOMPLETE", "complete paginated review-thread inventory is required")
    gate(gates, "review_inventory", inventory)

    unresolved, _ = strings(reviews.get("unresolved_thread_ids"), "reviews.unresolved_thread_ids", blockers)
    initial, recorded = resolution_records(reviews, observed.get("head_oid"), blockers)
    explicit = reviews.get("explicit_blockers")
    requested = reviews.get("requested_changes_active")
    approvals = policy.get("approvals_required")
    if not isinstance(explicit, int) or isinstance(explicit, bool) or explicit < 0:
        issue(blockers, "EXPLICIT_BLOCKERS_INVALID", "reviews.explicit_blockers must be a non-negative integer")
    if requested not in {True, False}:
        issue(blockers, "REQUESTED_CHANGES_STATE_INVALID", "reviews.requested_changes_active must be true or false")
    if approvals not in {True, False}:
        issue(blockers, "APPROVAL_POLICY_UNKNOWN", "policy.approvals_required must be true or false")

    live, started, done = set(unresolved), set(initial), set(recorded)
    overlap = sorted(live & done)
    if overlap:
        issue(blockers, "REVIEW_RESOLUTION_STATE_CONTRADICTION", f"threads are both unresolved and resolved: {overlap!r}")
    unbound = sorted((live | done) - started)
    if unbound:
        issue(blockers, "REVIEW_RECONCILIATION_SCOPE_MISMATCH", f"threads are absent from initial unresolved set: {unbound!r}")

    if blockers:
        gate(gates, "review_reconciliation", False)
        gate(gates, "review_decision", False)
        for name in NA_GATES:
            gate(gates, name, "not-applicable")
        return result("block", "obstructed", "not-ready", "obstructed",
                      expected.get("head_oid"), gates, reasons, blockers)

    pending = sorted(started - (live | done))
    needs_review = bool(live or pending or requested is True or explicit > 0)
    if live:
        issue(reasons, "REVIEW_THREADS_UNRESOLVED", f"{len(live)} unresolved review thread(s) require reconciliation")
    if pending:
        issue(reasons, "REVIEW_RECONCILIATION_INCOMPLETE", f"threads disappeared without resolution evidence: {pending!r}")
    if requested is True:
        issue(reasons, "REQUESTED_CHANGES_ACTIVE", "active requested changes require review reconciliation")
    if explicit > 0:
        issue(reasons, "EXPLICIT_BLOCKERS_PRESENT", f"observed {explicit} explicit blocker(s)")
    gate(gates, "review_reconciliation", not needs_review)
    gate(gates, "review_decision", requested is False and explicit == 0)
    if needs_review:
        for name in NA_GATES:
            gate(gates, name, "not-applicable")
        return result("continue", "continue", "not-ready", "reconcile-reviews",
                      expected.get("head_oid"), gates, reasons, blockers)

    if approvals is True and reviews.get("review_decision") != "APPROVED":
        issue(blockers, "APPROVAL_MISSING", f"approval required but review_decision is {reviews.get('review_decision')!r}")
        gate(gates, "review_decision", False)

    checks = snapshot.get("checks") if isinstance(snapshot.get("checks"), dict) else {}
    required_expected = checks.get("required_expected")
    allow_skip = policy.get("allow_required_skipping")
    items = checks.get("items")
    checks_ok = required_expected in {True, False} and allow_skip in {True, False} and isinstance(items, list)
    if required_expected not in {True, False}:
        issue(blockers, "REQUIRED_CHECK_POLICY_UNKNOWN", "checks.required_expected must be true or false")
    if allow_skip not in {True, False}:
        issue(blockers, "REQUIRED_SKIP_POLICY_UNKNOWN", "policy.allow_required_skipping must be true or false")
    if not isinstance(items, list):
        issue(blockers, "CHECK_ITEMS_INVALID", "checks.items must be a list")
        items = []
    required: list[dict[str, Any]] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict) or item.get("required") not in {True, False}:
            checks_ok = False
            issue(blockers, "CHECK_ITEM_INVALID", f"checks.items[{i}] is invalid")
        elif item["required"] is True:
            required.append(item)
    if required_expected is True and not required:
        checks_ok = False
        issue(blockers, "REQUIRED_CHECKS_MISSING", "policy expects required checks but none were supplied")
    allowed = {"pass", "skipping"} if allow_skip is True else {"pass"}
    for i, item in enumerate(required):
        bucket = item.get("bucket")
        if bucket not in allowed:
            checks_ok = False
            code = "REQUIRED_CHECK_CANCELLED" if bucket == "cancel" else "REQUIRED_CHECK_NOT_GREEN"
            issue(blockers, code, f"required check {(item.get('name') or i)!r} has bucket {bucket!r}")
    gate(gates, "required_checks", checks_ok)

    merge = snapshot.get("merge") if isinstance(snapshot.get("merge"), dict) else {}
    delivery = merge.get("delivery_mode")
    route = ROUTES.get(delivery)
    if route is None:
        issue(blockers, "DELIVERY_MODE_INVALID", f"invalid merge.delivery_mode {delivery!r}")
    conflict = merge.get("conflict_free") is True
    policy_ok = merge.get("policy_satisfied") is True
    method_ok = merge.get("method_allowed") is True
    admin = merge.get("admin_override")
    current = merge.get("branch_up_to_date")
    strict = merge.get("strict_freshness_required")
    if not conflict:
        issue(blockers, "MERGE_CONFLICT", "merge.conflict_free must be true")
    if not policy_ok:
        issue(blockers, "REPOSITORY_POLICY_BLOCK", "merge.policy_satisfied must be true")
    if not method_ok:
        issue(blockers, "MERGE_METHOD_NOT_ALLOWED", "merge.method_allowed must be true")
    if admin is not False:
        issue(blockers, "ADMIN_OVERRIDE_PROHIBITED", "ordinary $land never performs an administrator bypass")
    if current not in {True, False}:
        issue(blockers, "BRANCH_FRESHNESS_UNKNOWN", "merge.branch_up_to_date must be true or false")
    if strict not in {True, False}:
        issue(blockers, "STRICT_FRESHNESS_POLICY_UNKNOWN", "merge.strict_freshness_required must be true or false")
    gate(gates, "conflict_free", conflict)
    if delivery == "queue":
        gate(gates, "branch_freshness", "not-applicable")
    else:
        freshness = strict is False or (strict is True and current is True)
        if not freshness:
            issue(blockers, "BRANCH_NOT_CURRENT", "strict policy requires the PR branch to be current")
        gate(gates, "branch_freshness", freshness)
    gate(gates, "repository_policy", policy_ok and method_ok and admin is False)

    passed = not blockers
    return result("pass" if passed else "block", "ready" if passed else "obstructed",
                  "ready" if passed else "not-ready", route if passed and route else "obstructed",
                  expected.get("head_oid"), gates, reasons, blockers)


def load(path: str) -> dict[str, Any]:
    value = json.loads(sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("snapshot must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?", default="-", help="JSON file, or - for stdin")
    args = parser.parse_args(argv)
    try:
        out = evaluate(load(args.snapshot))
    except Exception as exc:
        out = result("block", "obstructed", "not-ready", "obstructed", None, {}, [],
                     [{"code": "SNAPSHOT_INVALID", "detail": str(exc)}])
    print(json.dumps(out, indent=2, sort_keys=True))
    return {"pass": 0, "continue": 3}.get(out["land_preflight"]["verdict"], 2)


if __name__ == "__main__":
    raise SystemExit(main())
