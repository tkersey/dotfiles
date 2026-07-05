#!/usr/bin/env python3
"""Select the next EPG-v1 action or terminal from an EPS-v1 state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import (
    canonical_digest,
    condition_true,
    emit,
    load_epg,
    load_wrapped,
    state_digest,
    terminal_thresholds_met,
)
from execution_policy_gate import validate_policy


def utility_vector(action: dict[str, Any], order: list[dict[str, str]]) -> tuple:
    utility = action.get("utility", {})
    vector: list[object] = []
    for row in order:
        direction, key = next(iter(row.items()))
        value = utility.get(key, 0)
        vector.append(-value if direction == "maximize" else value)
    vector.append(action.get("action_id", ""))
    return tuple(vector)


def validate_state(
    state: dict[str, Any],
    epg: dict[str, Any],
    policy_digest: str,
    derived: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if derived is None:
        _, _, derived = validate_policy(epg)

    if state.get("state_version") != "EPS-v1":
        errors.append("state_version")
    if not state.get("state_id"):
        errors.append("state_id")
    if state.get("policy_id") != epg.get("policy_id"):
        errors.append("policy_id:mismatch")
    if state.get("policy_revision") != epg.get("revision"):
        errors.append("policy_revision:mismatch")
    if state.get("policy_digest") != policy_digest:
        errors.append("policy_digest:mismatch")
    if state.get("state_digest") != state_digest(state):
        errors.append("state_digest:mismatch")
    if not isinstance(state.get("artifact_state"), dict) or not state.get(
        "artifact_state"
    ):
        errors.append("artifact_state:must-be-nonempty-object")

    list_keys = (
        "satisfied_atoms",
        "completed_actions",
        "failed_actions",
        "resolved_unknowns",
        "closed_obligations",
        "transition_receipts",
    )
    for key in list_keys:
        if not isinstance(state.get(key), list):
            errors.append(f"{key}:must-be-list")

    satisfied = set(state.get("satisfied_atoms", []))
    if len(satisfied) != len(state.get("satisfied_atoms", [])):
        errors.append("satisfied_atoms:duplicates")
    declared = set(derived.get("declared_atoms", []))
    for atom in sorted(satisfied - declared):
        errors.append(f"satisfied_atoms:unknown:{atom}")
    initial_atoms = set(epg.get("initial_state", {}).get("satisfied_atoms", []))
    for atom in sorted(initial_atoms - satisfied):
        errors.append(f"satisfied_atoms:missing-monotonic-initial-atom:{atom}")

    actions = {
        row.get("action_id")
        for row in epg.get("actions", [])
        if isinstance(row, dict) and row.get("action_id")
    }
    unknowns = {
        row.get("unknown_id")
        for row in epg.get("belief", {}).get("unknowns", [])
        if isinstance(row, dict) and row.get("unknown_id")
    }
    obligations = {
        row.get("obligation_id")
        for row in epg.get("goal", {}).get("obligations", [])
        if isinstance(row, dict) and row.get("obligation_id")
    }

    completed = set(state.get("completed_actions", []))
    failed = set(state.get("failed_actions", []))
    for action_id in sorted((completed | failed) - actions):
        errors.append(f"actions:unknown:{action_id}")
    for action_id in sorted(completed & failed):
        errors.append(f"actions:completed-and-failed:{action_id}")
    for action_id in sorted(completed):
        if f"action:{action_id}=success" not in satisfied:
            errors.append(f"completed_actions:missing-success-atom:{action_id}")
    for action_id in sorted(failed):
        if f"action:{action_id}=failure" not in satisfied:
            errors.append(f"failed_actions:missing-failure-atom:{action_id}")

    resolved = set(state.get("resolved_unknowns", []))
    for unknown_id in sorted(resolved - unknowns):
        errors.append(f"resolved_unknowns:unknown:{unknown_id}")
    for unknown_id in sorted(resolved):
        if f"unknown:{unknown_id}=resolved" not in satisfied:
            errors.append(f"resolved_unknowns:missing-atom:{unknown_id}")

    closed = set(state.get("closed_obligations", []))
    for obligation_id in sorted(closed - obligations):
        errors.append(f"closed_obligations:unknown:{obligation_id}")
    for obligation_id in sorted(closed):
        if f"obligation:{obligation_id}=closed" not in satisfied:
            errors.append(f"closed_obligations:missing-atom:{obligation_id}")

    dimensions = {
        row.get("dimension_id"): row
        for row in epg.get("potential", {}).get("dimensions", [])
        if isinstance(row, dict) and row.get("dimension_id")
    }
    potential = state.get("current_potential")
    if not isinstance(potential, dict):
        errors.append("current_potential:must-be-object")
    else:
        if set(potential) != set(dimensions):
            errors.append("current_potential:dimension-set-mismatch")
        for dimension_id, value in potential.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"current_potential:{dimension_id}:must-be-number")

    active = state.get("active_action_id")
    if active not in (None, ""):
        if active not in actions:
            errors.append("active_action_id:unknown")
        if active in completed or active in failed:
            errors.append("active_action_id:already-terminal")
    return errors


def select_policy(
    epg: dict[str, Any],
    state: dict[str, Any],
    *,
    policy_digest: str | None = None,
    derived: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], dict[str, Any]]:
    """Return deterministic EPD-v1 selection without performing I/O."""
    errors: list[str] = []
    warnings: list[str] = []
    digest = policy_digest or canonical_digest(epg)
    if derived is None:
        policy_errors, policy_warnings, derived = validate_policy(epg)
        errors.extend(f"policy:{item}" for item in policy_errors)
        warnings.extend(f"policy:{item}" for item in policy_warnings)
    errors.extend(
        f"state:{item}" for item in validate_state(state, epg, digest, derived)
    )

    actions = {
        str(row["action_id"]): row
        for row in epg.get("actions", [])
        if isinstance(row, dict) and row.get("action_id")
    }
    completed = set(state.get("completed_actions", []))
    failed = set(state.get("failed_actions", []))
    satisfied = set(state.get("satisfied_atoms", []))
    if state.get("active_action_id"):
        errors.append("state.active_action_id:must-be-empty-before-selection")

    shielded: set[str] = set()
    shield_reasons: dict[str, list[str]] = {}
    shield_responses: dict[str, list[dict[str, str]]] = {}
    for shield in epg.get("safety_shield", {}).get("rules", []):
        if not isinstance(shield, dict):
            continue
        if not condition_true(shield.get("when", {}), satisfied):
            continue
        missing = [
            atom for atom in shield.get("requires_atoms", []) if atom not in satisfied
        ]
        if not missing:
            continue
        targets = set(str(item) for item in shield.get("forbids_action_ids", []))
        kinds = set(str(item) for item in shield.get("forbids_action_kinds", []))
        targets |= {
            action_id
            for action_id, action in actions.items()
            if action.get("kind") in kinds
        }
        for action_id in targets:
            shielded.add(action_id)
            reason = (
                f"{shield.get('shield_id')}:{shield.get('reason')}:"
                f"missing={','.join(missing)}"
            )
            shield_reasons.setdefault(action_id, []).append(reason)
            shield_responses.setdefault(action_id, []).append(
                {
                    "shield_id": str(shield.get("shield_id")),
                    "response": str(shield.get("response")),
                    "reason": reason,
                }
            )

    terminal_candidates: list[dict[str, Any]] = []
    eligible: list[tuple[dict[str, Any], dict[str, Any]]] = []
    shielded_candidates: list[tuple[dict[str, Any], str]] = []
    rule_rows = sorted(
        (
            row
            for row in epg.get("policy", {}).get("rules", [])
            if isinstance(row, dict)
        ),
        key=lambda row: (row.get("priority", 10**9), row.get("rule_id", "")),
    )
    dimensions = {
        str(row.get("dimension_id")): row
        for row in epg.get("potential", {}).get("dimensions", [])
        if isinstance(row, dict) and row.get("dimension_id")
    }
    potential_order = [
        str(item) for item in epg.get("potential", {}).get("lexicographic_order", [])
    ]

    for rule in rule_rows:
        if not condition_true(rule.get("when", {}), satisfied):
            continue
        if rule.get("terminal"):
            if rule.get("terminal") == "success":
                thresholds_met, failed_dimensions = terminal_thresholds_met(
                    state.get("current_potential", {}), dimensions, potential_order
                )
                if not thresholds_met:
                    warnings.append(
                        "success-terminal-thresholds-not-met:"
                        + ",".join(failed_dimensions)
                    )
                    continue
            terminal_candidates.append(rule)
            continue
        for action_id in rule.get("candidate_action_ids", []):
            action = actions.get(str(action_id))
            if not action:
                continue
            if action_id in shielded:
                shielded_candidates.append((rule, str(action_id)))
                continue
            if action_id in completed and not action.get("repeatable", False):
                continue
            if action_id in failed and not action.get("repeatable", False):
                continue
            if any(
                dependency not in completed
                for dependency in action.get("requires_actions", [])
            ):
                continue
            if not condition_true(action.get("preconditions", {}), satisfied):
                continue
            eligible.append((rule, action))

    applicable_rule_ids = {
        rule.get("rule_id") for rule, _ in eligible + shielded_candidates
    } | {rule.get("rule_id") for rule in terminal_candidates}
    decision: dict[str, Any] = {
        "decision_version": "EPD-v1",
        "decision_id": f"EPD-{state.get('state_id')}",
        "policy_id": epg.get("policy_id"),
        "policy_revision": epg.get("revision"),
        "policy_digest": digest,
        "state_id": state.get("state_id"),
        "state_digest": state.get("state_digest"),
        "satisfied_atoms": sorted(satisfied),
        "eligible_rule_ids": sorted(
            str(rule_id) for rule_id in applicable_rule_ids if rule_id
        ),
        "eligible_action_ids": sorted(
            str(action.get("action_id")) for _, action in eligible
        ),
        "eligible_terminal_rules": sorted(
            str(rule.get("rule_id")) for rule in terminal_candidates
        ),
        "shielded_actions": shield_reasons,
        "selected_rule_id": None,
        "selected_action_id": None,
        "terminal": None,
        "rationale": None,
        "expected_effects": None,
        "expected_observation_refs": [],
        "failure_observation_refs": [],
        "utility": None,
        "mutation_authority": "no",
        "requires_actuation_authority": False,
        "requires_frontier_record": False,
    }

    if errors:
        return errors, warnings, decision

    minimum_priority = min(
        [rule.get("priority", 10**9) for rule, _ in eligible]
        + [rule.get("priority", 10**9) for rule in terminal_candidates],
        default=None,
    )
    terminal_at_priority = [
        rule
        for rule in terminal_candidates
        if rule.get("priority", 10**9) == minimum_priority
    ]
    if terminal_at_priority:
        terminal_at_priority.sort(key=lambda row: row.get("rule_id", ""))
        rule = terminal_at_priority[0]
        decision.update(
            {
                "selected_rule_id": rule.get("rule_id"),
                "terminal": rule.get("terminal"),
                "rationale": rule.get("rationale"),
            }
        )
    elif minimum_priority is not None:
        order = epg.get("policy", {}).get("utility_order", [])
        candidates = [
            pair
            for pair in eligible
            if pair[0].get("priority", 10**9) == minimum_priority
        ]
        candidates.sort(key=lambda pair: utility_vector(pair[1], order))
        rule, action = candidates[0]
        repository_mutation = action.get("mutation_boundary", {}).get("kind") == "repository"
        decision.update(
            {
                "selected_rule_id": rule.get("rule_id"),
                "selected_action_id": action.get("action_id"),
                "rationale": rule.get("rationale"),
                "expected_effects": action.get("expected_effects"),
                "expected_observation_refs": action.get(
                    "expected_observation_refs", []
                ),
                "failure_observation_refs": action.get(
                    "failure_observation_refs", []
                ),
                "utility": action.get("utility"),
                "requires_actuation_authority": repository_mutation,
                "requires_frontier_record": repository_mutation
                and action.get("kind")
                in {"mutate", "stabilize", "deploy", "rollback"},
            }
        )
    elif shielded_candidates:
        # A branch matched, but the shield vetoed every candidate action.
        response_rank = {"return_to_spec": 0, "rollback": 1, "block": 2}
        candidates: list[tuple[int, str, str, dict[str, Any]]] = []
        for rule, action_id in shielded_candidates:
            for row in shield_responses.get(action_id, []):
                response = row.get("response", "block")
                candidates.append(
                    (
                        response_rank.get(response, 99),
                        row.get("shield_id", ""),
                        action_id,
                        {"rule": rule, **row},
                    )
                )
        candidates.sort()
        _, _, action_id, row = candidates[0]
        response = row.get("response")
        terminal = "blocked" if response == "block" else response
        decision.update(
            {
                "selected_rule_id": row["rule"].get("rule_id"),
                "terminal": terminal,
                "rationale": f"Safety shield blocked {action_id}: {row.get('reason')}",
            }
        )
    else:
        errors.append("no-eligible-action-or-terminal")

    return errors, warnings, decision


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()

    try:
        epg, _ = load_epg(args.policy)
        digest = canonical_digest(epg)
        state = load_wrapped(args.state, "execution_policy_state")
        errors, warnings, decision = select_policy(
            epg, state, policy_digest=digest
        )
    except Exception as exc:
        return emit("policy_select", {}, [str(exc)], [])

    wrapper = {"execution_policy_decision": decision}
    if args.out and not errors:
        Path(args.out).write_text(
            json.dumps(wrapper, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return emit(
        "policy_select",
        {"decision": decision, "out": args.out},
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
