#!/usr/bin/env python3
"""Create and advance atomic EPS-v1 checkpoints."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from common import canonical_digest, emit, load_epg, load_wrapped, state_digest
from execution_policy_gate import validate_policy
from policy_select import validate_state
from transition_receipt_gate import validate_transition


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def initialize(args: argparse.Namespace) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        epg, _ = load_epg(args.policy)
        policy_errors, policy_warnings, derived = validate_policy(epg)
        errors.extend(policy_errors)
        warnings.extend(policy_warnings)
    except Exception as exc:
        return emit("policy_checkpoint", {}, [str(exc)], [])

    digest = canonical_digest(epg)
    initial = epg.get("initial_state", {})
    state: dict[str, Any] = {
        "state_version": "EPS-v1",
        "state_id": initial.get("state_id"),
        "policy_id": epg.get("policy_id"),
        "policy_revision": epg.get("revision"),
        "policy_digest": digest,
        "artifact_state": epg.get("source", {}).get("artifact_state", {}),
        "satisfied_atoms": sorted(set(initial.get("satisfied_atoms", []))),
        "completed_actions": sorted(set(initial.get("completed_actions", []))),
        "failed_actions": sorted(set(initial.get("failed_actions", []))),
        "resolved_unknowns": sorted(set(initial.get("resolved_unknowns", []))),
        "closed_obligations": sorted(set(initial.get("closed_obligations", []))),
        "current_potential": dict(initial.get("current_potential", {})),
        "active_action_id": initial.get("active_action_id"),
        "transition_receipts": [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    state["state_digest"] = state_digest(state)
    errors.extend(validate_state(state, epg, digest, derived))

    if args.out and not errors:
        atomic_write(Path(args.out), {"execution_policy_state": state})
    return emit(
        "policy_checkpoint",
        {"operation": "init", "state": state, "out": args.out},
        errors,
        warnings,
    )


def apply_receipt(args: argparse.Namespace) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        epg, _ = load_epg(args.policy)
        policy_errors, policy_warnings, derived = validate_policy(epg)
        errors.extend(policy_errors)
        warnings.extend(policy_warnings)
        digest = canonical_digest(epg)
        state = load_wrapped(args.state, "execution_policy_state")
        errors.extend(validate_state(state, epg, digest, derived))
        decision = load_wrapped(args.decision, "execution_policy_decision")
        receipt = load_wrapped(args.receipt, "execution_transition_receipt")
    except Exception as exc:
        return emit("policy_checkpoint", {}, [str(exc)], [])

    transition_errors, transition_warnings, transition_details = validate_transition(
        epg,
        state,
        decision,
        receipt,
        policy_digest=digest,
    )
    errors.extend(transition_errors)
    warnings.extend(transition_warnings)
    if errors:
        return emit(
            "policy_checkpoint",
            {"operation": "apply", "transition": transition_details},
            errors,
            warnings,
        )

    action_id = str(decision.get("selected_action_id"))
    actions = {
        str(row.get("action_id")): row
        for row in epg.get("actions", [])
        if isinstance(row, dict) and row.get("action_id")
    }
    observations = {
        str(row.get("observation_id")): row
        for row in epg.get("observations", [])
        if isinstance(row, dict) and row.get("observation_id")
    }
    action = actions[action_id]

    new_state = dict(state)
    atoms = set(state.get("satisfied_atoms", []))
    completed = set(state.get("completed_actions", []))
    failed = set(state.get("failed_actions", []))
    resolved = set(state.get("resolved_unknowns", []))
    closed = set(state.get("closed_obligations", []))

    result = receipt.get("result")
    if result == "success":
        completed.add(action_id)
        failed.discard(action_id)
        atoms.add(f"action:{action_id}=success")
    elif result in {
        "failure",
        "return_to_policy",
        "return_to_spec",
        "rollback",
        "blocked",
    }:
        failed.add(action_id)
        completed.discard(action_id)
        atoms.add(f"action:{action_id}=failure")

    observed = receipt.get("observed", {})
    facts = {
        str(row.get("fact_id")): row
        for row in epg.get("belief", {}).get("facts", [])
        if isinstance(row, dict) and row.get("fact_id")
    }
    for fact_id in observed.get("facts_added", []):
        atom = facts.get(str(fact_id), {}).get("atom")
        if atom:
            atoms.add(str(atom))
    for unknown_id in observed.get("unknowns_resolved", []):
        resolved.add(str(unknown_id))
        atoms.add(f"unknown:{unknown_id}=resolved")
    for obligation_id in observed.get("obligations_closed", []):
        closed.add(str(obligation_id))
        atoms.add(f"obligation:{obligation_id}=closed")
    for row in observed.get("observations", []):
        if not isinstance(row, dict):
            continue
        observation = observations.get(str(row.get("observation_id")))
        if not observation:
            continue
        outcome = next(
            (
                item
                for item in observation.get("outcomes", [])
                if isinstance(item, dict) and item.get("outcome") == row.get("outcome")
            ),
            None,
        )
        if outcome and outcome.get("atom"):
            atoms.add(str(outcome["atom"]))

    transition_id = str(receipt.get("transition_id"))
    transition_receipts = list(state.get("transition_receipts", []))
    if transition_id in transition_receipts:
        errors.append(f"transition_receipts:duplicate:{transition_id}")
    else:
        transition_receipts.append(transition_id)

    new_state.update(
        {
            "state_id": receipt.get("state_after", {}).get("state_id"),
            "satisfied_atoms": sorted(atoms),
            "completed_actions": sorted(completed),
            "failed_actions": sorted(failed),
            "resolved_unknowns": sorted(resolved),
            "closed_obligations": sorted(closed),
            "current_potential": dict(observed.get("potential_after", {})),
            "active_action_id": None,
            "artifact_state": dict(receipt.get("artifact_state_after", {})),
            "transition_receipts": transition_receipts,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    new_state["state_digest"] = state_digest(new_state)
    errors.extend(validate_state(new_state, epg, digest, derived))

    if args.out and not errors:
        atomic_write(Path(args.out), {"execution_policy_state": new_state})
    return emit(
        "policy_checkpoint",
        {
            "operation": "apply",
            "transition": transition_details,
            "state": new_state,
            "out": args.out,
        },
        errors,
        warnings,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)

    command = subcommands.add_parser("init")
    command.add_argument("--policy", required=True)
    command.add_argument("--out", required=True)
    command.set_defaults(function=initialize)

    command = subcommands.add_parser("apply")
    command.add_argument("--policy", required=True)
    command.add_argument("--state", required=True)
    command.add_argument("--decision", required=True)
    command.add_argument("--receipt", required=True)
    command.add_argument("--out", required=True)
    command.set_defaults(function=apply_receipt)

    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
