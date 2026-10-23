#!/usr/bin/env python3
"""Check a projection of the existing campaign working set; no storage or effects.

Read one JSON object from stdin and write one JSON result to stdout. These checks
do not read provider state, authenticate receipts, or establish review adequacy.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from typing import Any


STATES = {
    "queued", "launched", "running", "needs-input", "completed", "accepted",
    "incomplete", "failed", "stale",
}
IDENTITY_FIELDS = {
    "schema", "mode", "repo", "pr", "campaign_id", "assignment_id",
    "campaign_context_id", "campaign_seed_thread_id", "target", "base",
    "candidate", "view",
}
EPOCH_FIELDS = (
    "host", "viewer_id", "pr_node_id", "repo", "pr", "base_tip", "base", "candidate",
)
CAMPAIGN_FIELDS = ("campaign_id", "campaign_context_id", "campaign_seed_thread_id")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def nonempty(value: Any, field: str) -> None:
    require(isinstance(value, str) and bool(value), f"{field} must be nonempty text")


def merge_policy(source: dict[str, Any]) -> str | None:
    """Absence preserves a historical binding; it never selects today's default."""
    if "merge_policy" not in source:
        return None
    value = source["merge_policy"]
    require(isinstance(value, str) and value in ("pragmatic", "pedantic"),
            "merge_policy must be pragmatic or pedantic when supplied")
    return value


def execution_mode(source: dict[str, Any]) -> str | None:
    """Keep historical fork bindings absent rather than relabeling them."""
    if "execution_mode" not in source:
        return None
    value = source["execution_mode"]
    require(isinstance(value, str) and value in ("fork", "subagents"),
            "execution_mode must be fork or subagents when supplied")
    return value


def rows_by_id(rows: Any) -> dict[str, dict[str, Any]]:
    require(isinstance(rows, list), "assignments must be a list")
    result = {}
    paths = set()
    for row in rows:
        require(isinstance(row, dict), "assignment must be an object")
        assignment_id, path = row["assignment_id"], row["path"]
        nonempty(assignment_id, "assignment_id")
        nonempty(path, "path")
        require(assignment_id not in result and path not in paths, "duplicate assignment or path")
        require(row["state"] in STATES, "unknown assignment state")
        require(type(row["active"]) is bool and type(row["runnable"]) is bool,
                "active and runnable must be observed booleans")
        require(not (row["active"] and row["runnable"]), "an active attempt cannot be redispatched")
        if row["state"] in {"launched", "running"}:
            require(row["active"], "recover the active attempt before changing its state")
        if row["state"] in {"queued", "completed", "accepted", "incomplete", "failed", "stale"}:
            require(not row["active"], "terminal or queued assignment still has an active attempt")
        if row["state"] in {"accepted", "stale"}:
            require(not row["runnable"], "accepted or stale work is not runnable")
        result[assignment_id] = row
        paths.add(path)
    return result


def check_selection(selected: Any, rows: list[dict[str, Any]]) -> None:
    require(isinstance(selected, list), "selected_paths must be a list")
    for path in selected:
        nonempty(path, "selected path")
    require(len(selected) == len(set(selected)), "duplicate selected path")
    require(set(selected) == {row["path"] for row in rows},
            "assignments must cover the exact frozen selected set")


def schedule(payload: dict[str, Any]) -> dict[str, Any]:
    """Tail-requeue an eligible idle assignment and select the oldest ready work."""
    check_epoch(payload["bound_epoch"], payload["observed_epoch"])
    rows = copy.deepcopy(payload["assignments"])
    assignments = rows_by_id(rows)
    check_selection(payload["selected_paths"], rows)
    queue = list(payload["queue"])
    require(isinstance(payload["queue"], list), "queue must be a FIFO list")
    require(all(isinstance(item, str) for item in queue), "queue entries must be assignment IDs")
    require(len(queue) == len(set(queue)), "duplicate queue entry")
    require(set(queue) == {key for key, row in assignments.items() if row["state"] == "queued"},
            "queue must contain exactly the queued assignments; recover missing order")
    limit = payload["concurrency"]
    require(type(limit) is int and 1 <= limit <= 20, "concurrency must be in 1..20")

    assignment_id = payload.get("requeue")
    if assignment_id is not None:
        require(assignment_id in assignments, "unknown requeue assignment")
        row = assignments[assignment_id]
        require(not row["active"] and row["runnable"], "requeue requires idle, runnable work")
        require(row["state"] in {"queued", "completed", "incomplete", "failed", "needs-input"},
                "only unfinished current work can be requeued")
        if assignment_id not in queue:
            queue.append(assignment_id)
            row["state"] = "queued"

    active = sum(row["active"] for row in rows)
    require(active <= limit, "active attempts exceed concurrency")
    ready = [key for key in queue if assignments[key]["runnable"]]
    return {
        "assignments": rows, "queue": queue, "active_count": active,
        "dispatchable": ready[:limit - active],
    }


def check_epoch(bound: dict[str, Any], observed: dict[str, Any]) -> None:
    require(observed["state"] == "OPEN", "PR is not OPEN")
    for field in EPOCH_FIELDS:
        if field == "pr":
            require(type(bound[field]) is int and bound[field] > 0, "pr must be a positive integer")
            require(type(observed[field]) is int, "observed pr must be an integer")
        else:
            nonempty(bound[field], field)
            nonempty(observed[field], f"observed {field}")
        require(bound[field] == observed[field], f"changed epoch field: {field}")


