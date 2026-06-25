#!/usr/bin/env python3
"""Validate execution_policy_graph / EPG-v1."""

from __future__ import annotations

import argparse
from typing import Any

from common import (
    apply_potential_delta,
    bool_claim,
    canonical_digest,
    compare_potential,
    condition_atoms,
    emit,
    graph_cycles,
    is_no,
    is_yes,
    list_field,
    load_epg,
    object_field,
    require,
    unique_rows,
    valid_atom,
    valid_digest,
    validate_iso_timestamp,
)

PROFILES = {"fast", "balanced", "strict", "campaign"}
SOURCE_MODES = {"spec_handoff", "direct_brief", "existing_policy_revision"}
REGIMES = {"clear", "complicated", "complex", "chaotic"}
CONFIDENCE = {"high", "medium", "low"}
UNKNOWN_STATUS = {"open", "resolved", "blocked"}
URGENCY = {"critical", "high", "medium", "low"}
OBS_SOURCES = {"command", "test", "metric", "inspection", "user_decision", "external_event"}
ACTION_KINDS = {"inspect", "probe", "decide", "mutate", "prove", "stabilize", "deploy", "rollback"}
MUTATION_KINDS = {"repository", "external", "docs", "none"}
RISKY_ACTIONS = {"mutate", "stabilize", "deploy", "rollback"}
EVIDENCE_KINDS = {"command", "inspection", "metric", "live_integration", "experiment", "user_acceptance"}
ARTIFACT_BINDINGS = {"action", "wave", "final_tree", "live_system"}
TERMINALS = {"success", "blocked", "return_to_spec", "rollback"}
SHIELD_RESPONSES = {"block", "rollback", "return_to_spec"}
INVALIDATOR_ACTIONS = {"return_to_spec", "return_to_grill", "replan", "recompile_st", "block"}
HANDOFF_OWNERS = {"st", "actuating", "spec-pipeline", "grill-me", "blocked"}
HANDOFF_RESULTS = {"pass", "stale", "return_to_spec", "return_to_grill", "blocked"}
SEMANTIC_DRIFT = {"none", "authorized", "unauthorized"}

UTILITY_KEYS = (
    "obligation_reduction",
    "information_gain",
    "downstream_unlock",
    "proof_gain",
    "execution_cost",
    "irreversible_risk",
    "semantic_surface_growth",
    "rework_risk",
)


def _nonempty(parent: dict[str, Any], key: str, errors: list[str], prefix: str) -> list[Any]:
    value = list_field(parent, key, errors, prefix)
    if not value:
        errors.append(f"{prefix}{key}:empty")
    return value


