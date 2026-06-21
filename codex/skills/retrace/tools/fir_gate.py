#!/usr/bin/env python3
"""Validate fork_inquiry_receipt / FIR-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

HORIZONS = {"pre_decision", "post_decision_pre_outcome", "outcome_aware"}
OUTCOME_BLIND = {"pre_decision", "post_decision_pre_outcome"}
TERMINAL = {"completed", "failed", "interrupted", "timeout", "budget_exhausted"}
WORKSPACES = {"exact", "head_only", "transcript_only", "unavailable"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    body = value.get("fork_inquiry_receipt", value) if isinstance(value, dict) else value
    if not isinstance(body, dict):
        raise ValueError("fork_inquiry_receipt must be an object")
    return body


def obj(parent: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key}:object")
        return {}
    return value


def lst(parent: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        errors.append(f"{key}:list")
        return []
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        receipt = load(args.file)
    except Exception as exc:
        print(json.dumps({"fir_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if receipt.get("receipt_version") != "FIR-v1":
        errors.append("receipt_version")
    for key in ("receipt_id", "inquiry_id", "lane_id"):
        if not receipt.get(key):
            errors.append(key)

    source = obj(receipt, "source", errors)
    if not source.get("capsule_id"):
        errors.append("source.capsule_id")
    if not any(source.get(key) for key in ("source_thread_id", "source_rollout_path")):
        errors.append("source.thread-or-rollout")
    if not source.get("source_turn_digest"):
        errors.append("source.source_turn_digest")

    fork = obj(receipt, "fork", errors)
    if not fork.get("fork_thread_id"):
        errors.append("fork.fork_thread_id")
    if (
        source.get("source_thread_id")
        and fork.get("fork_thread_id") == source.get("source_thread_id")
    ):
        errors.append("fork:must-differ-from-source")
    if source.get("source_thread_id") and fork.get("forked_from_id") != source.get("source_thread_id"):
        errors.append("fork.forked_from_id:mismatch")
    for key in ("model", "model_provider", "codex_version"):
        if not fork.get(key):
            warnings.append(f"fork.{key}:missing")

    anchor = obj(fork, "anchor", errors)
    horizon = anchor.get("temporal_horizon")
    if horizon not in HORIZONS:
        errors.append("fork.anchor.temporal_horizon")
    before = anchor.get("turns_before")
    dropped = anchor.get("turns_dropped")
    after = anchor.get("turns_after")
    if not all(isinstance(value, int) and value >= 0 for value in (before, dropped, after)):
        errors.append("fork.anchor.turn-counts")
    elif before - dropped != after:
        errors.append("fork.anchor:before-minus-dropped-must-equal-after")
    if not anchor.get("anchor_digest_expected") or not anchor.get("anchor_digest_observed"):
        errors.append("fork.anchor.digest")
    if anchor.get("anchor_digest_expected") != anchor.get("anchor_digest_observed"):
        errors.append("fork.anchor.digest-mismatch")
    if horizon in OUTCOME_BLIND and anchor.get("exact") is not True:
        errors.append("fork.anchor:outcome-blind-must-be-exact")

    if fork.get("ephemeral") is not True:
        warnings.append("fork.ephemeral:not-true")
    permissions = str(fork.get("permissions", "")).lower()
    sandbox = str(fork.get("sandbox", "")).lower()
    if "read" not in permissions and "read" not in sandbox:
        errors.append("fork.permissions:not-read-only")
    if str(fork.get("approval_policy", "")).lower() not in {"never", "deny", "denied"}:
        warnings.append("fork.approval_policy:not-clearly-never")

    workspace = obj(receipt, "workspace_reconstruction", errors)
    if workspace.get("mode") not in WORKSPACES:
        errors.append("workspace_reconstruction.mode")
    if workspace.get("network_allowed") is not False:
        errors.append("workspace_reconstruction.network_allowed")
    if workspace.get("mode") == "transcript_only" and workspace.get("tools_allowed") is not False:
        errors.append("workspace_reconstruction:transcript-only-tools")
    lst(workspace, "limitations", errors)

    inquiry = obj(receipt, "inquiry", errors)
    if not inquiry.get("mode") or not inquiry.get("question"):
        errors.append("inquiry.mode-or-question")
    for key in ("evidence_allowed", "evidence_withheld"):
        lst(inquiry, key, errors)
    if inquiry.get("status") not in TERMINAL:
        errors.append("inquiry.status")
    if not inquiry.get("turn_id"):
        errors.append("inquiry.turn_id")

    answer = obj(receipt, "answer", errors)
    for key in (
        "rejected_routes",
        "evidence_refs",
        "assumptions",
        "alternatives",
        "route_flip_conditions",
        "unsupported_claims",
    ):
        lst(answer, key, errors)
    if not answer.get("selected_route"):
        warnings.append("answer.selected_route:unknown")
    if horizon in OUTCOME_BLIND and answer.get("hindsight_available") is not False:
        errors.append("answer.hindsight_available:outcome-blind-must-be-false")
    if horizon == "outcome_aware" and answer.get("hindsight_available") is not True:
        errors.append("answer.hindsight_available:outcome-aware-must-be-true")
    if not answer.get("final_text_ref"):
        errors.append("answer.final_text_ref")

    lifecycle = obj(receipt, "lifecycle", errors)
    if not lifecycle.get("event_log_ref"):
        errors.append("lifecycle.event_log_ref")
    cleanup = lifecycle.get("cleanup_status")
    if not cleanup:
        errors.append("lifecycle.cleanup_status")
    if fork.get("ephemeral") is not True and cleanup not in {
        "deleted",
        "archived",
        "cleanup_complete",
    }:
        errors.append("lifecycle:persisted-fork-not-cleaned")

    gate = obj(receipt, "gate", errors)
    required_gates = (
        "lineage_valid",
        "anchor_valid",
        "permissions_valid",
        "hindsight_label_valid",
        "answer_complete",
        "receipt_valid",
    )
    for key in required_gates:
        if gate.get(key) is not True:
            errors.append(f"gate.{key}")

    result = {
        "fir_gate": {
            "verdict": "pass" if not errors else "fail",
            "receipt_id": receipt.get("receipt_id"),
            "horizon": horizon,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
