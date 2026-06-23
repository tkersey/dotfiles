#!/usr/bin/env python3
"""Validate actuation_state / ASR-v2 and its ship gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

PR_MODES = {"ready", "draft", "update-existing", "promote-draft", "blocked"}
PROOF_STATES = {"pass", "fail", "missing", "not-run", "stale", "blocked"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    body = value.get("actuation_state", value) if isinstance(value, dict) else value
    if not isinstance(body, dict):
        raise ValueError("actuation_state must be an object")
    return body


def obj(parent: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key}:must-be-object")
        return {}
    return value


def arr(parent: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        errors.append(f"{key}:must-be-list")
        return []
    return value


def int_field(parent: dict[str, Any], key: str, errors: list[str], prefix: str) -> int:
    value = parent.get(key)
    if not isinstance(value, int) or value < 0:
        errors.append(f"{prefix}.{key}")
        return 0
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--mode", choices=("status", "ship"), default="status")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        state = load(args.file)
    except Exception as exc:
        print(json.dumps({"asr_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if state.get("run_version") != "ASR-v2":
        errors.append("run_version")
    for key in ("run_id", "plan_source", "objective", "repository"):
        if not state.get(key):
            errors.append(key)

    artifact = obj(state, "artifact_state", errors)
    for key in ("branch", "base", "head", "dirty_fingerprint"):
        if not artifact.get(key):
            errors.append(f"artifact_state.{key}")

    control = obj(state, "control", errors)
    for key in ("plan_ref", "gcr_id"):
        if not control.get(key):
            errors.append(f"control.{key}")
    if control.get("gcr_current") is not True:
        errors.append("control.gcr_current")
    if control.get("execution_allowed") is not True:
        errors.append("control.execution_allowed")
    debt = control.get("blocking_debt")
    if not isinstance(debt, list):
        errors.append("control.blocking_debt")
        debt = []
    if debt:
        errors.append("control.blocking_debt:not-empty")
    if control.get("projection_valid") is not True:
        errors.append("control.projection_valid")
    if not isinstance(control.get("selected_task_ids"), list):
        errors.append("control.selected_task_ids")

    graph = obj(state, "graph_state", errors)
    counts = {
        key: int_field(graph, key, errors, "graph_state")
        for key in ("total", "complete", "blocked", "deferred", "open")
    }
    if counts["complete"] + counts["blocked"] + counts["deferred"] + counts["open"] != counts["total"]:
        errors.append("graph_state:counts-do-not-sum")

    frontiers = obj(state, "frontiers", errors)
    afr_refs = frontiers.get("afr_refs")
    if not isinstance(afr_refs, list):
        errors.append("frontiers.afr_refs")
        afr_refs = []
    frontier_counts = {
        key: int_field(frontiers, key, errors, "frontiers")
        for key in ("terminal", "return_to_frontier", "blocked", "open")
    }
    if sum(frontier_counts.values()) != len(afr_refs):
        errors.append("frontiers:counts-do-not-match-refs")

    proof = obj(state, "proof", errors)
    for key in ("focused", "wave", "closure"):
        if proof.get(key) not in PROOF_STATES:
            errors.append(f"proof.{key}")
    if not proof.get("closure_artifact_fingerprint"):
        errors.append("proof.closure_artifact_fingerprint")
    stale = proof.get("stale_receipts")
    if not isinstance(stale, list):
        errors.append("proof.stale_receipts")
        stale = []

    surface = obj(state, "surface", errors)
    for key in (
        "helpers_added",
        "branches_added",
        "fields_added",
        "public_symbols_added",
        "fallback_paths_added",
        "test_families_added",
    ):
        int_field(surface, key, errors, "surface")
    arr(surface, "surfaces_retired", errors)

    ship = obj(state, "ship", errors)
    if ship.get("ship_allowed") not in {True, False}:
        errors.append("ship.ship_allowed")
    if ship.get("pr_mode") not in PR_MODES:
        errors.append("ship.pr_mode")
    if not ship.get("pr_mode_reason"):
        errors.append("ship.pr_mode_reason")
    if not ship.get("draft_allowed_reason"):
        errors.append("ship.draft_allowed_reason")
    arr(state, "residual_risk", errors)

    ship_ready = (
        not errors
        and control.get("gcr_current") is True
        and control.get("projection_valid") is True
        and not debt
        and counts["open"] == 0
        and counts["blocked"] == 0
        and counts["deferred"] == 0
        and frontier_counts["open"] == 0
        and frontier_counts["return_to_frontier"] == 0
        and frontier_counts["blocked"] == 0
        and proof.get("focused") == "pass"
        and proof.get("wave") == "pass"
        and proof.get("closure") == "pass"
        and not stale
        and ship.get("pr_mode") in {"ready", "update-existing", "promote-draft"}
    )

    if args.mode == "ship":
        if ship.get("ship_allowed") is not True:
            errors.append("ship.ship_allowed:not-true")
        if not ship_ready:
            errors.append("ship:gate-not-satisfied")
        if ship.get("pr_mode") == "draft":
            errors.append("ship:draft-not-full-closure-mode")

    if ship.get("ship_allowed") is True and not ship_ready:
        warnings.append("ship_allowed:true-but-derived-gate-not-ready")

    result = {
        "asr_gate": {
            "verdict": "pass" if not errors else "fail",
            "mode": args.mode,
            "run_id": state.get("run_id"),
            "ship_ready": ship_ready,
            "pr_mode": ship.get("pr_mode"),
            "graph_state": counts,
            "frontier_state": frontier_counts,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
