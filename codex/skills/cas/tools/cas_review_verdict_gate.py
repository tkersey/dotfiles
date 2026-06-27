#!/usr/bin/env -S uv run python
"""Validate CAS review-session receipts against the CAS review proof boundary.

This is a reference validator for the skill docs. It accepts one JSON object and
checks the fields introduced by the numbered CLI specs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PHASES = {
    "pre_lane_start",
    "lane_started",
    "pre_review_start",
    "review_started",
    "review_waiting",
    "review_terminal",
    "normalized_verdict",
}
STATUSES = {
    "clean",
    "findings",
    "timeout",
    "transport_failure",
    "account_resource_exhausted",
    "parse_mismatch",
    "incomplete",
    "no_attempt",
}
BACKENDS = {"cas-lane", "cas-start-wait", "cas-native-fallback", "cas-receipt-normalized"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    return data


def field(data: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in data:
            return data[name]
    return None


def review_verdict(data: dict[str, Any]) -> dict[str, Any] | None:
    verdict = data.get("reviewVerdict")
    if verdict is None:
        return None
    if not isinstance(verdict, dict):
        raise ValueError("reviewVerdict must be an object")
    return verdict


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    phase = field(data, "reviewAttemptPhase", "phase")
    failure_code = field(data, "failureCode", "failure_code")
    review_thread_id = field(data, "reviewThreadId", "review_thread_id")
    review_attempt_exists = field(data, "reviewAttemptExists", "review_attempt_exists")
    proof_verdict_exists = field(data, "proofVerdictExists", "proof_verdict_exists")
    verdict = review_verdict(data)

    if phase is None:
        errors.append("missing reviewAttemptPhase")
    elif phase not in PHASES:
        errors.append(f"invalid reviewAttemptPhase: {phase}")

    expected_attempt = review_thread_id is not None
    if review_attempt_exists is not None and bool(review_attempt_exists) != expected_attempt:
        errors.append("reviewAttemptExists must equal reviewThreadId != null")

    if phase == "pre_review_start":
        if review_thread_id is not None:
            errors.append("pre_review_start must not have reviewThreadId")
        if review_attempt_exists not in (False, None):
            errors.append("pre_review_start must have reviewAttemptExists=false")

    if failure_code == "pre_review_lane_transport_lost":
        if phase != "pre_review_start":
            errors.append("pre_review_lane_transport_lost requires reviewAttemptPhase=pre_review_start")
        if review_thread_id is not None:
            errors.append("pre_review_lane_transport_lost must not have reviewThreadId")
        for name in ("laneId", "managedServerPid", "reviewCount"):
            if name not in data:
                errors.append(f"pre_review_lane_transport_lost missing {name}")

    if failure_code == "account_resource_exhausted":
        if field(data, "retryableSameTupleNow", "retryable_same_tuple_now") is not False:
            errors.append("account_resource_exhausted requires retryableSameTupleNow=false")

    if verdict is not None:
        status = verdict.get("status")
        backend = verdict.get("backendClass")
        if status not in STATUSES:
            errors.append(f"invalid reviewVerdict.status: {status}")
        if backend not in BACKENDS:
            errors.append(f"invalid reviewVerdict.backendClass: {backend}")
        if status in {"clean", "findings"}:
            for name in ("baseSha", "headSha", "targetFingerprint", "reviewThreadId", "reviewTurnId"):
                if not verdict.get(name):
                    errors.append(f"reviewVerdict.status={status} missing {name}")
            if status == "clean" and verdict.get("findingCount") not in (0, None):
                errors.append("clean reviewVerdict must have findingCount=0")
            if status == "clean" and verdict.get("failureCode") is not None:
                errors.append("clean reviewVerdict must not have failureCode")
        if status == "no_attempt" and verdict.get("reviewThreadId") is not None:
            errors.append("no_attempt reviewVerdict must not have reviewThreadId")
        if proof_verdict_exists is True and status not in {"clean", "findings", "account_resource_exhausted", "parse_mismatch"}:
            errors.append("proofVerdictExists=true is inconsistent with reviewVerdict.status")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    try:
        data = load_json(args.json_file)
        errors = validate(data)
    except Exception as exc:  # noqa: BLE001
        errors = [str(exc)]

    ok = not errors
    result = {"ok": ok, "errors": errors, "path": str(args.json_file)}
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if ok:
            print(f"ok: {args.json_file}")
        else:
            print(f"failed: {args.json_file}", file=sys.stderr)
            for err in errors:
                print(f"- {err}", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
