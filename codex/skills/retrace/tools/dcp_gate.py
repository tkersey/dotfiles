#!/usr/bin/env python3
"""Validate decision_context_packet / DCP-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

RECONSTRUCTION = {"exact", "head_only", "transcript_only", "unavailable"}
ANCHORS = ("pre_decision", "post_decision_pre_outcome", "outcome_aware")


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("packet must be an object")
    body = value.get("decision_context_packet", value)
    if not isinstance(body, dict):
        raise ValueError("decision_context_packet must be an object")
    return body


def require_object(parent: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key}:must-be-object")
        return {}
    return value


def require_list(parent: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        errors.append(f"{key}:must-be-list")
        return []
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        packet = load(args.file)
    except Exception as exc:
        print(json.dumps({"dcp_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if packet.get("packet_version") != "DCP-v1":
        errors.append("packet_version")
    if not packet.get("packet_id"):
        errors.append("packet_id")

    source = require_object(packet, "source", errors)
    if not any(source.get(key) for key in ("session_id", "rollout_path", "thread_id")):
        errors.append("source:session-id-rollout-path-or-thread-id-required")
    if not source.get("decision_id"):
        errors.append("source.decision_id")

    artifact = require_object(packet, "artifact_state", errors)
    if artifact.get("reconstructability") not in RECONSTRUCTION:
        errors.append("artifact_state.reconstructability")

    episode = require_object(packet, "episode", errors)
    if not episode.get("question"):
        errors.append("episode.question")
    if not episode.get("selected_route"):
        warnings.append("episode.selected_route:unknown")
    for key in (
        "rejected_routes",
        "explicit_rationale",
        "explicit_assumptions",
        "evidence_refs",
        "tools_and_artifacts",
        "skills_and_instructions",
        "outcome_refs",
    ):
        require_list(episode, key, errors)

    turns = require_object(packet, "turns", errors)
    total = turns.get("total_turns")
    decision = turns.get("decision_turn_index")
    outcome = turns.get("first_outcome_turn_index")
    if not isinstance(total, int) or total < 1:
        errors.append("turns.total_turns")
        total = 0
    if not isinstance(decision, int) or not (1 <= decision <= max(total, 1)):
        errors.append("turns.decision_turn_index")
        decision = 0
    if outcome is not None and (
        not isinstance(outcome, int) or not (decision < outcome <= max(total, 1))
    ):
        errors.append("turns.first_outcome_turn_index")
    if not turns.get("source_turn_digest"):
        errors.append("turns.source_turn_digest")

    anchors = require_object(packet, "anchors", errors)
    available = {}
    for name in ANCHORS:
        anchor = anchors.get(name)
        if not isinstance(anchor, dict):
            errors.append(f"anchors.{name}:must-be-object")
            continue
        is_available = anchor.get("available")
        if not isinstance(is_available, bool):
            errors.append(f"anchors.{name}.available")
            continue
        available[name] = is_available
        keep = anchor.get("keep_through_turn_index")
        drop = anchor.get("drop_last_n_turns")
        digest = anchor.get("anchor_digest")
        if is_available:
            if not isinstance(keep, int) or keep < 0 or keep > total:
                errors.append(f"anchors.{name}.keep_through_turn_index")
            if not isinstance(drop, int) or drop < 0:
                errors.append(f"anchors.{name}.drop_last_n_turns")
            if isinstance(keep, int) and isinstance(drop, int) and keep + drop != total:
                errors.append(f"anchors.{name}:keep-plus-drop-must-equal-total")
            if not digest:
                errors.append(f"anchors.{name}.anchor_digest")
        elif digest:
            warnings.append(f"anchors.{name}:unavailable-with-digest")

    pre = anchors.get("pre_decision", {})
    if available.get("pre_decision") and isinstance(pre.get("keep_through_turn_index"), int):
        if pre["keep_through_turn_index"] >= decision:
            errors.append("anchors.pre_decision:must-end-before-decision")

    post = anchors.get("post_decision_pre_outcome", {})
    if available.get("post_decision_pre_outcome") and isinstance(post.get("keep_through_turn_index"), int):
        keep = post["keep_through_turn_index"]
        if keep < decision:
            errors.append("anchors.post_decision_pre_outcome:must-include-decision")
        if isinstance(outcome, int) and keep >= outcome:
            errors.append("anchors.post_decision_pre_outcome:must-precede-outcome")

    full = anchors.get("outcome_aware", {})
    if available.get("outcome_aware") and full.get("keep_through_turn_index") != total:
        warnings.append("anchors.outcome_aware:does-not-include-full-history")

    contamination = require_object(packet, "contamination", errors)
    for key in ("injected_skill_blocks", "generated_reports", "current_audit_prompt", "quoted_material"):
        if not isinstance(contamination.get(key), bool):
            errors.append(f"contamination.{key}")

    require_list(packet, "limitations", errors)

    result = {
        "dcp_gate": {
            "verdict": "pass" if not errors else "fail",
            "packet_id": packet.get("packet_id"),
            "anchors_available": [name for name, yes in available.items() if yes],
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