def validate_policy(epg: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    if epg.get("policy_version") != "EPG-v1":
        errors.append("policy_version")
    for key in ("policy_id", "created_at", "profile"):
        require(epg, key, errors)
    if not validate_iso_timestamp(epg.get("created_at")):
        errors.append("created_at:invalid")
    revision = epg.get("revision")
    if not isinstance(revision, int) or revision < 1:
        errors.append("revision")
        revision = 0
    if epg.get("profile") not in PROFILES:
        errors.append("profile")

    parent = epg.get("parent")
    if revision == 1:
        if parent not in (None, {}):
            errors.append("parent:must-be-null-for-revision-1")
    else:
        if not isinstance(parent, dict):
            errors.append("parent:required")
            parent = {}
        if parent.get("policy_id") != epg.get("policy_id"):
            errors.append("parent.policy_id:mismatch")
        if not valid_digest(parent.get("digest")):
            errors.append("parent.digest")

    source = object_field(epg, "source", errors)
    mode = source.get("mode")
    if mode not in SOURCE_MODES:
        errors.append("source.mode")
    require(source, "authority", errors, "source.")
    _nonempty(source, "source_refs", errors, "source.")
    if not valid_digest(source.get("source_digest")):
        errors.append("source.source_digest")
    list_field(source, "locked_decision_refs", errors, "source.")
    if source.get("current") not in {"yes", "no", "unknown", True, False}:
        errors.append("source.current")
    artifact = object_field(source, "artifact_state", errors, "source.")
    repo_bound = is_yes(artifact.get("repo_bound"))
    if not (is_yes(artifact.get("repo_bound")) or is_no(artifact.get("repo_bound"))):
        errors.append("source.artifact_state.repo_bound")
    if repo_bound:
        for key in ("repository", "branch", "base", "head"):
            require(artifact, key, errors, "source.artifact_state.")
        if not valid_digest(artifact.get("dirty_fingerprint")):
            errors.append("source.artifact_state.dirty_fingerprint")
    if mode == "spec_handoff":
        require(source, "spec_id", errors, "source.")
        require(source, "spec_governance_ref", errors, "source.")
    if mode == "existing_policy_revision" and revision <= 1:
        errors.append("existing_policy_revision:revision-must-exceed-1")

    goal = object_field(epg, "goal", errors)
    require(goal, "objective", errors, "goal.")
    obligation_rows = list_field(goal, "obligations", errors, "goal.")
    obligations = unique_rows(obligation_rows, "obligation_id", errors, "goal.obligations")
    if not obligations:
        errors.append("goal.obligations:empty")
    terminal_pred_rows = list_field(goal, "terminal_predicates", errors, "goal.")
    terminal_predicates = unique_rows(terminal_pred_rows, "predicate_id", errors, "goal.terminal_predicates")
    if not terminal_predicates:
        errors.append("goal.terminal_predicates:empty")
    invariant_rows = list_field(goal, "safety_invariants", errors, "goal.")
    invariants = unique_rows(invariant_rows, "invariant_id", errors, "goal.safety_invariants")
    if not invariants:
        errors.append("goal.safety_invariants:empty")
    forbidden_rows = list_field(goal, "forbidden_states", errors, "goal.")
    forbidden = unique_rows(forbidden_rows, "forbidden_id", errors, "goal.forbidden_states")

    declared_atoms: set[str] = set()
    obligation_terminal_refs: dict[str, list[str]] = {}
    proof_ref_declarations: set[str] = set()
    for index, row in enumerate(obligation_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"goal.obligations[{index}]."
        require(row, "statement", errors, prefix)
        _nonempty(row, "source_refs", errors, prefix)
        refs = _nonempty(row, "terminal_predicate_refs", errors, prefix)
        obligation_terminal_refs[str(row.get("obligation_id"))] = [str(x) for x in refs]
        proofs = _nonempty(row, "proof_refs", errors, prefix)
        proof_ref_declarations.update(str(x) for x in proofs)
        declared_atoms.add(f"obligation:{row.get('obligation_id')}=closed")
    for index, row in enumerate(terminal_pred_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"goal.terminal_predicates[{index}]."
        require(row, "statement", errors, prefix)
        atom = row.get("atom")
        if not valid_atom(atom):
            errors.append(f"{prefix}atom")
        else:
            declared_atoms.add(atom)
    for obligation_id, refs in obligation_terminal_refs.items():
        for ref in refs:
            if ref not in terminal_predicates:
                errors.append(f"goal.obligations:{obligation_id}:unknown-terminal-predicate:{ref}")
    for index, row in enumerate(invariant_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"goal.safety_invariants[{index}]."
        require(row, "statement", errors, prefix)
        _nonempty(row, "source_refs", errors, prefix)
        atom = row.get("violation_atom")
        if not valid_atom(atom):
            errors.append(f"{prefix}violation_atom")
        else:
            declared_atoms.add(atom)
    for index, row in enumerate(forbidden_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"goal.forbidden_states[{index}]."
        require(row, "statement", errors, prefix)
        atom = row.get("atom")
        if not valid_atom(atom):
            errors.append(f"{prefix}atom")
        else:
            declared_atoms.add(atom)
        if row.get("response_terminal") not in TERMINALS:
            errors.append(f"{prefix}response_terminal")

    regime = object_field(epg, "regime", errors)
    regime_kind = regime.get("kind")
    if regime_kind not in REGIMES:
        errors.append("regime.kind")
    if regime.get("confidence") not in CONFIDENCE:
        errors.append("regime.confidence")
    require(regime, "rationale", errors, "regime.")
    regime_obs_refs = list_field(regime, "reclassify_on_observation_refs", errors, "regime.")

    belief = object_field(epg, "belief", errors)
    fact_rows = list_field(belief, "facts", errors, "belief.")
    facts = unique_rows(fact_rows, "fact_id", errors, "belief.facts")
    unknown_rows = list_field(belief, "unknowns", errors, "belief.")
    unknowns = unique_rows(unknown_rows, "unknown_id", errors, "belief.unknowns")
    for index, row in enumerate(fact_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"belief.facts[{index}]."
        atom = row.get("atom")
        if not valid_atom(atom) or not str(atom).startswith("fact:"):
            errors.append(f"{prefix}atom")
        else:
            declared_atoms.add(atom)
        require(row, "statement", errors, prefix)
        _nonempty(row, "evidence_refs", errors, prefix)
        if row.get("confidence") not in CONFIDENCE:
            errors.append(f"{prefix}confidence")
        list_field(row, "invalidators", errors, prefix)
    critical_open_unknowns: set[str] = set()
    for index, row in enumerate(unknown_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"belief.unknowns[{index}]."
        for key in ("statement", "consequence_if_wrong", "decision_relevance"):
            require(row, key, errors, prefix)
        _nonempty(row, "evidence_required", errors, prefix)
        refs = list_field(row, "observation_refs", errors, prefix)
        status = row.get("status")
        urgency = row.get("urgency")
        if status not in UNKNOWN_STATUS:
            errors.append(f"{prefix}status")
        if urgency not in URGENCY:
            errors.append(f"{prefix}urgency")
        unknown_id = row.get("unknown_id")
        declared_atoms.add(f"unknown:{unknown_id}=resolved")
        declared_atoms.add(f"unknown:{unknown_id}=blocked")
        if status == "open" and urgency in {"critical", "high"}:
            critical_open_unknowns.add(str(unknown_id))
            if not refs:
                errors.append(f"{prefix}observation_refs:required-for-critical-open")

    observation_rows = list_field(epg, "observations", errors)
    observations = unique_rows(observation_rows, "observation_id", errors, "observations")
    observation_atoms: dict[str, set[str]] = {}
    for index, row in enumerate(observation_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"observations[{index}]."
        if row.get("source_kind") not in OBS_SOURCES:
            errors.append(f"{prefix}source_kind")
        for key in ("command_or_evidence", "predicate", "freshness", "evidence_schema"):
            require(row, key, errors, prefix)
        refs = list_field(row, "resolves_unknown_refs", errors, prefix)
        for ref in refs:
            if ref not in unknowns:
                errors.append(f"{prefix}resolves_unknown_refs:unknown:{ref}")
        outcomes = _nonempty(row, "outcomes", errors, prefix)
        atoms: set[str] = set()
        names: set[str] = set()
        for out_index, outcome in enumerate(outcomes):
            oprefix = f"{prefix}outcomes[{out_index}]."
            if not isinstance(outcome, dict):
                errors.append(f"{oprefix}must-be-object")
                continue
            name = require(outcome, "outcome", errors, oprefix)
            atom = outcome.get("atom")
            if name in names:
                errors.append(f"{prefix}outcomes:duplicate:{name}")
            names.add(str(name))
            if not valid_atom(atom) or not str(atom).startswith(f"obs:{row.get('observation_id')}="):
                errors.append(f"{oprefix}atom")
            else:
                atoms.add(atom)
                declared_atoms.add(atom)
        observation_atoms[str(row.get("observation_id"))] = atoms
    for ref in regime_obs_refs:
        if ref not in observations:
            errors.append(f"regime.reclassify_on_observation_refs:unknown:{ref}")
    for unknown_id, row in unknowns.items():
        for ref in row.get("observation_refs", []):
            if ref not in observations:
                errors.append(f"belief.unknowns:{unknown_id}:unknown-observation:{ref}")

    action_rows = list_field(epg, "actions", errors)
    actions = unique_rows(action_rows, "action_id", errors, "actions")
    if not actions:
        errors.append("actions:empty")
    action_deps: dict[str, list[str]] = {}
    action_proof_ids: set[str] = set()
    actions_bounded = True
    unknown_resolvers: dict[str, set[str]] = {uid: set() for uid in unknowns}
    obligation_closers: dict[str, set[str]] = {oid: set() for oid in obligations}
    risky_actions: set[str] = set()
    action_outcome_atoms: set[str] = set()
    action_expected_obs: dict[str, set[str]] = {}
    action_failure_obs: dict[str, set[str]] = {}
    potential_delta_keys: set[str] = set()
    action_potential_deltas: dict[str, dict[str, float]] = {}
    for index, row in enumerate(action_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"actions[{index}]."
        action_id = str(row.get("action_id"))
        kind = row.get("kind")
        if kind not in ACTION_KINDS:
            errors.append(f"{prefix}kind")
            actions_bounded = False
        if kind in RISKY_ACTIONS:
            risky_actions.add(action_id)
        if not row.get("owner"):
            errors.append(f"{prefix}owner")
            actions_bounded = False
        preconditions = object_field(row, "preconditions", errors, prefix)
        condition_atoms(preconditions, errors, f"{prefix}preconditions.")
        deps = list_field(row, "requires_actions", errors, prefix)
        action_deps[action_id] = [str(x) for x in deps]
        boundary = object_field(row, "mutation_boundary", errors, prefix)
        boundary_kind = boundary.get("kind")
        if boundary_kind not in MUTATION_KINDS:
            errors.append(f"{prefix}mutation_boundary.kind")
            actions_bounded = False
        paths = list_field(boundary, "paths", errors, f"{prefix}mutation_boundary.")
        symbols = list_field(boundary, "symbols", errors, f"{prefix}mutation_boundary.")
        lock_roots = list_field(row, "lock_roots", errors, prefix)
        if kind in RISKY_ACTIONS and boundary_kind == "repository":
            if not paths and not symbols:
                errors.append(f"{prefix}mutation_boundary:empty")
                actions_bounded = False
            if not lock_roots:
                errors.append(f"{prefix}lock_roots:empty")
                actions_bounded = False
        effects = object_field(row, "expected_effects", errors, prefix)
        facts_added = list_field(effects, "facts_added", errors, f"{prefix}expected_effects.")
        unknowns_resolved = list_field(effects, "unknowns_resolved", errors, f"{prefix}expected_effects.")
        obligations_closed = list_field(effects, "obligations_closed", errors, f"{prefix}expected_effects.")
        delta = object_field(effects, "potential_delta", errors, f"{prefix}expected_effects.")
        numeric_delta: dict[str, float] = {}
        for dimension_id, value in delta.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(
                    f"{prefix}expected_effects.potential_delta.{dimension_id}:must-be-number"
                )
            else:
                numeric_delta[str(dimension_id)] = float(value)
        action_potential_deltas[action_id] = numeric_delta
        potential_delta_keys.update(delta.keys())
        for ref in facts_added:
            if ref not in facts:
                errors.append(f"{prefix}expected_effects.facts_added:unknown:{ref}")
        for ref in unknowns_resolved:
            if ref not in unknowns:
                errors.append(f"{prefix}expected_effects.unknowns_resolved:unknown:{ref}")
            else:
                unknown_resolvers[str(ref)].add(action_id)
        for ref in obligations_closed:
            if ref not in obligations:
                errors.append(f"{prefix}expected_effects.obligations_closed:unknown:{ref}")
            else:
                obligation_closers[str(ref)].add(action_id)
        expected_obs = list_field(row, "expected_observation_refs", errors, prefix)
        failure_obs = list_field(row, "failure_observation_refs", errors, prefix)
        action_expected_obs[action_id] = {str(x) for x in expected_obs}
        action_failure_obs[action_id] = {str(x) for x in failure_obs}
        for ref in expected_obs + failure_obs:
            if ref not in observations:
                errors.append(f"{prefix}observation-ref:unknown:{ref}")
        if not (facts_added or unknowns_resolved or obligations_closed or expected_obs or failure_obs):
            errors.append(f"{prefix}no-observable-predicted-effect")
            actions_bounded = False
        proofs = list_field(row, "proof_obligations", errors, prefix)
        if kind in RISKY_ACTIONS | {"prove"} and not proofs:
            errors.append(f"{prefix}proof_obligations:empty")
            actions_bounded = False
        for proof_index, proof in enumerate(proofs):
            pprefix = f"{prefix}proof_obligations[{proof_index}]."
            if not isinstance(proof, dict):
                errors.append(f"{pprefix}must-be-object")
                continue
            proof_id = proof.get("proof_id")
            if not isinstance(proof_id, str) or not proof_id:
                errors.append(f"{pprefix}proof_id")
            elif proof_id in action_proof_ids:
                errors.append(f"proof_obligations:duplicate:{proof_id}")
            else:
                action_proof_ids.add(proof_id)
            for key in ("statement", "command_or_evidence"):
                require(proof, key, errors, pprefix)
            if proof.get("evidence_kind") not in EVIDENCE_KINDS:
                errors.append(f"{pprefix}evidence_kind")
            if proof.get("artifact_binding") not in ARTIFACT_BINDINGS:
                errors.append(f"{pprefix}artifact_binding")
        rollback = object_field(row, "rollback", errors, prefix)
        list_field(rollback, "trigger_atoms", errors, f"{prefix}rollback.")
        rollback_action = rollback.get("action_id")
        instructions = rollback.get("instructions")
        if kind in RISKY_ACTIONS and not (rollback_action or instructions):
            errors.append(f"{prefix}rollback:missing")
            actions_bounded = False
        utility = object_field(row, "utility", errors, prefix)
        for key in UTILITY_KEYS:
            value = utility.get(key)
            if not isinstance(value, int) or not 0 <= value <= 100:
                errors.append(f"{prefix}utility.{key}")
        if not isinstance(row.get("repeatable"), bool):
            errors.append(f"{prefix}repeatable")
        declared_atoms.add(f"action:{action_id}=success")
        declared_atoms.add(f"action:{action_id}=failure")
        action_outcome_atoms.add(f"action:{action_id}=success")
        action_outcome_atoms.add(f"action:{action_id}=failure")
    for action_id, deps in action_deps.items():
        for dep in deps:
            if dep not in actions:
                errors.append(f"actions:{action_id}:requires-actions:unknown:{dep}")
            if dep == action_id:
                errors.append(f"actions:{action_id}:requires-actions:self")
    cycles = graph_cycles(action_deps)
    for cycle in cycles:
        errors.append("actions:dependency-cycle:" + "->".join(cycle))

    action_kinds_present = {
        str(action.get("kind")) for action in actions.values() if action.get("kind")
    }
    open_unknowns = {
        unknown_id
        for unknown_id, row in unknowns.items()
        if row.get("status") == "open"
    }
    if regime_kind == "clear" and critical_open_unknowns:
        errors.append("regime.clear:critical-open-unknowns")
    if (
        regime_kind == "complicated"
        and open_unknowns
        and not action_kinds_present.intersection({"inspect", "probe", "decide"})
    ):
        errors.append("regime.complicated:analysis-action-required")
    if regime_kind == "complex":
        if not open_unknowns:
            errors.append("regime.complex:open-unknown-required")
        if "probe" not in action_kinds_present:
            errors.append("regime.complex:probe-action-required")
    if regime_kind == "chaotic" and "stabilize" not in action_kinds_present:
        errors.append("regime.chaotic:stabilize-action-required")

    policy = object_field(epg, "policy", errors)
    if policy.get("selection") != "lexicographic_utility":
        errors.append("policy.selection")
    utility_order = _nonempty(policy, "utility_order", errors, "policy.")
    utility_seen: set[str] = set()
    for index, row in enumerate(utility_order):
        prefix = f"policy.utility_order[{index}]"
        if not isinstance(row, dict) or len(row) != 1:
            errors.append(f"{prefix}:invalid")
            continue
        direction, key = next(iter(row.items()))
        if direction not in {"maximize", "minimize"} or key not in UTILITY_KEYS:
            errors.append(f"{prefix}:invalid")
        if str(key) in utility_seen:
            errors.append(f"policy.utility_order:duplicate:{key}")
        utility_seen.add(str(key))
    if utility_seen != set(UTILITY_KEYS):
        missing = sorted(set(UTILITY_KEYS) - utility_seen)
        extra = sorted(utility_seen - set(UTILITY_KEYS))
        if missing:
            errors.append("policy.utility_order:missing:" + ",".join(missing))
        if extra:
            errors.append("policy.utility_order:extra:" + ",".join(extra))
    rule_rows = list_field(policy, "rules", errors, "policy.")
    rules = unique_rows(rule_rows, "rule_id", errors, "policy.rules")
    if not rules:
        errors.append("policy.rules:empty")
    priorities: set[int] = set()
    selected_by_rule: dict[str, set[str]] = {aid: set() for aid in actions}
    terminal_rule_conditions: dict[str, list[dict[str, Any]]] = {
        name: [] for name in TERMINALS
    }
    condition_referenced_atoms: set[str] = set()
    for index, row in enumerate(rule_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"policy.rules[{index}]."
        priority = row.get("priority")
        if not isinstance(priority, int):
            errors.append(f"{prefix}priority")
        elif priority in priorities:
            errors.append(f"policy.rules:duplicate-priority:{priority}")
        else:
            priorities.add(priority)
        when = object_field(row, "when", errors, prefix)
        condition_referenced_atoms |= condition_atoms(when, errors, f"{prefix}when.")
        candidates = list_field(row, "candidate_action_ids", errors, prefix)
        terminal = row.get("terminal")
        if not candidates and not terminal:
            errors.append(f"{prefix}candidate-action-or-terminal-required")
        if candidates and terminal:
            errors.append(f"{prefix}cannot-have-action-and-terminal")
        for action_id in candidates:
            if action_id not in actions:
                errors.append(f"{prefix}candidate_action_ids:unknown:{action_id}")
            else:
                selected_by_rule[str(action_id)].add(str(row.get("rule_id")))
        if terminal and terminal not in TERMINALS:
            errors.append(f"{prefix}terminal")
        elif terminal:
            terminal_rule_conditions[str(terminal)].append(when)
        require(row, "rationale", errors, prefix)
        for ref in list_field(row, "obligation_refs", errors, prefix):
            if ref not in obligations:
                errors.append(f"{prefix}obligation_refs:unknown:{ref}")
        for ref in list_field(row, "unknown_refs", errors, prefix):
            if ref not in unknowns:
                errors.append(f"{prefix}unknown_refs:unknown:{ref}")
        list_field(row, "evidence_refs", errors, prefix)
        replans = list_field(row, "replan_if_atoms", errors, prefix)
        for atom in replans:
            if not valid_atom(atom):
                errors.append(f"{prefix}replan_if_atoms:invalid:{atom}")
            else:
                condition_referenced_atoms.add(atom)
    list_field(policy, "tie_breakers", errors, "policy.")

    potential = object_field(epg, "potential", errors)
    dimension_rows = list_field(potential, "dimensions", errors, "potential.")
    dimensions = unique_rows(dimension_rows, "dimension_id", errors, "potential.dimensions")
    lex_order = _nonempty(potential, "lexicographic_order", errors, "potential.")
    initial_potential = object_field(potential, "initial", errors, "potential.")
    if set(lex_order) != set(dimensions):
        errors.append("potential.lexicographic_order:must-match-dimensions")
    for index, row in enumerate(dimension_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"potential.dimensions[{index}]."
        require(row, "statement", errors, prefix)
        if row.get("direction") not in {"minimize", "maximize"}:
            errors.append(f"{prefix}direction")
        for key in ("current_value", "terminal_threshold"):
            if not isinstance(row.get(key), (int, float)):
                errors.append(f"{prefix}{key}")
        if row.get("dimension_id") not in initial_potential:
            errors.append(f"potential.initial:missing:{row.get('dimension_id')}")
        elif initial_potential[row.get("dimension_id")] != row.get("current_value"):
            errors.append(f"potential.initial:mismatch:{row.get('dimension_id')}")
    for key in potential_delta_keys:
        if key not in dimensions:
            errors.append(f"actions.potential_delta:unknown-dimension:{key}")

    # Every action must predict strict lexicographic progress. This is the
    # execution-policy equivalent of requiring a useful next move rather than
    # a merely plausible task. Later dimensions may worsen only when an
    # earlier, higher-priority dimension improves.
    zero_potential = {dimension_id: 0 for dimension_id in dimensions}
    for action_id, delta in action_potential_deltas.items():
        try:
            expected = apply_potential_delta(
                zero_potential, delta, set(dimensions)
            )
            comparison = compare_potential(
                zero_potential, expected, dimensions, list(lex_order)
            )
        except ValueError as exc:
            errors.append(f"actions:{action_id}:potential:{exc}")
            continue
        if comparison["relation"] != "improved":
            errors.append(
                f"actions:{action_id}:expected-potential-not-strictly-improving"
            )

    shield = object_field(epg, "safety_shield", errors)
    shield_rows = list_field(shield, "rules", errors, "safety_shield.")
    shields = unique_rows(shield_rows, "shield_id", errors, "safety_shield.rules")
    shield_coverage: set[str] = set()
    for index, row in enumerate(shield_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"safety_shield.rules[{index}]."
        when = object_field(row, "when", errors, prefix)
        condition_referenced_atoms |= condition_atoms(when, errors, f"{prefix}when.")
        action_ids = list_field(row, "forbids_action_ids", errors, prefix)
        action_kinds = list_field(row, "forbids_action_kinds", errors, prefix)
        if not action_ids and not action_kinds:
            errors.append(f"{prefix}forbidden-targets:empty")
        for action_id in action_ids:
            if action_id not in actions:
                errors.append(f"{prefix}forbids_action_ids:unknown:{action_id}")
            else:
                shield_coverage.add(str(action_id))
        for kind in action_kinds:
            if kind not in ACTION_KINDS:
                errors.append(f"{prefix}forbids_action_kinds:unknown:{kind}")
            for action_id, action in actions.items():
                if action.get("kind") == kind:
                    shield_coverage.add(action_id)
        requires_atoms = list_field(row, "requires_atoms", errors, prefix)
        if not requires_atoms:
            errors.append(f"{prefix}requires_atoms:empty")
        for atom in requires_atoms:
            if not valid_atom(atom):
                errors.append(f"{prefix}requires_atoms:invalid:{atom}")
            else:
                condition_referenced_atoms.add(atom)
        if row.get("response") not in SHIELD_RESPONSES:
            errors.append(f"{prefix}response")
        require(row, "reason", errors, prefix)
    uncovered_risky = risky_actions - shield_coverage
    for action_id in sorted(uncovered_risky):
        errors.append(f"safety_shield:uncovered-risky-action:{action_id}")
    safety_shield_complete = bool(shields) and not uncovered_risky

    horizon = object_field(epg, "horizon", errors)
    for key in ("mutation_actions_max", "evidence_actions_max", "delivery_transitions_max"):
        value = horizon.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"horizon.{key}")
    if isinstance(horizon.get("mutation_actions_max"), int) and horizon.get("mutation_actions_max") > 1:
        warnings.append("horizon.mutation_actions_max:greater-than-default-1")
    repository_mutation_exists = any(
        action.get("kind") in RISKY_ACTIONS
        and action.get("mutation_boundary", {}).get("kind") == "repository"
        for action in actions.values()
    )
    evidence_action_exists = any(
        action.get("kind") in {"inspect", "probe", "decide", "prove"}
        for action in actions.values()
    )
    delivery_action_exists = any(
        action.get("kind") == "deploy" for action in actions.values()
    )
    if repository_mutation_exists and horizon.get("mutation_actions_max", 0) < 1:
        errors.append("horizon.mutation_actions_max:must-permit-one-current-action")
    if evidence_action_exists and horizon.get("evidence_actions_max", 0) < 1:
        errors.append("horizon.evidence_actions_max:must-permit-evidence")
    if delivery_action_exists and horizon.get("delivery_transitions_max", 0) < 1:
        errors.append("horizon.delivery_transitions_max:must-permit-delivery")

    for name in TERMINALS:
        declared_atoms.add(f"terminal:{name}")
    terminal_states = object_field(epg, "terminal_states", errors)
    terminal_condition_atoms: set[str] = set()
    terminal_state_conditions: dict[str, dict[str, Any]] = {}
    for name in TERMINALS:
        terminal = object_field(terminal_states, name, errors, "terminal_states.")
        when = object_field(terminal, "when", errors, f"terminal_states.{name}.")
        terminal_state_conditions[name] = when
        terminal_condition_atoms |= condition_atoms(when, errors, f"terminal_states.{name}.when.")
        if name == "success":
            proofs = _nonempty(terminal, "proof_refs", errors, f"terminal_states.{name}.")
            for proof_id in proofs:
                if proof_id not in action_proof_ids and proof_id not in proof_ref_declarations:
                    errors.append(f"terminal_states.success.proof_refs:unknown:{proof_id}")

    terminal_rules_complete = True
    for name in TERMINALS:
        candidates = terminal_rule_conditions.get(name, [])
        if not candidates:
            errors.append(f"policy.rules:terminal-unreachable:{name}")
            terminal_rules_complete = False
            continue
        canonical_state = {
            key: sorted(terminal_state_conditions.get(name, {}).get(key, []))
            for key in ("all", "any", "none")
        }
        candidate_states = [
            {key: sorted(candidate.get(key, [])) for key in ("all", "any", "none")}
            for candidate in candidates
        ]
        exact_match = canonical_state in candidate_states
        disjunctive_match = False
        # A terminal with `any: [a,b,c]` may be represented by three terminal
        # rules whose `all` clauses are base_all+a, base_all+b, and base_all+c.
        # This preserves deterministic rule priorities while remaining
        # semantically equivalent to the terminal declaration.
        if canonical_state["any"]:
            base_all = set(canonical_state["all"])
            base_none = canonical_state["none"]
            covered: set[str] = set()
            for candidate in candidate_states:
                if candidate["any"] or candidate["none"] != base_none:
                    continue
                candidate_all = set(candidate["all"])
                extras = candidate_all - base_all
                if base_all.issubset(candidate_all) and len(extras) == 1:
                    atom = next(iter(extras))
                    if atom in canonical_state["any"]:
                        covered.add(atom)
            disjunctive_match = covered == set(canonical_state["any"])
        if not (exact_match or disjunctive_match):
            errors.append(f"policy.rules:terminal-condition-mismatch:{name}")
            terminal_rules_complete = False

    required_success_exclusions = {
        str(row.get("violation_atom"))
        for row in invariant_rows
        if isinstance(row, dict) and row.get("violation_atom")
    } | {
        str(row.get("atom"))
        for row in forbidden_rows
        if isinstance(row, dict) and row.get("atom")
    }
    success_none = set(
        terminal_state_conditions.get("success", {}).get("none", [])
    )
    missing_success_exclusions = required_success_exclusions - success_none
    for atom in sorted(missing_success_exclusions):
        errors.append(f"terminal_states.success:missing-safety-exclusion:{atom}")

    invalidator_rows = list_field(epg, "invalidators", errors)
    invalidators = unique_rows(invalidator_rows, "invalidator_id", errors, "invalidators")
    if not invalidators:
        errors.append("invalidators:empty")
    for index, row in enumerate(invalidator_rows):
        if not isinstance(row, dict):
            continue
        prefix = f"invalidators[{index}]."
        require(row, "condition", errors, prefix)
        if row.get("required_action") not in INVALIDATOR_ACTIONS:
            errors.append(f"{prefix}required_action")
        list_field(row, "affected_refs", errors, prefix)

    initial = object_field(epg, "initial_state", errors)
    if initial.get("state_version") != "EPS-v1":
        errors.append("initial_state.state_version")
    require(initial, "state_id", errors, "initial_state.")
    initial_atoms = list_field(initial, "satisfied_atoms", errors, "initial_state.")
    for atom in initial_atoms:
        if atom not in declared_atoms:
            errors.append(f"initial_state.satisfied_atoms:unknown:{atom}")
    completed = list_field(initial, "completed_actions", errors, "initial_state.")
    failed = list_field(initial, "failed_actions", errors, "initial_state.")
    for action_id in completed + failed:
        if action_id not in actions:
            errors.append(f"initial_state.action:unknown:{action_id}")
    resolved_unknowns = list_field(initial, "resolved_unknowns", errors, "initial_state.")
    for unknown_id in resolved_unknowns:
        if unknown_id not in unknowns:
            errors.append(f"initial_state.resolved_unknowns:unknown:{unknown_id}")
    closed_obligations = list_field(initial, "closed_obligations", errors, "initial_state.")
    for obligation_id in closed_obligations:
        if obligation_id not in obligations:
            errors.append(f"initial_state.closed_obligations:unknown:{obligation_id}")
    current_potential = object_field(initial, "current_potential", errors, "initial_state.")
    if current_potential != initial_potential:
        errors.append("initial_state.current_potential:mismatch")

    initial_atom_set = set(initial_atoms)
    completed_set = set(completed)
    failed_set = set(failed)
    overlap = completed_set & failed_set
    for action_id in sorted(overlap):
        errors.append(f"initial_state.action-both-completed-and-failed:{action_id}")
    for action_id in completed_set:
        if f"action:{action_id}=success" not in initial_atom_set:
            errors.append(
                f"initial_state.completed_actions:missing-success-atom:{action_id}"
            )
    for action_id in failed_set:
        if f"action:{action_id}=failure" not in initial_atom_set:
            errors.append(
                f"initial_state.failed_actions:missing-failure-atom:{action_id}"
            )
    for unknown_id in resolved_unknowns:
        if f"unknown:{unknown_id}=resolved" not in initial_atom_set:
            errors.append(
                f"initial_state.resolved_unknowns:missing-resolved-atom:{unknown_id}"
            )
    for obligation_id in closed_obligations:
        if f"obligation:{obligation_id}=closed" not in initial_atom_set:
            errors.append(
                f"initial_state.closed_obligations:missing-closed-atom:{obligation_id}"
            )
    for unknown_id, row in unknowns.items():
        status = row.get("status")
        if status == "resolved" and unknown_id not in set(resolved_unknowns):
            errors.append(
                f"belief.unknowns:{unknown_id}:resolved-status-missing-initial-state"
            )
        if status == "open" and unknown_id in set(resolved_unknowns):
            errors.append(
                f"belief.unknowns:{unknown_id}:open-status-but-initially-resolved"
            )
        if status == "blocked" and f"unknown:{unknown_id}=blocked" not in initial_atom_set:
            errors.append(
                f"belief.unknowns:{unknown_id}:blocked-status-missing-atom"
            )

    if initial.get("active_action_id") not in (None, ""):
        if initial.get("active_action_id") not in actions:
            errors.append("initial_state.active_action_id:unknown")

    challenge = object_field(epg, "challenge", errors)
    if challenge.get("disposition") not in {"adopt", "defer", "reject", "none", "return_to_spec", "return_to_grill"}:
        errors.append("challenge.disposition")
    require(challenge, "reason", errors, "challenge.")
    list_field(challenge, "affected_refs", errors, "challenge.")
    if not isinstance(challenge.get("source_change_required"), bool):
        errors.append("challenge.source_change_required")
    if challenge.get("source_change_required") and challenge.get("disposition") not in {"return_to_spec", "return_to_grill"}:
        errors.append("challenge:source-change-needs-authority-return")

    revision_summary = object_field(epg, "revision_summary", errors)
    if revision > 1 and not revision_summary.get("parent_diff_ref"):
        errors.append("revision_summary.parent_diff_ref")
    list_field(revision_summary, "policy_changes", errors, "revision_summary.")
    semantic_changes = list_field(revision_summary, "semantic_changes", errors, "revision_summary.")
    source_changes = list_field(revision_summary, "source_changes", errors, "revision_summary.")

    gate = object_field(epg, "gate", errors)
    semantic_drift = gate.get("semantic_drift")
    if semantic_drift not in SEMANTIC_DRIFT:
        errors.append("gate.semantic_drift")
    if mode == "spec_handoff" and semantic_changes and semantic_drift != "authorized":
        errors.append("spec_handoff:unauthorized-semantic-change")
    if semantic_drift == "none" and semantic_changes:
        errors.append("gate.semantic_drift:none-with-semantic-changes")
    if semantic_drift == "authorized" and not source_changes:
        warnings.append("gate.semantic_drift:authorized-without-source-change")

    # Validate all referenced atoms after collecting every declaration.
    all_referenced_atoms = condition_referenced_atoms | terminal_condition_atoms
    for action_id, action in actions.items():
        condition = action.get("preconditions", {})
        if isinstance(condition, dict):
            all_referenced_atoms |= set(condition.get("all", [])) | set(condition.get("any", [])) | set(condition.get("none", []))
        rollback = action.get("rollback", {})
        if isinstance(rollback, dict):
            all_referenced_atoms |= set(rollback.get("trigger_atoms", []))
    for atom in sorted(all_referenced_atoms):
        if atom not in declared_atoms:
            errors.append(f"policy:unknown-atom:{atom}")

    selected_actions = {action_id for action_id, rule_ids in selected_by_rule.items() if rule_ids}
    rollback_refs = {
        str(action.get("rollback", {}).get("action_id"))
        for action in actions.values()
        if isinstance(action.get("rollback"), dict) and action.get("rollback", {}).get("action_id")
    }
    unreachable_actions = set(actions) - selected_actions - rollback_refs
    for action_id in sorted(unreachable_actions):
        errors.append(f"policy:unreachable-action:{action_id}")

    # Outcome closure: every modeled observation outcome must lead to a rule,
    # terminal, shield, rollback, or explicit replan condition. This prevents a
    # superficially complete policy from going open-loop on one adverse result.
    successor_atoms = all_referenced_atoms
    dangling_outcomes: list[str] = []
    for action_id in actions:
        action_atoms = {
            f"action:{action_id}=success",
            f"action:{action_id}=failure",
        }
        handled_any = bool(action_atoms & successor_atoms)
        missing_observation_outcomes: list[str] = []
        for observation_id in (
            action_expected_obs.get(action_id, set())
            | action_failure_obs.get(action_id, set())
        ):
            atoms = observation_atoms.get(observation_id, set())
            if atoms:
                handled_any = True
            for atom in atoms:
                if atom not in successor_atoms:
                    missing_observation_outcomes.append(atom)
                    errors.append(
                        f"policy:unhandled-observation-outcome:{action_id}:{atom}"
                    )
        if not handled_any:
            dangling_outcomes.append(action_id)
            errors.append(f"policy:dangling-action-outcome:{action_id}")
        elif missing_observation_outcomes:
            dangling_outcomes.append(action_id)

    critical_unknowns_observable = True
    for unknown_id in critical_open_unknowns:
        row = unknowns[unknown_id]
        observation_refs = set(row.get("observation_refs", []))
        resolvers = unknown_resolvers.get(unknown_id, set())
        correlated_resolver = any(
            bool(action_expected_obs.get(action_id, set()) & observation_refs)
            for action_id in resolvers
        )
        if not observation_refs or not resolvers or not correlated_resolver:
            critical_unknowns_observable = False
            errors.append(f"belief.unknowns:{unknown_id}:no-observable-resolver")

    obligations_covered = all(bool(obligation_closers[obligation_id]) for obligation_id in obligations)
    for obligation_id, closers in obligation_closers.items():
        if not closers:
            errors.append(f"goal.obligations:{obligation_id}:no-closing-action")

    potential_complete = (
        bool(dimensions)
        and set(initial_potential) == set(dimensions)
        and not (potential_delta_keys - set(dimensions))
    )
    policy_references_valid = not any(
        token in error
        for error in errors
        for token in ("unknown:", "unknown-atom", "invalid-atom", "unreachable-action")
    )
    policy_closed = (
        bool(rules)
        and not dangling_outcomes
        and not cycles
        and terminal_rules_complete
    )
    terminal_states_complete = (
        all(isinstance(terminal_states.get(name), dict) for name in TERMINALS)
        and terminal_rules_complete
        and not missing_success_exclusions
    )
    source_current = is_yes(source.get("current"))
    semantic_ok = semantic_drift in {"none", "authorized"}
    challenge_allows_runtime = (
        challenge.get("disposition") not in {"return_to_spec", "return_to_grill"}
        and challenge.get("source_change_required") is False
    )
    fresh_eyes = gate.get("fresh_eyes_blockers")
    if not isinstance(fresh_eyes, int) or fresh_eyes < 0:
        errors.append("gate.fresh_eyes_blockers")
        fresh_eyes = 1
    downstream_ready = all(
        (
            source_current,
            semantic_ok,
            obligations_covered,
            critical_unknowns_observable,
            actions_bounded,
            policy_references_valid,
            policy_closed,
            safety_shield_complete,
            potential_complete,
            terminal_states_complete,
            challenge_allows_runtime,
            fresh_eyes == 0,
        )
    )
    policy_ready = downstream_ready

    for key, derived in (
        ("source_current", source_current),
        ("obligations_covered", obligations_covered),
        ("critical_unknowns_observable_or_blocked", critical_unknowns_observable),
        ("actions_bounded", actions_bounded),
        ("policy_references_valid", policy_references_valid),
        ("policy_closed", policy_closed),
        ("safety_shield_complete", safety_shield_complete),
        ("potential_complete", potential_complete),
        ("terminal_states_complete", terminal_states_complete),
        ("downstream_runtime_ready", downstream_ready),
        ("policy_ready", policy_ready),
    ):
        bool_claim(gate, key, derived, errors, "gate.")

    handoff = object_field(epg, "handoff", errors)
    if handoff.get("next_owner") not in HANDOFF_OWNERS:
        errors.append("handoff.next_owner")
    if not (is_yes(handoff.get("runtime_ready")) or is_no(handoff.get("runtime_ready"))):
        errors.append("handoff.runtime_ready")
    if not is_no(handoff.get("mutation_allowed")):
        errors.append("handoff.mutation_allowed:must-be-no")
    if handoff.get("gate_result") not in HANDOFF_RESULTS:
        errors.append("handoff.gate_result")
    require(handoff, "reason", errors, "handoff.")
    expected_runtime_ready = policy_ready and handoff.get("next_owner") in {"st", "actuating"}
    if is_yes(handoff.get("runtime_ready")) != expected_runtime_ready:
        errors.append("handoff.runtime_ready:contradicts-derived-value")
    if policy_ready and handoff.get("gate_result") != "pass":
        errors.append("handoff.gate_result:must-be-pass-when-ready")
    if not policy_ready and handoff.get("gate_result") == "pass":
        errors.append("handoff.gate_result:pass-while-not-ready")

    digest = canonical_digest(epg)
    derived = {
        "computed_digest": digest,
        "source_mode": mode,
        "regime": regime_kind,
        "policy_ready": policy_ready,
        "source_current": source_current,
        "obligations": len(obligations),
        "facts": len(facts),
        "unknowns": len(unknowns),
        "observations": len(observations),
        "actions": len(actions),
        "rules": len(rules),
        "shield_rules": len(shields),
        "potential_dimensions": len(dimensions),
        "critical_open_unknowns": sorted(critical_open_unknowns),
        "unreachable_actions": sorted(unreachable_actions),
        "dangling_outcomes": sorted(dangling_outcomes),
        "dependency_cycles": cycles,
        "declared_atoms": sorted(declared_atoms),
    }
    return errors, warnings, derived


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="EPG JSON/YAML or proposed-plan Markdown")
    args = parser.parse_args()
    try:
        epg, metadata = load_epg(args.file)
        errors, warnings, derived = validate_policy(epg)
    except Exception as exc:
        return emit("execution_policy_gate", {}, [str(exc)], [])
    return emit(
        "execution_policy_gate",
        {
            "policy_id": epg.get("policy_id"),
            "revision": epg.get("revision"),
            "source_kind": metadata.get("source_kind"),
            **derived,
        },
        errors,
        warnings,
    )


if __name__ == "__main__":
    raise SystemExit(main())
