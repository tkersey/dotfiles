#!/usr/bin/env -S uv run python
"""Classify CAS review-session receipts into review transport facts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def iter_json_records(path: Path) -> Iterable[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    stripped = raw.strip()
    if not stripped:
        return
    if stripped.startswith("["):
        data = json.loads(stripped)
        for item in data:
            if isinstance(item, dict):
                yield item
        return
    if stripped.startswith("{") and "\n" not in stripped:
        data = json.loads(stripped)
        if isinstance(data, dict):
            yield data
        return
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        if isinstance(data, dict):
            yield data


def pick(obj: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in obj:
            return obj[key]
    return None


def contains_usage_limit(obj: Any) -> bool:
    if obj is None:
        return False
    text = json.dumps(obj, sort_keys=True) if not isinstance(obj, str) else obj
    return "usageLimitExceeded" in text or "quota exceeded" in text or "rate limit exceeded" in text


def classify(receipt: dict[str, Any]) -> dict[str, Any]:
    verdict = receipt.get("reviewVerdict") if isinstance(receipt.get("reviewVerdict"), dict) else None
    failure_code = pick(receipt, "failureCode", "failure_code") or (verdict or {}).get("failureCode")
    review_thread_id = pick(receipt, "reviewThreadId", "review_thread_id") or (verdict or {}).get("reviewThreadId")
    review_count = pick(receipt, "reviewCount", "review_count")
    last_review_thread = pick(receipt, "lastReviewThreadId", "last_review_thread_id")
    last_head = pick(receipt, "lastHeadSha", "last_head_sha")

    if contains_usage_limit(receipt) or failure_code == "account_resource_exhausted":
        phase = "review_terminal" if review_thread_id else "pre_review_start"
        return {
            "classification": "account_resource_exhausted",
            "failureCode": "account_resource_exhausted",
            "failureClass": "account_resource",
            "reviewAttemptPhase": phase,
            "reviewAttemptExists": review_thread_id is not None,
            "tupleVerdictExists": False,
            "reviewThreadId": review_thread_id,
            "retryableSameTupleNow": False,
        }

    if failure_code in {"pre_review_lane_transport_lost", "lane_transport_lost"} and (review_count in (0, None)) and not review_thread_id and not last_review_thread and not last_head:
        return {
            "classification": "pre_review_lane_transport_lost",
            "failureCode": "pre_review_lane_transport_lost",
            "failureClass": "transport",
            "reviewAttemptPhase": "pre_review_start",
            "reviewAttemptExists": False,
            "tupleVerdictExists": False,
            "reviewThreadId": None,
            "retryableSameTupleNow": True,
        }

    if verdict:
        status = verdict.get("status")
        return {
            "classification": f"review_verdict_{status}",
            "failureCode": verdict.get("failureCode"),
            "failureClass": "review_verdict",
            "reviewAttemptPhase": "normalized_verdict",
            "reviewAttemptExists": bool(verdict.get("reviewThreadId") or review_thread_id),
            "tupleVerdictExists": status in {"clean", "findings", "account_resource_exhausted", "parse_mismatch"},
            "reviewThreadId": verdict.get("reviewThreadId") or review_thread_id,
            "retryableSameTupleNow": status not in {"timeout", "account_resource_exhausted"},
        }

    if review_thread_id:
        return {
            "classification": "review_attempt_unormalized",
            "failureCode": failure_code,
            "failureClass": "review_attempt",
            "reviewAttemptPhase": "review_started",
            "reviewAttemptExists": True,
            "tupleVerdictExists": False,
            "reviewThreadId": review_thread_id,
            "retryableSameTupleNow": False,
        }

    return {
        "classification": "unknown_no_attempt",
        "failureCode": failure_code,
        "failureClass": "unknown",
        "reviewAttemptPhase": pick(receipt, "reviewAttemptPhase", "phase") or "pre_lane_start",
        "reviewAttemptExists": False,
        "tupleVerdictExists": False,
        "reviewThreadId": None,
        "retryableSameTupleNow": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt_file", type=Path)
    parser.add_argument("--format", choices=["json", "jsonl"], default="json")
    args = parser.parse_args()
    rows = [{"sourceIndex": idx, **classify(record)} for idx, record in enumerate(iter_json_records(args.receipt_file))]
    if args.format == "jsonl":
        for row in rows:
            print(json.dumps(row, sort_keys=True))
    else:
        print(json.dumps(rows, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
