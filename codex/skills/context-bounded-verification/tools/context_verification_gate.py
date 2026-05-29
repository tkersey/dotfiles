#!/usr/bin/env python3
"""Mechanical contract checker for context-bounded-verification packets.

The checker validates output shape, current-artifact binding, evidence versus
intuition separation, actionability gating, direction/scope fit, validation
proof, authority/subagent receipts, closure consistency, and handoff safety.

It cannot prove semantic correctness. It deliberately blocks incomplete,
stale-state, weak-evidence, wrong-objective, validation-laundered, or
authority-laundered packets before pass/readiness/implementation handoff.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - exercised only when PyYAML missing
    yaml = None

PACKET_VERSION = "CBV-GATE-v1"
SKILL_NAME = "context-bounded-verification"

ALLOWED_MODE = {
    "implementation",
    "review",
    "closure",
    "verification",
    "validation-only",
    "no-change",
    "handoff",
    "audit",
}
ALLOWED_TIER = {"tier0", "tier1", "tier2", "tier3"}
TIER_ORDER = {"tier0": 0, "tier1": 1, "tier2": 2, "tier3": 3}
ALLOWED_ARTIFACT_SOURCE = {
    "current-tree",
    "current-diff",
    "pull-request",
    "supplied-snippet",
    "prior-session",
    "unknown",
}
ALLOWED_FRESHNESS = {"current", "stale", "superseded", "unknown"}
ALLOWED_DIRTY_STATE = {"clean", "dirty", "unknown", "not-applicable"}
ALLOWED_DIRECTION_FIT = {"aligned", "partial", "conflicting", "unknown"}
ALLOWED_DIRECTION_SOURCE = {
    "user-current-instruction",
    "plan",
    "pr-body",
    "issue",
    "repo-convention",
    "current-artifact",
    "unknown",
}
ALLOWED_CLAIM_TYPE = {"validity", "actionability", "scope", "risk", "proof", "closure"}
ALLOWED_EVIDENCE_KIND = {
    "current-artifact",
    "current-diff",
    "current-test",
    "current-ci",
    "current-command",
    "manual-inspection",
    "runtime-observation",
    "prior-session",
    "memory",
    "reviewer-claim",
    "none",
}
CURRENT_EVIDENCE_KINDS = {
    "current-artifact",
    "current-diff",
    "current-test",
    "current-ci",
    "current-command",
    "manual-inspection",
    "runtime-observation",
}
EXECUTABLE_EVIDENCE_KINDS = {"current-test", "current-ci", "current-command", "runtime-observation"}
WEAK_EVIDENCE_KINDS = {"prior-session", "memory", "reviewer-claim", "none"}
ALLOWED_SUPPORTS = {"yes", "partial", "no", "unknown"}
ALLOWED_ARTIFACT_MATCH = {"yes", "no", "unknown"}
ALLOWED_ACTIONABILITY = {
    "implement",
    "validate-only",
    "proof-only",
    "no-change",
    "defer",
    "blocked",
    "closure-pass",
    "none",
}
ACTION_REQUIRING_CURRENT_EVIDENCE = {"implement", "handoff", "closure-pass"}
ALLOWED_SURFACE_STATUS = {"checked", "not-applicable", "unchecked", "unknown"}
ALLOWED_COMMAND_RESULT = {"pass", "fail", "not-run", "skipped"}
ALLOWED_YES_NO_UNKNOWN = {"yes", "no", "unknown"}
ALLOWED_YES_NO = {"yes", "no"}
ALLOWED_READINESS = {
    "pass",
    "pass-with-residual-risk",
    "validate-only",
    "proof-only",
    "no-change",
    "defer",
    "blocked",
}
PASSING_READINESS = {"pass", "pass-with-residual-risk"}
BLOCKING_READINESS = {"blocked", "defer"}
ALLOWED_HANDOFF_TARGET = {
    "none",
    "accretive-implementer",
    "fixed-point-driver",
    "review-adjudication",
    "verification-closure",
    "human-owner",
    "other",
}
ALLOWED_ROOT_OWNED = {
    "tier-decision",
    "scope-boundary",
    "artifact-state-acceptance",
    "final-readiness",
    "implementation-authorization",
    "handoff-routing",
}
REQUIRED_ROOT_OWNED = {
    "tier-decision",
    "scope-boundary",
    "artifact-state-acceptance",
    "final-readiness",
    "implementation-authorization",
    "handoff-routing",
}
ALLOWED_AUTHORITY_ROLE = {
    "context-evidence-authority",
    "context-scope-direction-authority",
    "context-blast-radius-authority",
    "context-closure-authority",
    "context_evidence_authority",
    "context_scope_direction_authority",
    "context_blast_radius_authority",
    "context_closure_authority",
}
ALLOWED_PACKET_STATUS = {"accepted", "rejected", "not-used"}
ALLOWED_CLEARANCE = {"clear", "veto", "unresolved", "not-required"}
IMPLEMENTATION_TARGETS = {"accretive-implementer", "fixed-point-driver", "other"}

REQUIRED_TOP = [
    "packet_version",
    "skill",
    "mode",
    "objective",
    "artifact_state",
    "tier",
    "scope",
    "direction_fit",
    "evidence_ledger",
    "blast_radius",
    "validation",
    "authority",
    "closure",
    "handoff",
]
REQUIRED_OBJECTIVE = ["current_workflow_objective", "semantic_change", "done_condition"]
REQUIRED_ARTIFACT = ["state_id", "source", "freshness", "dirty_state", "evidence_refs"]
REQUIRED_TIER = ["declared", "drivers", "rationale"]
REQUIRED_SCOPE = ["in_scope", "out_of_scope", "must_not_change"]
REQUIRED_DIRECTION = ["current_objective_fit", "direction_source", "stale_or_wrong_objective_pressure"]
REQUIRED_EVIDENCE = [
    "id",
    "claim",
    "claim_type",
    "evidence_kind",
    "evidence_ref",
    "artifact_state_match",
    "supports",
    "actionability",
]
REQUIRED_SURFACE = ["name", "status", "evidence_ref"]
REQUIRED_COMMAND = ["command", "result", "evidence_ref", "artifact_state_match"]
REQUIRED_VALIDATION = [
    "commands",
    "tests_added_or_updated",
    "negative_or_counterexample_checks",
    "proof_surface_changed",
    "test_gap_reason",
]
REQUIRED_AUTHORITY = ["root_owned", "fanout", "subagent_packets"]
REQUIRED_AUTHORITY_FANOUT = ["required", "reason"]
REQUIRED_SUBAGENT_PACKET = [
    "role",
    "packet_status",
    "artifact_state_match",
    "scope_match",
    "clearance",
    "reason",
]
REQUIRED_CLOSURE = ["readiness", "closure_claim", "blockers", "remaining_risk", "next_action"]
REQUIRED_HANDOFF = ["allowed", "target", "agenda", "must_not_do"]


@dataclass
class GateResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_packet(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = parse_text(text, path.suffix.lower())
    if not isinstance(data, Mapping):
        raise ValueError("packet root must be a mapping/object")
    if "verification_packet" in data:
        packet = data["verification_packet"]
    else:
        packet = data
    if not isinstance(packet, Mapping):
        raise ValueError("verification_packet must be a mapping/object")
    return normalize_scalars(dict(packet))


def parse_text(text: str, suffix: str = "") -> Any:
    stripped = text.strip()
    if not stripped:
        raise ValueError("empty packet")

    # Direct JSON first for precise errors on .json files.
    if suffix == ".json" or stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            if suffix == ".json":
                raise

    # Markdown fenced packet: prefer a block containing verification_packet or packet_version.
    for block in extract_fenced_blocks(text):
        if "verification_packet" in block or "packet_version" in block:
            return parse_yaml_or_json(block)

    return parse_yaml_or_json(stripped)




def normalize_scalars(value: Any) -> Any:
    """Normalize YAML 1.1 booleans used for schema enums.

    PyYAML treats unquoted `yes`/`no` as booleans. The packet contract uses
    yes/no as enum strings, so normalize booleans recursively to preserve the
    documented YAML shape.
    """
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return [normalize_scalars(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_scalars(item) for key, item in value.items()}
    return value


def extract_fenced_blocks(text: str) -> Iterable[str]:
    fence = re.compile(r"```(?:yaml|yml|json|verification_packet)?\s*\n(.*?)\n```", re.IGNORECASE | re.DOTALL)
    for match in fence.finditer(text):
        yield match.group(1).strip()


def parse_yaml_or_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        pass
    if yaml is None:
        raise RuntimeError("PyYAML is required for YAML or Markdown packet parsing")
    return yaml.safe_load(text)


def get_mapping(packet: Mapping[str, Any], key: str, result: GateResult) -> Dict[str, Any]:
    value = packet.get(key)
    if not isinstance(value, Mapping):
        result.error(f"{key}: must be a mapping/object")
        return {}
    return dict(value)


def get_list(mapping: Mapping[str, Any], key: str, result: GateResult, path: str) -> List[Any]:
    value = mapping.get(key)
    if not isinstance(value, list):
        result.error(f"{path}.{key}: must be a list")
        return []
    return value


def require_fields(mapping: Mapping[str, Any], fields: Sequence[str], result: GateResult, path: str) -> None:
    for field_name in fields:
        if field_name not in mapping:
            result.error(f"{path}: missing required field `{field_name}`")
        elif mapping[field_name] is None:
            result.error(f"{path}.{field_name}: must not be null")
        elif isinstance(mapping[field_name], str) and not mapping[field_name].strip():
            result.error(f"{path}.{field_name}: must not be empty")


def require_enum(value: Any, allowed: Iterable[str], result: GateResult, path: str) -> Optional[str]:
    allowed_set = set(allowed)
    if not isinstance(value, str):
        result.error(f"{path}: must be a string in {sorted(allowed_set)}")
        return None
    if value not in allowed_set:
        result.error(f"{path}: invalid value {value!r}; expected one of {sorted(allowed_set)}")
        return value
    return value


def nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def validate_packet(packet: Mapping[str, Any]) -> Tuple[GateResult, Dict[str, Any]]:
    result = GateResult()
    summary: Dict[str, Any] = {}

    require_fields(packet, REQUIRED_TOP, result, "verification_packet")

    packet_version = packet.get("packet_version")
    if packet_version != PACKET_VERSION:
        result.error(f"packet_version: expected {PACKET_VERSION!r}, got {packet_version!r}")
    if packet.get("skill") != SKILL_NAME:
        result.error(f"skill: expected {SKILL_NAME!r}, got {packet.get('skill')!r}")

    mode = require_enum(packet.get("mode"), ALLOWED_MODE, result, "mode")
    summary["mode"] = mode

    objective = get_mapping(packet, "objective", result)
    artifact = get_mapping(packet, "artifact_state", result)
    tier = get_mapping(packet, "tier", result)
    scope = get_mapping(packet, "scope", result)
    direction = get_mapping(packet, "direction_fit", result)
    blast = get_mapping(packet, "blast_radius", result)
    validation = get_mapping(packet, "validation", result)
    authority = get_mapping(packet, "authority", result)
    closure = get_mapping(packet, "closure", result)
    handoff = get_mapping(packet, "handoff", result)

    require_fields(objective, REQUIRED_OBJECTIVE, result, "objective")
    require_fields(artifact, REQUIRED_ARTIFACT, result, "artifact_state")
    require_fields(tier, REQUIRED_TIER, result, "tier")
    require_fields(scope, REQUIRED_SCOPE, result, "scope")
    require_fields(direction, REQUIRED_DIRECTION, result, "direction_fit")
    require_fields(validation, REQUIRED_VALIDATION, result, "validation")
    require_fields(authority, REQUIRED_AUTHORITY, result, "authority")
    require_fields(closure, REQUIRED_CLOSURE, result, "closure")
    require_fields(handoff, REQUIRED_HANDOFF, result, "handoff")

    tier_declared = require_enum(tier.get("declared"), ALLOWED_TIER, result, "tier.declared")
    summary["tier"] = tier_declared
    tier_level = TIER_ORDER.get(tier_declared or "tier0", 0)
    if isinstance(tier.get("drivers"), list):
        if tier_level >= 2 and not tier.get("drivers"):
            result.error("tier.drivers: Tier 2/Tier 3 packets require at least one concrete tier driver")
    else:
        result.error("tier.drivers: must be a list")

    artifact_source = require_enum(artifact.get("source"), ALLOWED_ARTIFACT_SOURCE, result, "artifact_state.source")
    artifact_freshness = require_enum(artifact.get("freshness"), ALLOWED_FRESHNESS, result, "artifact_state.freshness")
    require_enum(artifact.get("dirty_state"), ALLOWED_DIRTY_STATE, result, "artifact_state.dirty_state")
    artifact_refs = get_list(artifact, "evidence_refs", result, "artifact_state")
    if not artifact_refs:
        result.error("artifact_state.evidence_refs: require at least one current artifact/diff/commit/PR evidence reference")
    if artifact_source == "prior-session":
        result.warn("artifact_state.source: prior-session source is explanatory only and cannot support pass/handoff")

    in_scope = get_list(scope, "in_scope", result, "scope")
    out_of_scope = get_list(scope, "out_of_scope", result, "scope")
    must_not_change = get_list(scope, "must_not_change", result, "scope")
    if tier_level >= 1:
        if not in_scope:
            result.error("scope.in_scope: Tier 1+ requires explicit in-scope items")
        if not out_of_scope:
            result.error("scope.out_of_scope: Tier 1+ requires explicit out-of-scope/non-goal items")
        if not must_not_change:
            result.error("scope.must_not_change: Tier 1+ requires preserved invariants/non-changes")

    current_objective_fit = require_enum(
        direction.get("current_objective_fit"), ALLOWED_DIRECTION_FIT, result, "direction_fit.current_objective_fit"
    )
    require_enum(direction.get("direction_source"), ALLOWED_DIRECTION_SOURCE, result, "direction_fit.direction_source")
    stale_pressure = get_list(direction, "stale_or_wrong_objective_pressure", result, "direction_fit")

    evidence_items = packet.get("evidence_ledger")
    if not isinstance(evidence_items, list):
        result.error("evidence_ledger: must be a list")
        evidence_items = []
    if not evidence_items:
        result.error("evidence_ledger: require at least one evidence item")

    current_evidence = 0
    executable_evidence = 0
    actionable_claims = 0
    weak_actionable = 0
    closure_claims = 0
    evidence_ids = set()
    for idx, item in enumerate(evidence_items):
        path = f"evidence_ledger[{idx}]"
        if not isinstance(item, Mapping):
            result.error(f"{path}: must be a mapping/object")
            continue
        require_fields(item, REQUIRED_EVIDENCE, result, path)
        item_id = item.get("id")
        if isinstance(item_id, str):
            if item_id in evidence_ids:
                result.error(f"{path}.id: duplicate id {item_id!r}")
            evidence_ids.add(item_id)
        claim_type = require_enum(item.get("claim_type"), ALLOWED_CLAIM_TYPE, result, f"{path}.claim_type")
        evidence_kind = require_enum(item.get("evidence_kind"), ALLOWED_EVIDENCE_KIND, result, f"{path}.evidence_kind")
        artifact_match = require_enum(
            item.get("artifact_state_match"), ALLOWED_ARTIFACT_MATCH, result, f"{path}.artifact_state_match"
        )
        supports = require_enum(item.get("supports"), ALLOWED_SUPPORTS, result, f"{path}.supports")
        actionability = require_enum(item.get("actionability"), ALLOWED_ACTIONABILITY, result, f"{path}.actionability")
        if evidence_kind in CURRENT_EVIDENCE_KINDS and artifact_match == "yes" and supports in {"yes", "partial"}:
            current_evidence += 1
        if evidence_kind in EXECUTABLE_EVIDENCE_KINDS and artifact_match == "yes" and supports == "yes":
            executable_evidence += 1
        if actionability in {"implement", "closure-pass"}:
            actionable_claims += 1
            if evidence_kind not in CURRENT_EVIDENCE_KINDS or artifact_match != "yes" or supports != "yes":
                weak_actionable += 1
                result.error(
                    f"{path}: actionability={actionability!r} requires current evidence, artifact_state_match=yes, supports=yes"
                )
        if claim_type == "closure" or actionability == "closure-pass":
            closure_claims += 1
        if evidence_kind in WEAK_EVIDENCE_KINDS and actionability in {"implement", "closure-pass"}:
            result.error(f"{path}: weak evidence kind {evidence_kind!r} cannot support {actionability!r}")
        if evidence_kind == "none" and supports == "yes":
            result.error(f"{path}: evidence_kind=none cannot supports=yes")
        if not nonempty(item.get("evidence_ref")):
            result.error(f"{path}.evidence_ref: require concrete file:line, command, test, log, diff, or artifact ref")

    summary["current_evidence_items"] = current_evidence
    summary["executable_evidence_items"] = executable_evidence
    summary["actionable_claims"] = actionable_claims
    summary["closure_claims"] = closure_claims

    surfaces = blast.get("surfaces_checked")
    if not isinstance(surfaces, list):
        result.error("blast_radius.surfaces_checked: must be a list")
        surfaces = []
    unchecked_material = blast.get("unchecked_material_surfaces")
    if not isinstance(unchecked_material, list):
        result.error("blast_radius.unchecked_material_surfaces: must be a list")
        unchecked_material = []
    checked_surfaces = 0
    for idx, surface in enumerate(surfaces):
        path = f"blast_radius.surfaces_checked[{idx}]"
        if not isinstance(surface, Mapping):
            result.error(f"{path}: must be a mapping/object")
            continue
        require_fields(surface, REQUIRED_SURFACE, result, path)
        status = require_enum(surface.get("status"), ALLOWED_SURFACE_STATUS, result, f"{path}.status")
        if status == "checked":
            checked_surfaces += 1
        if status == "checked" and not nonempty(surface.get("evidence_ref")):
            result.error(f"{path}.evidence_ref: checked surfaces require evidence_ref")
    summary["checked_surfaces"] = checked_surfaces
    if tier_level >= 2 and checked_surfaces == 0:
        result.error("blast_radius: Tier 2/Tier 3 packets require at least one checked blast-radius surface")

    commands = validation.get("commands")
    if not isinstance(commands, list):
        result.error("validation.commands: must be a list")
        commands = []
    passing_commands = 0
    failing_commands = 0
    not_run_commands = 0
    current_passing_commands = 0
    for idx, command in enumerate(commands):
        path = f"validation.commands[{idx}]"
        if not isinstance(command, Mapping):
            result.error(f"{path}: must be a mapping/object")
            continue
        require_fields(command, REQUIRED_COMMAND, result, path)
        command_result = require_enum(command.get("result"), ALLOWED_COMMAND_RESULT, result, f"{path}.result")
        command_match = require_enum(
            command.get("artifact_state_match"), ALLOWED_ARTIFACT_MATCH, result, f"{path}.artifact_state_match"
        )
        if command_result == "pass":
            passing_commands += 1
            if command_match == "yes":
                current_passing_commands += 1
        elif command_result == "fail":
            failing_commands += 1
        elif command_result in {"not-run", "skipped"}:
            not_run_commands += 1
        if command_result == "pass" and command_match != "yes":
            result.error(f"{path}: passing command must match current artifact_state")
        if not nonempty(command.get("evidence_ref")):
            result.error(f"{path}.evidence_ref: require command log/result reference")
    tests_added = get_list(validation, "tests_added_or_updated", result, "validation")
    negative_checks = get_list(validation, "negative_or_counterexample_checks", result, "validation")
    proof_surface_changed = require_enum(
        validation.get("proof_surface_changed"), ALLOWED_YES_NO_UNKNOWN, result, "validation.proof_surface_changed"
    )
    summary["passing_commands"] = passing_commands
    summary["current_passing_commands"] = current_passing_commands
    summary["failing_commands"] = failing_commands
    summary["not_run_or_skipped_commands"] = not_run_commands
    if failing_commands:
        result.warn("validation.commands: failing commands require blocked/defer/validate-only closure unless explicitly non-material")
    if proof_surface_changed == "yes" and not negative_checks:
        result.error("validation.negative_or_counterexample_checks: proof/verifier/checker changes require a negative or counterexample check")
    if tier_level >= 2 and not commands and not nonempty(validation.get("test_gap_reason")):
        result.error("validation.commands/test_gap_reason: Tier 2/Tier 3 requires commands or a concrete test-gap reason")

    root_owned = get_list(authority, "root_owned", result, "authority")
    root_owned_set = set(x for x in root_owned if isinstance(x, str))
    invalid_root_owned = root_owned_set - ALLOWED_ROOT_OWNED
    if invalid_root_owned:
        result.error(f"authority.root_owned: invalid root-owned entries {sorted(invalid_root_owned)}")
    missing_root_owned = REQUIRED_ROOT_OWNED - root_owned_set
    if missing_root_owned:
        result.error(f"authority.root_owned: missing required root-owned authority entries {sorted(missing_root_owned)}")

    fanout = authority.get("fanout")
    if not isinstance(fanout, Mapping):
        result.error("authority.fanout: must be a mapping/object")
        fanout = {}
    require_fields(fanout, REQUIRED_AUTHORITY_FANOUT, result, "authority.fanout")
    fanout_required = require_enum(fanout.get("required"), ALLOWED_YES_NO, result, "authority.fanout.required")
    subagent_packets = authority.get("subagent_packets")
    if not isinstance(subagent_packets, list):
        result.error("authority.subagent_packets: must be a list")
        subagent_packets = []
    if fanout_required == "yes" and not subagent_packets:
        result.error("authority.subagent_packets: fanout.required=yes requires at least one subagent packet or a rejected packet receipt")
    veto_count = 0
    unresolved_count = 0
    accepted_packets = 0
    for idx, packet_item in enumerate(subagent_packets):
        path = f"authority.subagent_packets[{idx}]"
        if not isinstance(packet_item, Mapping):
            result.error(f"{path}: must be a mapping/object")
            continue
        require_fields(packet_item, REQUIRED_SUBAGENT_PACKET, result, path)
        require_enum(packet_item.get("role"), ALLOWED_AUTHORITY_ROLE, result, f"{path}.role")
        status = require_enum(packet_item.get("packet_status"), ALLOWED_PACKET_STATUS, result, f"{path}.packet_status")
        artifact_state_match = require_enum(
            packet_item.get("artifact_state_match"), ALLOWED_ARTIFACT_MATCH, result, f"{path}.artifact_state_match"
        )
        scope_match = require_enum(packet_item.get("scope_match"), ALLOWED_ARTIFACT_MATCH, result, f"{path}.scope_match")
        clearance = require_enum(packet_item.get("clearance"), ALLOWED_CLEARANCE, result, f"{path}.clearance")
        if status == "accepted":
            accepted_packets += 1
            if artifact_state_match != "yes" or scope_match != "yes":
                result.error(f"{path}: accepted packet requires artifact_state_match=yes and scope_match=yes")
        if status == "rejected" and clearance == "clear":
            result.error(f"{path}: rejected packet cannot clearance=clear")
        if clearance == "veto":
            veto_count += 1
        elif clearance == "unresolved":
            unresolved_count += 1
    summary["authority_packets_accepted"] = accepted_packets
    summary["authority_vetoes"] = veto_count
    summary["authority_unresolved"] = unresolved_count

    readiness = require_enum(closure.get("readiness"), ALLOWED_READINESS, result, "closure.readiness")
    blockers = get_list(closure, "blockers", result, "closure")
    remaining_risk = get_list(closure, "remaining_risk", result, "closure")
    summary["readiness"] = readiness
    if readiness in PASSING_READINESS:
        if artifact_freshness != "current":
            result.error("closure.readiness: pass/pass-with-residual-risk requires artifact_state.freshness=current")
        if current_objective_fit != "aligned":
            result.error("closure.readiness: pass/pass-with-residual-risk requires direction_fit.current_objective_fit=aligned")
        if blockers:
            result.error("closure.blockers: pass/pass-with-residual-risk cannot have blockers")
        if unchecked_material:
            result.error("blast_radius.unchecked_material_surfaces: pass cannot leave material unchecked surfaces")
        if veto_count or unresolved_count:
            result.error("authority.subagent_packets: pass cannot proceed with veto or unresolved authority clearance")
        if failing_commands:
            result.error("validation.commands: pass cannot proceed with failing commands")
        if weak_actionable:
            result.error("evidence_ledger: pass cannot include weak actionable claims")
        if tier_level >= 2 and current_passing_commands == 0 and executable_evidence == 0:
            result.error("closure.readiness: Tier 2/Tier 3 pass requires current executable proof (command/test/CI/runtime)")
        if tier_level >= 2 and not remaining_risk:
            result.error("closure.remaining_risk: Tier 2/Tier 3 pass requires explicit residual risk, even if `none known`")
        if not nonempty(closure.get("closure_claim")):
            result.error("closure.closure_claim: pass requires a concrete bounded closure claim")
    elif readiness in BLOCKING_READINESS:
        if not blockers:
            result.error("closure.blockers: blocked/defer readiness requires at least one concrete blocker")
    elif readiness in {"validate-only", "proof-only"}:
        if not nonempty(closure.get("next_action")):
            result.error("closure.next_action: validate-only/proof-only readiness requires the exact next validation/proof action")
    elif readiness == "no-change":
        if any(item.get("actionability") == "implement" for item in evidence_items if isinstance(item, Mapping)):
            result.error("closure.readiness=no-change conflicts with evidence_ledger actionability=implement")

    if stale_pressure and readiness in PASSING_READINESS:
        result.error("direction_fit.stale_or_wrong_objective_pressure: pass requires stale/wrong-objective pressure to be cleared, not merely listed")

    handoff_allowed = require_enum(handoff.get("allowed"), ALLOWED_YES_NO, result, "handoff.allowed")
    handoff_target = require_enum(handoff.get("target"), ALLOWED_HANDOFF_TARGET, result, "handoff.target")
    agenda = get_list(handoff, "agenda", result, "handoff")
    must_not_do = get_list(handoff, "must_not_do", result, "handoff")
    summary["handoff_allowed"] = handoff_allowed
    summary["handoff_target"] = handoff_target
    if handoff_allowed == "yes":
        if handoff_target == "none":
            result.error("handoff.target: allowed=yes requires a non-none target")
        if not agenda:
            result.error("handoff.agenda: allowed=yes requires a concrete agenda")
        if not must_not_do:
            result.error("handoff.must_not_do: allowed=yes requires must_not_do boundaries")
        if artifact_freshness != "current":
            result.error("handoff.allowed: yes requires artifact_state.freshness=current")
        if current_objective_fit != "aligned":
            result.error("handoff.allowed: yes requires direction_fit.current_objective_fit=aligned")
        if blockers or readiness in {"blocked", "defer"}:
            result.error("handoff.allowed: yes cannot coexist with blockers or blocked/defer readiness")
        if veto_count or unresolved_count:
            result.error("handoff.allowed: yes cannot proceed with authority veto/unresolved clearance")
        if handoff_target in IMPLEMENTATION_TARGETS:
            has_implementation_evidence = any(
                isinstance(item, Mapping)
                and item.get("actionability") == "implement"
                and item.get("evidence_kind") in CURRENT_EVIDENCE_KINDS
                and item.get("artifact_state_match") == "yes"
                and item.get("supports") == "yes"
                for item in evidence_items
            )
            if not has_implementation_evidence:
                result.error("handoff: implementation target requires at least one current implement-actionable evidence item")
            if readiness in {"validate-only", "proof-only", "no-change"}:
                result.error("handoff: implementation target cannot be paired with validate-only/proof-only/no-change readiness")
    else:
        if handoff_target != "none" and agenda:
            result.warn("handoff: allowed=no with target/agenda present; keep agenda only as non-authorized suggestion")

    if mode == "implementation" and readiness in {"no-change", "blocked", "defer"} and handoff_allowed == "yes":
        result.error("mode/readiness/handoff: implementation mode with no-change/blocked/defer cannot authorize handoff")
    if mode == "no-change" and handoff_allowed == "yes":
        result.error("mode=no-change cannot authorize implementation handoff")
    if mode in {"closure", "handoff"} and tier_level >= 2 and packet.get("packet_version") == PACKET_VERSION:
        # Good packet shape: leave note for humans that the checker is structural, not semantic.
        result.notes.append("Semantic correctness still requires human/repo-specific review; this gate checks anti-laundering structure.")

    return result, summary


def result_to_json(result: GateResult, summary: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "status": "PASS" if result.ok else "FAIL",
        "summary": dict(summary),
        "errors": result.errors,
        "warnings": result.warnings,
        "notes": result.notes,
    }


def make_valid_sample() -> Dict[str, Any]:
    return {
        "verification_packet": {
            "packet_version": PACKET_VERSION,
            "skill": SKILL_NAME,
            "mode": "closure",
            "objective": {
                "current_workflow_objective": "Verify PR readiness for route-specific certificate proof change.",
                "semantic_change": "Reject certificates whose route support witness does not match the selected provider.",
                "done_condition": "Current diff has a targeted negative test and passing proof command.",
            },
            "artifact_state": {
                "state_id": "git:abc123+diff:route-witness-v2",
                "source": "current-diff",
                "freshness": "current",
                "dirty_state": "dirty",
                "evidence_refs": ["git diff --stat", "src/cert.zig:120", "tests/cert_route.zig:44"],
            },
            "tier": {
                "declared": "tier2",
                "drivers": ["proof-surface", "generated-artifact", "public-runtime-behavior"],
                "rationale": "Verifier semantics and certificate proof surface changed.",
            },
            "scope": {
                "in_scope": ["certificate route witness checker", "negative route mismatch regression"],
                "out_of_scope": ["provider selection algorithm", "unrelated certificate fields"],
                "must_not_change": ["supported matching route certificates remain accepted"],
            },
            "direction_fit": {
                "current_objective_fit": "aligned",
                "direction_source": "user-current-instruction",
                "stale_or_wrong_objective_pressure": [],
            },
            "evidence_ledger": [
                {
                    "id": "E1",
                    "claim": "The new predicate checks selected provider identity, not only witness presence.",
                    "claim_type": "proof",
                    "evidence_kind": "current-artifact",
                    "evidence_ref": "src/cert.zig:120-155",
                    "artifact_state_match": "yes",
                    "supports": "yes",
                    "actionability": "closure-pass",
                },
                {
                    "id": "E2",
                    "claim": "Wrong-provider same-kind witness is rejected.",
                    "claim_type": "proof",
                    "evidence_kind": "current-test",
                    "evidence_ref": "tests/cert_route.zig:test rejects wrong provider route witness",
                    "artifact_state_match": "yes",
                    "supports": "yes",
                    "actionability": "closure-pass",
                },
            ],
            "blast_radius": {
                "surfaces_checked": [
                    {"name": "generated-artifact", "status": "checked", "evidence_ref": "src/cert.zig:120-155"},
                    {"name": "regression-tests", "status": "checked", "evidence_ref": "tests/cert_route.zig:44-89"},
                    {"name": "rollback", "status": "not-applicable", "evidence_ref": "local verifier-only change"},
                ],
                "unchecked_material_surfaces": [],
            },
            "validation": {
                "commands": [
                    {
                        "command": "zig build test --summary all",
                        "result": "pass",
                        "evidence_ref": "terminal:2026-05-29T13:00Z",
                        "artifact_state_match": "yes",
                    }
                ],
                "tests_added_or_updated": ["tests/cert_route.zig wrong-provider negative regression"],
                "negative_or_counterexample_checks": ["wrong-provider same-kind witness rejected"],
                "proof_surface_changed": "yes",
                "test_gap_reason": "none known",
            },
            "authority": {
                "root_owned": sorted(REQUIRED_ROOT_OWNED),
                "fanout": {"required": "no", "reason": "Single proof surface with direct current test evidence."},
                "subagent_packets": [],
            },
            "closure": {
                "readiness": "pass-with-residual-risk",
                "closure_claim": "Current diff appears ready for PR review on the route-witness proof surface.",
                "blockers": [],
                "remaining_risk": ["Only targeted regression was run; full downstream integration not exercised."],
                "next_action": "Open PR or request human review of route witness semantics.",
            },
            "handoff": {
                "allowed": "no",
                "target": "none",
                "agenda": [],
                "must_not_do": [],
            },
        }
    }


def make_invalid_sample() -> Dict[str, Any]:
    sample = make_valid_sample()["verification_packet"]
    sample = json.loads(json.dumps(sample))
    sample["artifact_state"]["freshness"] = "stale"
    sample["evidence_ledger"][0]["evidence_kind"] = "memory"
    sample["evidence_ledger"][0]["artifact_state_match"] = "unknown"
    sample["validation"]["commands"][0]["artifact_state_match"] = "no"
    sample["authority"]["subagent_packets"] = [
        {
            "role": "context-evidence-authority",
            "packet_status": "accepted",
            "artifact_state_match": "yes",
            "scope_match": "yes",
            "clearance": "veto",
            "reason": "Claim depends on stale evidence.",
        }
    ]
    sample["handoff"] = {
        "allowed": "yes",
        "target": "accretive-implementer",
        "agenda": ["Implement broader certificate rewrite"],
        "must_not_do": ["Do not use stale proof"],
    }
    return {"verification_packet": sample}


def run_self_test() -> int:
    valid_packet = make_valid_sample()["verification_packet"]
    invalid_packet = make_invalid_sample()["verification_packet"]
    valid_result, valid_summary = validate_packet(valid_packet)
    invalid_result, invalid_summary = validate_packet(invalid_packet)
    report = {
        "valid_sample": result_to_json(valid_result, valid_summary),
        "invalid_sample": result_to_json(invalid_result, invalid_summary),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if not valid_result.ok:
        print("self-test failed: valid sample did not pass", file=sys.stderr)
        return 1
    if invalid_result.ok:
        print("self-test failed: invalid sample did not fail", file=sys.stderr)
        return 1
    return 0


def write_example(path: Path) -> None:
    if yaml is not None and path.suffix.lower() in {".yaml", ".yml", ".md"}:
        packet = make_valid_sample()
        if path.suffix.lower() == ".md":
            body = "# Example Context-Bounded Verification Packet\n\n```yaml\n"
            body += yaml.safe_dump(packet, sort_keys=False)
            body += "```\n"
            path.write_text(body, encoding="utf-8")
        else:
            path.write_text(yaml.safe_dump(packet, sort_keys=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(make_valid_sample(), indent=2, sort_keys=True), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a context-bounded-verification verification_packet")
    parser.add_argument("packet", nargs="?", help="JSON/YAML/Markdown file containing verification_packet")
    parser.add_argument("--self-test", action="store_true", help="run built-in positive and negative contract tests")
    parser.add_argument("--write-example", metavar="PATH", help="write a valid example packet and exit")
    parser.add_argument("--warn-only", action="store_true", help="print failures but exit 0")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if args.write_example:
        write_example(Path(args.write_example))
        return 0

    if not args.packet:
        parser.error("packet is required unless --self-test or --write-example is used")

    try:
        packet = load_packet(Path(args.packet))
        result, summary = validate_packet(packet)
    except Exception as exc:
        output = {"status": "FAIL", "summary": {}, "errors": [f"parse/load error: {exc}"], "warnings": [], "notes": []}
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0 if args.warn_only else 1

    output = result_to_json(result, summary)
    print(json.dumps(output, indent=2, sort_keys=True))
    if result.ok or args.warn_only:
        return 0
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
