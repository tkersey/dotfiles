#!/usr/bin/env -S uv run python
"""Validate CRTL-v1 CAS review tuple locks."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STATES = {
    "starting_lane",
    "pre_review_start_failed",
    "review_started",
    "waiting",
    "terminal",
    "normalized",
    "account_resource_exhausted",
    "stale",
}
ACTIVE_STATES = {"review_started", "waiting"}


def validate(lock: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if lock.get("lockVersion") != "CRTL-v1":
        errors.append("lockVersion must be CRTL-v1")
    for name in (
        "tupleHash",
        "repoRealpath",
        "baseSha",
        "headSha",
        "targetFingerprint",
        "resolvedCodexPath",
        "resolvedCodexVersion",
        "accountFingerprint",
        "state",
    ):
        if not lock.get(name):
            errors.append(f"missing {name}")
    state = lock.get("state")
    if state not in STATES:
        errors.append(f"invalid state: {state}")
    if state in ACTIVE_STATES and not lock.get("reviewThreadId"):
        errors.append(f"{state} requires reviewThreadId")
    if state == "pre_review_start_failed" and lock.get("reviewThreadId") is not None:
        errors.append("pre_review_start_failed must not have reviewThreadId")
    if state == "account_resource_exhausted" and lock.get("lastFailureCode") != "account_resource_exhausted":
        errors.append("account_resource_exhausted state requires lastFailureCode=account_resource_exhausted")
    if lock.get("expiresAtUnixS", 0) and lock.get("updatedAtUnixS", 0) and lock["expiresAtUnixS"] < lock["updatedAtUnixS"]:
        errors.append("expiresAtUnixS must be >= updatedAtUnixS")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lock_json", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    try:
        lock = json.loads(args.lock_json.read_text(encoding="utf-8"))
        if not isinstance(lock, dict):
            raise ValueError("top-level lock must be an object")
        errors = validate(lock)
    except Exception as exc:  # noqa: BLE001
        errors = [str(exc)]
    ok = not errors
    result = {"ok": ok, "errors": errors, "path": str(args.lock_json)}
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if ok:
            print(f"ok: {args.lock_json}")
        else:
            print(f"failed: {args.lock_json}", file=sys.stderr)
            for err in errors:
                print(f"- {err}", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