def check_report(payload: dict[str, Any]) -> dict[str, Any]:
    """Check identity/attempt consistency, not source authenticity or adjudication."""
    bound, observed = payload["bound_epoch"], payload["observed_epoch"]
    check_epoch(bound, observed)
    expected = payload["expected_identity"]
    require(isinstance(expected, dict), "expected_identity must be an object")
    execution = execution_mode(expected)
    fields = IDENTITY_FIELDS | ({"execution_mode"} if execution is not None else set())
    if execution == "subagents":
        fields |= {"attempt_id"}
    require(set(expected) in (fields, fields | {"merge_policy"}),
            "expected_identity needs the fixed v1 single-file bindings for its execution mode")
    for field, value in expected.items():
        if field == "pr":
            require(type(value) is int and value > 0, "pr must be a positive integer")
        elif field == "campaign_seed_thread_id" and execution == "subagents":
            require(value is None, "subagents cannot claim a campaign seed thread")
        else:
            nonempty(value, field)
    require(expected["schema"] == "elenctic-review-identity/v1"
            and expected["mode"] == "single-file" and expected["view"] == "pr-head",
            "expected identity is not a v1 PR-head file assignment")
    for field in ("repo", "pr", "base", "candidate"):
        require(expected[field] == bound[field], f"assignment disagrees with epoch: {field}")

    active, report = payload["active_attempt"], payload["report"]
    identity = report["identity"]
    require(isinstance(identity, dict), "report identity must be an object")
    require(execution_mode(identity) == execution,
            "report execution_mode differs from its assignment binding")
    if execution == "subagents":
        nonempty(active.get("attempt_id"), "active attempt_id")
        require(active["attempt_id"] == expected["attempt_id"],
                "active attempt_id differs from its assignment binding")
    else:
        require("attempt_id" not in active and "attempt_id" not in identity,
                "attempt_id requires subagents execution")
    for field in ("worker_id", "turn_id"):
        require(field in active, f"active {field} is required")
        if not (field == "turn_id" and execution == "subagents" and active[field] is None):
            nonempty(active[field], f"active {field}")
        require(field in report and type(report[field]) is type(active[field])
                and report[field] == active[field],
                f"report is not from the recorded active {field}")
    require(merge_policy(identity) == merge_policy(expected),
            "report merge_policy differs from its assignment binding")
    for field, value in expected.items():
        require(type(identity.get(field)) is type(value) and identity[field] == value,
                f"report identity mismatch: {field}")
    coverage, verdict = identity["coverage"], identity["verdict"]
    require((coverage, verdict) in {
        ("complete", "APPROVE"), ("complete", "BLOCKED"),
        ("incomplete", "INCOMPLETE"), ("incomplete", "BLOCKED"),
    }, "contradictory coverage and verdict")
    require(report["decision"] == verdict, "textual decision differs from identity verdict")
    result = {
        "assignment_id": expected["assignment_id"], "worker_id": active["worker_id"],
        "turn_id": active["turn_id"], "coverage_claim": coverage, "verdict_claim": verdict,
        "completion_claim_consistent": coverage == "complete",
    }
    if execution is not None:
        result["execution_mode"] = execution
    if execution == "subagents":
        result["attempt_id"] = active["attempt_id"]
    return result


def coverage(payload: dict[str, Any]) -> dict[str, Any]:
    """Count caller-admitted reports once per frozen selected path; never emit a verdict."""
    check_epoch(payload["bound_epoch"], payload["observed_epoch"])
    selected = payload["selected_paths"]
    rows = payload["assignments"]
    assignments = rows_by_id(rows)
    check_selection(selected, rows)
    nonempty(payload["campaign_id"], "campaign_id")
    policy = merge_policy(payload)
    execution = execution_mode(payload)
    if execution == "subagents":
        require(payload["campaign_seed_thread_id"] is None,
                "subagents cannot claim a campaign seed thread")
    states = Counter(row["state"] for row in rows)
    verdicts = Counter()
    for assignment_id, row in assignments.items():
        if row["state"] != "accepted":
            continue
        require(row["expected_identity"]["assignment_id"] == assignment_id
                and row["expected_identity"]["target"] == row["path"],
                "accepted identity is bound to another assignment or path")
        for field in CAMPAIGN_FIELDS:
            require(row["expected_identity"][field] == payload[field],
                    f"accepted report belongs to another {field}")
        require(merge_policy(row["expected_identity"]) == policy,
                "accepted report belongs to another merge_policy binding")
        require(execution_mode(row["expected_identity"]) == execution,
                "accepted report belongs to another execution_mode binding")
        claim = check_report({
            "bound_epoch": payload["bound_epoch"], "observed_epoch": payload["observed_epoch"],
            "expected_identity": row["expected_identity"], "active_attempt": row["active_attempt"],
            "report": row["accepted_report"],
        })
        require(claim["completion_claim_consistent"], "accepted report is incomplete")
        verdicts[claim["verdict_claim"]] += 1
    return {
        "selected_files": len(selected), "complete_files": states["accepted"],
        "state_counts": {state: states[state] for state in sorted(STATES)},
        "complete_verdict_counts": {verdict: verdicts[verdict] for verdict in ("APPROVE", "BLOCKED")},
        "has_selected_files": bool(selected),
        "all_selected_files_have_accepted_reports": states["accepted"] == len(selected),
    }


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("schedule", "check-report", "coverage"))
    args = parser.parse_args()
    operations = {"schedule": schedule, "check-report": check_report, "coverage": coverage}
    try:
        payload = json.load(sys.stdin, object_pairs_hook=unique_object)
        require(isinstance(payload, dict), "input must be a JSON object")
        result = operations[args.operation](payload)
    except (KeyError, TypeError, ValueError) as error:
        parser.exit(2, f"elenctic campaign state: {error}\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
