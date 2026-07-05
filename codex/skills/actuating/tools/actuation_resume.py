#!/usr/bin/env python3
"""Render a compact compaction-safe actuation resume packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def body(path: str, wrapper: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    result = value.get(wrapper, value) if isinstance(value, dict) else value
    if not isinstance(result, dict):
        raise ValueError(f"{wrapper} must be an object")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--frontier", required=True)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()

    state = body(args.state, "actuation_state")
    frontier = body(args.frontier, "actuation_frontier")

    errors = []
    if state.get("run_id") != frontier.get("run_id"):
        errors.append("run_id_mismatch")
    state_artifact = state.get("artifact_state", {})
    frontier_artifact = frontier.get("artifact_state", {})
    for key in ("branch", "base", "head", "dirty_fingerprint"):
        if state_artifact.get(key) != frontier_artifact.get(key):
            errors.append(f"artifact_state_mismatch:{key}")
    if state.get("control", {}).get("authority_id") != frontier.get("graph_binding", {}).get("authority_id"):
        errors.append("authority_id_mismatch")

    packet = {
        "actuation_resume": {
            "resume_version": "ARR-v1",
            "valid": not errors,
            "errors": errors,
            "run_id": state.get("run_id"),
            "objective": state.get("objective"),
            "artifact_state": state_artifact,
            "authority": {
                "id": state.get("control", {}).get("authority_id"),
                "current": state.get("control", {}).get("authority_current"),
                "execution_allowed": state.get("control", {}).get("execution_allowed"),
                "blocking_debt": state.get("control", {}).get("blocking_debt", []),
            },
            "graph_state": state.get("graph_state", {}),
            "active_frontier": {
                "afr_id": frontier.get("afr_id"),
                "slice_id": frontier.get("slice_id"),
                "task_ids": frontier.get("graph_binding", {}).get("selected_task_ids", []),
                "owner": frontier.get("domain", {}).get("owner"),
                "invariant": frontier.get("domain", {}).get("invariant"),
                "selected_class": frontier.get("domain", {}).get("selected_class_id"),
                "selected_route": frontier.get("decision", {}).get("selected_route"),
                "permitted_scope": frontier.get("decision", {}).get("permitted_scope", []),
                "forbidden_actions": frontier.get("decision", {}).get("forbidden_actions", []),
                "selected_proof_ids": frontier.get("proof_dag", {}).get("selected_proof_ids", []),
                "realization_result": frontier.get("realization", {}).get("result"),
                "new_observations": frontier.get("realization", {}).get("new_observations", []),
                "next_frontier": frontier.get("outcome", {}).get("next_frontier"),
                "terminal": frontier.get("outcome", {}).get("terminal"),
            },
            "ship": state.get("ship", {}),
        }
    }

    if args.format == "json":
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0 if not errors else 2

    row = packet["actuation_resume"]
    print("# Actuation Resume")
    print()
    print(f"- valid: {str(row['valid']).lower()}")
    print(f"- run: `{row['run_id']}`")
    print(f"- objective: {row['objective']}")
    print(f"- head: `{row['artifact_state'].get('head')}`")
    print(f"- authority receipt: `{row['authority']['id']}` current={row['authority']['current']} execution_allowed={row['authority']['execution_allowed']}")
    if row["errors"]:
        print(f"- errors: {', '.join(row['errors'])}")
    print()
    print("## Active Frontier")
    active = row["active_frontier"]
    print(f"- AFR / slice: `{active['afr_id']}` / `{active['slice_id']}`")
    print(f"- tasks: {', '.join(active['task_ids'])}")
    print(f"- owner: `{active['owner']}`")
    print(f"- invariant: {active['invariant']}")
    print(f"- class: `{active['selected_class']}`")
    print(f"- route: `{active['selected_route']}`")
    print(f"- proof: {', '.join(active['selected_proof_ids'])}")
    print(f"- realization: `{active['realization_result']}`")
    print(f"- next frontier: `{active['next_frontier']}`")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
