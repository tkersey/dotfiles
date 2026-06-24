#!/usr/bin/env python3
"""Validate acceptance_contract / AC-v2."""

from __future__ import annotations

import argparse

from common import emit, list_field, load_document, object_field, require, unique_ids, unwrap, yes

HORIZON = {"open", "sealed", "rebased"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        ac = unwrap(load_document(args.file), "acceptance_contract")
    except Exception as exc:
        return emit("acceptance_contract_gate", {}, [str(exc)], [])

    if ac.get("contract_version") != "AC-v2":
        errors.append("contract_version")
    for key in ("contract_id", "campaign_id", "fingerprint"):
        require(ac, key, errors)

    source = object_field(ac, "source", errors)
    source_count = 0
    for key in ("plan_refs", "issue_refs", "pr_intent_refs", "compatibility_baseline_refs"):
        source_count += len(list_field(source, key, errors, "source."))
    if source_count == 0:
        errors.append("source:no-refs")

    goal = object_field(ac, "goal", errors)
    require(goal, "goal_id", errors, "goal.")
    require(goal, "statement", errors, "goal.")

    required = list_field(ac, "required", errors)
    compatibility = list_field(ac, "compatibility", errors)
    forbidden = list_field(ac, "forbidden", errors)
    may = list_field(ac, "permitted_but_unrequired", errors)
    non_goals = list_field(ac, "non_goals", errors)
    proof_bar = list_field(ac, "proof_bar", errors)

    if not required and not compatibility and not forbidden:
        errors.append("contract:no-MUST-or-MUST-NOT")
    if not proof_bar:
        errors.append("proof_bar:empty")

    all_ids: set[str] = set()
    specs = (
        (required, "requirement_id", "required", ("statement", "source_refs", "observable_witnesses")),
        (compatibility, "obligation_id", "compatibility", ("statement", "baseline_ref", "observable_witnesses")),
        (forbidden, "prohibition_id", "forbidden", ("statement", "source_refs", "observable_witnesses")),
        (may, "behavior_id", "permitted_but_unrequired", ("statement", "reason")),
        (non_goals, "non_goal_id", "non_goals", ("statement", "source_refs")),
        (proof_bar, "proof_id", "proof_bar", ("statement", "command_or_surface")),
    )
    for rows, id_field, prefix, fields in specs:
        values = unique_ids(rows, id_field, errors, prefix)
        overlap = all_ids & values
        for value in overlap:
            errors.append(f"contract:duplicate-global-id:{value}")
        all_ids |= values
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            for field in fields:
                if field.endswith("_refs") or field == "observable_witnesses":
                    if not isinstance(row.get(field), list):
                        errors.append(f"{prefix}[{index}].{field}:must-be-list")
                elif not row.get(field):
                    errors.append(f"{prefix}[{index}].{field}:missing")

    language = object_field(ac, "observation_language", errors)
    observed_total = 0
    for key in (
        "actors", "operations", "states", "transitions",
        "externally_visible_results", "failure_observations", "authority_observations",
    ):
        observed_total += len(list_field(language, key, errors, "observation_language."))
    if observed_total == 0:
        errors.append("observation_language:empty")

    horizon = object_field(ac, "horizon", errors)
    state = horizon.get("state")
    if state not in HORIZON:
        errors.append("horizon.state")
    if not isinstance(horizon.get("sequence"), int) or horizon.get("sequence", 0) < 1:
        errors.append("horizon.sequence")
    if state in {"sealed", "rebased"} and not horizon.get("sealed_at"):
        errors.append("horizon.sealed_at")
    if state == "rebased":
        for key in ("prior_fingerprint", "rebase_reason", "rebase_authority"):
            require(horizon, key, errors, "horizon.")
    elif any(horizon.get(key) for key in ("prior_fingerprint", "rebase_reason", "rebase_authority")):
        warnings.append("horizon:rebase-fields-present-without-rebased-state")

    authority = object_field(ac, "authority", errors)
    for key in ("accepted_by", "accepted_at"):
        require(authority, key, errors, "authority.")
    if not yes(authority.get("change_requires_explicit_rebase")):
        errors.append("authority.change_requires_explicit_rebase")

    gate = object_field(ac, "gate", errors)
    gate_fields = (
        "sources_bound", "required_behavior_nonempty", "observation_language_nonempty",
        "non_goals_explicit", "proof_bar_present", "horizon_consistent", "seal_allowed",
    )
    for key in gate_fields:
        if not yes(gate.get(key)):
            errors.append(f"gate.{key}")
    if state == "open" and yes(gate.get("seal_allowed")):
        warnings.append("horizon:open-but-seal-allowed")

    return emit(
        "acceptance_contract_gate",
        {
            "contract_id": ac.get("contract_id"),
            "campaign_id": ac.get("campaign_id"),
            "horizon_state": state,
            "horizon_sequence": horizon.get("sequence"),
            "contract_entries": len(all_ids),
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
