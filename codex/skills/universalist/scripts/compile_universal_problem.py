#!/usr/bin/env python3
"""Validate one evidence-bound Universal Problem packet and nominate a construction.

The compiler is a deterministic decision-support tool, not an architecture authority.
It validates a ``universal-problem/v6`` packet, checks one architectural axis and one
hole, evaluates theorem cards, and returns a proof-obligation/evidence-debt
certificate. The root workflow adjudicates the nomination and owns any consequential
Ledger/Seq decision receipt.

Default output uses repository-native engineering language. ``--explain-theory``
adds the expert construction name, theorem guidance, and source references without
changing eligibility or nomination.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

PROBLEM_SCHEMA = "universal-problem/v6"
CERTIFICATE_SCHEMA = "universal-problem-certificate/v6"
REGISTRY_SCHEMA = "universal-construction-registry/v6"
FRAGMENT_SCHEMA = "universal-construction-fragment/v6"
VALID_ROUTES = {"NONE", "UNI-PRESERVE", "UNI-ORDINARY", "UNI-CANONICAL", "UNI-OBSTRUCT"}
VALID_SELECTION_MODES = {"selectable", "support_only"}
VALID_BOUNDARY_DISPOSITIONS = {
    "preserved",
    "introduced",
    "changed",
    "repaired",
    "removed",
    "bypass-justified",
}
FACT_STATUSES = {"evidenced", "absent", "unknown"}
EVIDENCE_REF = re.compile(r"^(?P<scheme>[a-z][a-z0-9_-]*):(?P<locator>\S+)$")


class ContractError(ValueError):
    """Raised when a registry or problem violates its public contract."""


@dataclass(frozen=True)
class CandidateEvaluation:
    card: Mapping[str, Any]
    matched_signals: tuple[Mapping[str, Any], ...]
    prerequisite_states: tuple[Mapping[str, Any], ...]
    witnesses: tuple[Mapping[str, Any], ...]
    proofs: Mapping[str, Mapping[str, Any]]
    missing_proof_obligations: tuple[str, ...]
    rejection: Mapping[str, Any] | None
    covered_requirement_ids: tuple[str, ...]
    missing_requirement_ids: tuple[str, ...]
    incompatible_reasons: tuple[str, ...]

    @property
    def support_only(self) -> bool:
        return self.card["selection_mode"] == "support_only"

    @property
    def contradicted(self) -> bool:
        return any(state["state"] == "absent" for state in self.prerequisite_states)

    @property
    def epistemically_blocked(self) -> bool:
        return any(
            state["state"] in {"missing", "unknown"}
            for state in self.prerequisite_states
        )

    @property
    def proof_complete(self) -> bool:
        return not self.missing_proof_obligations

    @property
    def witness_complete(self) -> bool:
        return not self.missing_requirement_ids

    @property
    def explicitly_rejected(self) -> bool:
        return self.rejection is not None

    @property
    def eligible(self) -> bool:
        return (
            not self.support_only
            and not self.incompatible_reasons
            and bool(self.matched_signals)
            and not self.explicitly_rejected
            and all(state["state"] == "satisfied" for state in self.prerequisite_states)
            and self.witness_complete
            and self.proof_complete
        )

    @property
    def resolved_against_nomination(self) -> bool:
        return self.explicitly_rejected or self.contradicted

    @property
    def obstruction(self) -> bool:
        return (
            self.card["route"] == "UNI-OBSTRUCT"
            or self.card["proof_profile"] == "obstruction"
        )

    @property
    def unresolved(self) -> bool:
        return (
            not self.support_only
            and bool(self.matched_signals)
            and not self.incompatible_reasons
            and not self.eligible
            and not self.resolved_against_nomination
        )


def _default_registry_path() -> Path:
    return (
        Path(__file__).resolve().parents[1]
        / "references"
        / "universal-construction-registry.yaml"
    )


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ContractError(f"invalid YAML in {path}: {exc}") from exc


def _string_list(value: Any, *, field: str, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ContractError(f"{field} must be a string list")
    if not allow_empty and not value:
        raise ContractError(f"{field} must not be empty")
    if len(value) != len(set(value)):
        raise ContractError(f"{field} must not contain duplicates")
    return list(value)


def load_registry(path: Path) -> dict[str, Any]:
    raw = _load_yaml(path)
    if not isinstance(raw, dict):
        raise ContractError("registry must be a mapping")
    includes = raw.get("includes", [])
    if not isinstance(includes, list) or not all(
        isinstance(item, str) and item for item in includes
    ):
        raise ContractError("registry includes must be a string list")
    constructions: list[dict[str, Any]] = []
    for relative in includes:
        include_path = path.parent / relative
        fragment = _load_yaml(include_path)
        if not isinstance(fragment, dict) or fragment.get("schema") != FRAGMENT_SCHEMA:
            raise ContractError(
                f"registry include has unsupported schema: {include_path}"
            )
        cards = fragment.get("constructions")
        if not isinstance(cards, list):
            raise ContractError(
                f"registry include must contain constructions: {include_path}"
            )
        constructions.extend(cards)
    merged = dict(raw)
    merged["constructions"] = constructions
    validate_registry(merged, registry_root=path.parent)
    return merged


def validate_registry(
    registry: Mapping[str, Any], *, registry_root: Path | None = None
) -> None:
    if registry.get("schema") != REGISTRY_SCHEMA:
        raise ContractError(f"registry schema must be {REGISTRY_SCHEMA}")

    material = _string_list(
        registry.get("material_dimensions"), field="registry.material_dimensions"
    )
    hole_kinds = _string_list(registry.get("hole_kinds"), field="registry.hole_kinds")
    claim_modes = _string_list(
        registry.get("claim_modes"), field="registry.claim_modes"
    )
    claim_scopes = _string_list(
        registry.get("claim_scopes"), field="registry.claim_scopes"
    )
    axes = _string_list(registry.get("axes"), field="registry.axes")
    evidence_schemes = _string_list(
        registry.get("allowed_evidence_schemes"),
        field="registry.allowed_evidence_schemes",
    )
    moves = registry.get("moves")
    roles = registry.get("universal_roles")
    proof_profiles = registry.get("proof_profiles")
    scope_obligations = registry.get("scope_obligations")
    rejection_bases = registry.get("rejection_bases")
    derived_mechanics = registry.get("derived_mechanics")
    packet_discipline = registry.get("packet_discipline")
    cards = registry.get("constructions")
    if not isinstance(moves, dict) or not moves:
        raise ContractError("registry.moves must be a non-empty mapping")
    if not isinstance(roles, dict) or not roles:
        raise ContractError("registry.universal_roles must be a non-empty mapping")
    if not isinstance(proof_profiles, dict) or not proof_profiles:
        raise ContractError("registry.proof_profiles must be a non-empty mapping")
    for profile, obligations in proof_profiles.items():
        if not isinstance(profile, str) or not profile:
            raise ContractError(
                "registry.proof_profiles keys must be non-empty strings"
            )
        _string_list(
            obligations,
            field=f"registry.proof_profiles.{profile}",
            allow_empty=profile == "support",
        )
    if not isinstance(scope_obligations, dict) or set(scope_obligations) != set(
        claim_scopes
    ):
        raise ContractError(
            "registry.scope_obligations must define every and only admitted claim scope"
        )
    all_obligations = {item for values in proof_profiles.values() for item in values}
    for scope, obligations in scope_obligations.items():
        values = _string_list(
            obligations,
            field=f"registry.scope_obligations.{scope}",
            allow_empty=True,
        )
        overlap = sorted(set(values).intersection(all_obligations))
        if overlap:
            raise ContractError(
                f"registry.scope_obligations.{scope} duplicates profile obligations: {', '.join(overlap)}"
            )
    _string_list(rejection_bases, field="registry.rejection_bases")
    if (
        not isinstance(packet_discipline, dict)
        or packet_discipline.get("one_axis_per_packet") is not True
    ):
        raise ContractError(
            "registry.packet_discipline must require one_axis_per_packet=true"
        )
    if not isinstance(cards, list) or not cards:
        raise ContractError("registry.constructions must be a non-empty list")

    seen_ids: set[str] = set()
    signal_owner: dict[str, str] = {}
    required_fields = {
        "id",
        "expert_name",
        "public_name",
        "route",
        "selection_mode",
        "diagnostic_order",
        "hole_kinds",
        "claim_modes",
        "claim_scopes",
        "axes",
        "proof_profile",
        "theory_refs",
        "guarantees",
        "moves",
        "signals",
        "requires",
        "emits",
        "laws",
        "falsifiers",
        "fallback",
        "universal",
    }
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            raise ContractError(f"construction {index} must be a mapping")
        missing = sorted(required_fields - card.keys())
        if missing:
            raise ContractError(
                f"construction {index} missing fields: {', '.join(missing)}"
            )
        card_id = card["id"]
        if not isinstance(card_id, str) or not card_id:
            raise ContractError(f"construction {index} has invalid id")
        if card_id in seen_ids:
            raise ContractError(f"duplicate construction id: {card_id}")
        seen_ids.add(card_id)
        if card["route"] not in VALID_ROUTES:
            raise ContractError(
                f"construction {card_id} has invalid route: {card['route']}"
            )
        if card["selection_mode"] not in VALID_SELECTION_MODES:
            raise ContractError(f"construction {card_id} has invalid selection_mode")
        if card["selection_mode"] == "support_only" and card["route"] != "NONE":
            raise ContractError(
                f"support-only construction {card_id} must use route NONE"
            )
        if card["selection_mode"] == "selectable" and card["route"] == "NONE":
            raise ContractError(f"selectable construction {card_id} must name a route")
        if not isinstance(card["diagnostic_order"], int):
            raise ContractError(
                f"construction {card_id} diagnostic_order must be an integer"
            )

        card_holes = _string_list(
            card["hole_kinds"], field=f"construction {card_id}.hole_kinds"
        )
        unknown_holes = sorted(set(card_holes) - set(hole_kinds))
        if unknown_holes:
            raise ContractError(
                f"construction {card_id} uses unknown hole kinds: {', '.join(unknown_holes)}"
            )
        card_modes = _string_list(
            card["claim_modes"], field=f"construction {card_id}.claim_modes"
        )
        unknown_modes = sorted(set(card_modes) - set(claim_modes))
        if unknown_modes:
            raise ContractError(
                f"construction {card_id} uses unknown claim modes: {', '.join(unknown_modes)}"
            )
        card_scopes = _string_list(
            card["claim_scopes"], field=f"construction {card_id}.claim_scopes"
        )
        unknown_scopes = sorted(set(card_scopes) - set(claim_scopes))
        if unknown_scopes:
            raise ContractError(
                f"construction {card_id} uses unknown claim scopes: {', '.join(unknown_scopes)}"
            )
        card_axes = _string_list(card["axes"], field=f"construction {card_id}.axes")
        unknown_axes = sorted(set(card_axes) - set(axes))
        if unknown_axes:
            raise ContractError(
                f"construction {card_id} uses unknown axes: {', '.join(unknown_axes)}"
            )
        proof_profile = card["proof_profile"]
        if proof_profile not in proof_profiles:
            raise ContractError(
                f"construction {card_id} uses unknown proof profile: {proof_profile}"
            )
        if card["selection_mode"] == "support_only" and proof_profile != "support":
            raise ContractError(
                f"support-only construction {card_id} must use support proof profile"
            )
        if card["selection_mode"] == "selectable" and proof_profile == "support":
            raise ContractError(
                f"selectable construction {card_id} cannot use support proof profile"
            )
        if card["route"] == "UNI-OBSTRUCT" and proof_profile != "obstruction":
            raise ContractError(
                f"obstruction construction {card_id} must use obstruction proof profile"
            )
        if card["route"] != "UNI-OBSTRUCT" and proof_profile == "obstruction":
            raise ContractError(
                f"non-obstruction construction {card_id} cannot use obstruction proof profile"
            )

        guarantees = _string_list(
            card["guarantees"],
            field=f"construction {card_id}.guarantees",
            allow_empty=True,
        )
        unknown_dimensions = sorted(set(guarantees) - set(material))
        if unknown_dimensions:
            raise ContractError(
                f"construction {card_id} uses unknown guarantee dimensions: {', '.join(unknown_dimensions)}"
            )
        if card["selection_mode"] == "support_only" and guarantees:
            raise ContractError(
                f"support-only construction {card_id} cannot guarantee material delta"
            )

        for field in (
            "moves",
            "signals",
            "requires",
            "emits",
            "laws",
            "falsifiers",
            "theory_refs",
        ):
            values = _string_list(
                card[field],
                field=f"construction {card_id}.{field}",
                allow_empty=field == "requires",
            )
            if field == "signals":
                for signal in values:
                    previous = signal_owner.get(signal)
                    if previous is not None:
                        raise ContractError(
                            f"signal {signal} is owned by both {previous} and {card_id}; v6 signals must be unambiguous"
                        )
                    signal_owner[signal] = card_id
        unknown_moves = sorted(set(card["moves"]) - set(moves))
        if unknown_moves:
            raise ContractError(
                f"construction {card_id} uses unknown moves: {', '.join(unknown_moves)}"
            )
        if not isinstance(card["fallback"], str) or not card["fallback"].strip():
            raise ContractError(f"construction {card_id}.fallback must be non-empty")
        universal = card["universal"]
        if not isinstance(universal, dict):
            raise ContractError(f"construction {card_id}.universal must be a mapping")
        for field in ("role", "competitors", "mediator", "canonicality", "effectivity"):
            if (
                not isinstance(universal.get(field), str)
                or not universal[field].strip()
            ):
                raise ContractError(
                    f"construction {card_id}.universal.{field} must be non-empty"
                )
        if universal["role"] not in roles:
            raise ContractError(
                f"construction {card_id} uses unknown universal role: {universal['role']}"
            )

        if registry_root is not None:
            root = registry_root.resolve()
            for reference in card["theory_refs"]:
                candidate = (root / reference).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError as exc:
                    raise ContractError(
                        f"construction {card_id} theory reference escapes registry root: {reference}"
                    ) from exc
                if not candidate.is_file():
                    raise ContractError(
                        f"construction {card_id} theory reference does not exist: {reference}"
                    )

    if not isinstance(derived_mechanics, dict) or not derived_mechanics:
        raise ContractError("registry.derived_mechanics must be a non-empty mapping")
    for mechanic_id, mechanic in derived_mechanics.items():
        if not isinstance(mechanic_id, str) or not mechanic_id:
            raise ContractError("registry.derived_mechanics keys must be non-empty strings")
        if not isinstance(mechanic, dict) or set(mechanic) != {"packet_axes", "card_composition", "rule"}:
            raise ContractError(
                f"registry.derived_mechanics.{mechanic_id} must contain exactly packet_axes, card_composition, and rule"
            )
        mechanic_axes = _string_list(
            mechanic["packet_axes"],
            field=f"registry.derived_mechanics.{mechanic_id}.packet_axes",
        )
        unknown_mechanic_axes = sorted(set(mechanic_axes) - set(axes))
        if unknown_mechanic_axes:
            raise ContractError(
                f"registry.derived_mechanics.{mechanic_id} uses unknown axes: {', '.join(unknown_mechanic_axes)}"
            )
        mechanic_cards = _string_list(
            mechanic["card_composition"],
            field=f"registry.derived_mechanics.{mechanic_id}.card_composition",
            allow_empty=True,
        )
        unknown_mechanic_cards = sorted(set(mechanic_cards) - seen_ids)
        if unknown_mechanic_cards:
            raise ContractError(
                f"registry.derived_mechanics.{mechanic_id} references unknown cards: {', '.join(unknown_mechanic_cards)}"
            )
        if not isinstance(mechanic["rule"], str) or not mechanic["rule"].strip():
            raise ContractError(f"registry.derived_mechanics.{mechanic_id}.rule must be non-empty")

    if len(evidence_schemes) != len(set(evidence_schemes)):
        raise ContractError("registry.allowed_evidence_schemes contains duplicates")


def load_problem(path: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"problem not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid problem JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ContractError("problem must be a JSON object")
    validate_problem(raw, registry)
    return raw


def _validate_evidence_refs(
    refs: Any,
    registry: Mapping[str, Any],
    *,
    field: str,
    allow_empty: bool = False,
) -> list[str]:
    values = _string_list(refs, field=field, allow_empty=allow_empty)
    allowed = set(registry["allowed_evidence_schemes"])
    for ref in values:
        match = EVIDENCE_REF.match(ref)
        if not match:
            raise ContractError(f"{field} contains malformed evidence reference: {ref}")
        if match.group("scheme") not in allowed:
            raise ContractError(
                f"{field} uses unsupported evidence scheme: {match.group('scheme')}"
            )
    return values


def _validate_claim(
    value: Any, registry: Mapping[str, Any], *, field: str
) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be an attributed claim object")
    if set(value) != {"claim", "evidence"}:
        raise ContractError(f"{field} must contain exactly claim and evidence")
    if not isinstance(value["claim"], str) or not value["claim"].strip():
        raise ContractError(f"{field}.claim must be non-empty")
    _validate_evidence_refs(value["evidence"], registry, field=f"{field}.evidence")
    return value


def _validate_claim_list(
    value: Any, registry: Mapping[str, Any], *, field: str
) -> None:
    if not isinstance(value, list) or not value:
        raise ContractError(f"{field} must be a non-empty attributed-claim list")
    for index, item in enumerate(value):
        _validate_claim(item, registry, field=f"{field}[{index}]")


def _validate_fact(key: str, fact: Any, registry: Mapping[str, Any]) -> None:
    if not isinstance(fact, dict):
        raise ContractError(f"facts.{key} must be an object")
    status = fact.get("status")
    satisfied = fact.get("satisfied", "__missing__")
    if status not in FACT_STATUSES:
        raise ContractError(f"facts.{key}.status must be evidenced, absent, or unknown")
    if status == "evidenced":
        if satisfied is not True:
            raise ContractError(f"facts.{key}: evidenced requires satisfied=true")
        _validate_evidence_refs(
            fact.get("evidence"), registry, field=f"facts.{key}.evidence"
        )
    elif status == "absent":
        if satisfied is not False:
            raise ContractError(f"facts.{key}: absent requires satisfied=false")
        _validate_evidence_refs(
            fact.get("evidence"), registry, field=f"facts.{key}.evidence"
        )
    else:
        if satisfied is not None:
            raise ContractError(f"facts.{key}: unknown requires satisfied=null")
        if not isinstance(fact.get("reason"), str) or not fact["reason"].strip():
            raise ContractError(f"facts.{key}: unknown requires a reason")
        _validate_evidence_refs(
            fact.get("evidence", []),
            registry,
            field=f"facts.{key}.evidence",
            allow_empty=True,
        )
    allowed = {"status", "satisfied", "value", "evidence", "reason"}
    extras = sorted(set(fact) - allowed)
    if extras:
        raise ContractError(f"facts.{key} has unknown fields: {', '.join(extras)}")


def _card_maps(
    registry: Mapping[str, Any],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    cards = {card["id"]: card for card in registry["constructions"]}
    signals: dict[str, Mapping[str, Any]] = {}
    for card in registry["constructions"]:
        for signal in card["signals"]:
            signals[signal] = card
    return cards, signals


def _card_compatible(card: Mapping[str, Any], problem: Mapping[str, Any]) -> bool:
    return (
        problem["hole"]["axis"] in card["axes"]
        and problem["hole"]["kind"] in card["hole_kinds"]
        and problem["claim_mode"] in card["claim_modes"]
        and problem["claim_scope"] in card["claim_scopes"]
    )


def _validate_card_target(
    card_id: str,
    *,
    problem: Mapping[str, Any],
    cards: Mapping[str, Mapping[str, Any]],
    signal_ids: set[str],
    field: str,
) -> Mapping[str, Any]:
    card = cards.get(card_id)
    if card is None:
        raise ContractError(f"{field} references unknown card: {card_id}")
    if card["selection_mode"] != "selectable":
        raise ContractError(f"{field} cannot target support-only card: {card_id}")
    if not _card_compatible(card, problem):
        raise ContractError(
            f"{field}.{card_id} is incompatible with axis {problem['hole']['axis']}, "
            f"hole kind {problem['hole']['kind']}, claim mode {problem['claim_mode']}, "
            f"or claim scope {problem['claim_scope']}"
        )
    if not set(card["signals"]).intersection(signal_ids):
        raise ContractError(f"{field}.{card_id} lacks a matching attributed signal")
    return card


def validate_problem(problem: Mapping[str, Any], registry: Mapping[str, Any]) -> None:
    if problem.get("schema") != PROBLEM_SCHEMA:
        raise ContractError(f"problem schema must be {PROBLEM_SCHEMA}")
    allowed_top = {
        "schema",
        "claim_mode",
        "claim_scope",
        "boundary_disposition",
        "disposition_rationale",
        "verification_target",
        "seam",
        "owner",
        "hole",
        "comparison_universe",
        "signals",
        "facts",
        "ordinary_candidate",
        "candidate_witnesses",
        "candidate_proofs",
        "candidate_rejections",
    }
    extras = sorted(set(problem) - allowed_top)
    if extras:
        raise ContractError(f"problem has unknown fields: {', '.join(extras)}")
    missing = sorted(allowed_top - set(problem))
    if missing:
        raise ContractError(f"problem is missing fields: {', '.join(missing)}")

    if problem["claim_mode"] not in registry["claim_modes"]:
        raise ContractError("problem.claim_mode is not admitted by the registry")
    if problem["claim_scope"] not in registry["claim_scopes"]:
        raise ContractError("problem.claim_scope is not admitted by the registry")
    if problem["boundary_disposition"] not in VALID_BOUNDARY_DISPOSITIONS:
        raise ContractError("problem.boundary_disposition is not admitted")
    _validate_claim(
        problem["disposition_rationale"],
        registry,
        field="problem.disposition_rationale",
    )
    verification_target = problem["verification_target"]
    if problem["claim_mode"] == "nomination":
        if verification_target is not None:
            raise ContractError(
                "problem.verification_target must be null in nomination mode"
            )
    else:
        if not isinstance(verification_target, str) or not verification_target.strip():
            raise ContractError(
                "problem.verification_target must name one selectable card in verification mode"
            )
    _validate_claim(problem["seam"], registry, field="problem.seam")
    _validate_claim(problem["owner"], registry, field="problem.owner")

    hole = problem["hole"]
    if not isinstance(hole, dict) or set(hole) != {
        "axis",
        "kind",
        "claim",
        "requirements",
    }:
        raise ContractError(
            "problem.hole must contain exactly axis, kind, claim, and requirements"
        )
    if hole["axis"] not in registry["axes"]:
        raise ContractError("problem.hole.axis is not admitted by the registry")
    if hole["kind"] not in registry["hole_kinds"]:
        raise ContractError("problem.hole.kind is not admitted by the registry")
    _validate_claim(hole["claim"], registry, field="problem.hole.claim")
    requirements = hole["requirements"]
    if not isinstance(requirements, list) or not requirements:
        raise ContractError("problem.hole.requirements must be non-empty")
    requirement_ids: set[str] = set()
    for index, requirement in enumerate(requirements):
        field = f"problem.hole.requirements[{index}]"
        if not isinstance(requirement, dict) or set(requirement) != {
            "id",
            "dimension",
            "claim",
            "evidence",
        }:
            raise ContractError(
                f"{field} must contain exactly id, dimension, claim, and evidence"
            )
        req_id = requirement["id"]
        if not isinstance(req_id, str) or not req_id.strip():
            raise ContractError(f"{field}.id must be non-empty")
        if req_id in requirement_ids:
            raise ContractError(f"duplicate requirement id: {req_id}")
        requirement_ids.add(req_id)
        if requirement["dimension"] not in registry["material_dimensions"]:
            raise ContractError(f"{field}.dimension is not admitted by the registry")
        if (
            not isinstance(requirement["claim"], str)
            or not requirement["claim"].strip()
        ):
            raise ContractError(f"{field}.claim must be non-empty")
        _validate_evidence_refs(
            requirement["evidence"], registry, field=f"{field}.evidence"
        )

    universe = problem["comparison_universe"]
    required_universe = {
        "objects",
        "transformations",
        "observations",
        "equivalence",
        "effects",
        "authority",
        "resources",
    }
    if not isinstance(universe, dict) or set(universe) != required_universe:
        raise ContractError(
            "problem.comparison_universe must contain exactly objects, transformations, observations, "
            "equivalence, effects, authority, and resources"
        )
    for key in sorted(required_universe):
        _validate_claim_list(
            universe[key], registry, field=f"problem.comparison_universe.{key}"
        )

    cards, signal_map = _card_maps(registry)
    signals = problem["signals"]
    if not isinstance(signals, list):
        raise ContractError("problem.signals must be a list")
    signal_ids: set[str] = set()
    matched_card_ids: set[str] = set()
    for index, signal in enumerate(signals):
        field = f"problem.signals[{index}]"
        if not isinstance(signal, dict) or set(signal) != {"id", "claim", "evidence"}:
            raise ContractError(f"{field} must contain exactly id, claim, and evidence")
        signal_id = signal["id"]
        if not isinstance(signal_id, str) or not signal_id.strip():
            raise ContractError(f"{field}.id must be non-empty")
        if signal_id in signal_ids:
            raise ContractError(f"duplicate signal id: {signal_id}")
        signal_ids.add(signal_id)
        if not isinstance(signal["claim"], str) or not signal["claim"].strip():
            raise ContractError(f"{field}.claim must be non-empty")
        _validate_evidence_refs(signal["evidence"], registry, field=f"{field}.evidence")
        card = signal_map.get(signal_id)
        if card is None:
            raise ContractError(
                f"{field}.id is not known by the theorem registry: {signal_id}"
            )
        if not _card_compatible(card, problem):
            raise ContractError(
                f"{field}.id belongs outside this packet's axis/hole/claim contract; "
                "compile it as a separate linked Universal Problem packet"
            )
        matched_card_ids.add(card["id"])

    if problem["claim_mode"] == "verification":
        _validate_card_target(
            problem["verification_target"],
            problem=problem,
            cards=cards,
            signal_ids=signal_ids,
            field="verification_target",
        )

    known_facts = {
        fact for card in registry["constructions"] for fact in card["requires"]
    }
    allowed_facts = {
        fact for card_id in matched_card_ids for fact in cards[card_id]["requires"]
    }
    facts = problem["facts"]
    if not isinstance(facts, dict):
        raise ContractError("problem.facts must be an object")
    for key, fact in facts.items():
        if not isinstance(key, str) or not key:
            raise ContractError("problem fact keys must be non-empty strings")
        if key not in known_facts:
            raise ContractError(
                f"problem.facts contains unknown prerequisite key: {key}"
            )
        if key not in allowed_facts:
            raise ContractError(
                f"problem.facts.{key} is unrelated to this packet's attributed signals; "
                "move it to the packet that owns that theorem card"
            )
        _validate_fact(key, fact, registry)

    ordinary = problem["ordinary_candidate"]
    expected_ordinary = {
        "artifact",
        "law",
        "falsifier",
        "resource_impact",
        "guarantees",
    }
    if not isinstance(ordinary, dict) or set(ordinary) != expected_ordinary:
        raise ContractError(
            "ordinary_candidate must contain exactly artifact, law, falsifier, resource_impact, and guarantees"
        )
    if not isinstance(ordinary["artifact"], str) or not ordinary["artifact"].strip():
        raise ContractError("ordinary_candidate.artifact must be non-empty")
    _validate_claim(ordinary["law"], registry, field="ordinary_candidate.law")
    _validate_claim(
        ordinary["falsifier"], registry, field="ordinary_candidate.falsifier"
    )
    _validate_claim(
        ordinary["resource_impact"],
        registry,
        field="ordinary_candidate.resource_impact",
    )
    guarantees = ordinary["guarantees"]
    if not isinstance(guarantees, list):
        raise ContractError("ordinary_candidate.guarantees must be a list")
    ordinary_ids: set[str] = set()
    for index, guarantee in enumerate(guarantees):
        field = f"ordinary_candidate.guarantees[{index}]"
        if not isinstance(guarantee, dict) or set(guarantee) != {
            "requirement_id",
            "claim",
            "evidence",
        }:
            raise ContractError(
                f"{field} must contain exactly requirement_id, claim, and evidence"
            )
        req_id = guarantee["requirement_id"]
        if req_id not in requirement_ids:
            raise ContractError(f"{field} references unknown requirement: {req_id}")
        if req_id in ordinary_ids:
            raise ContractError(
                f"ordinary candidate duplicates requirement guarantee: {req_id}"
            )
        ordinary_ids.add(req_id)
        if not isinstance(guarantee["claim"], str) or not guarantee["claim"].strip():
            raise ContractError(f"{field}.claim must be non-empty")
        _validate_evidence_refs(
            guarantee["evidence"], registry, field=f"{field}.evidence"
        )

    candidate_witnesses = problem["candidate_witnesses"]
    candidate_proofs = problem["candidate_proofs"]
    candidate_rejections = problem["candidate_rejections"]
    if not isinstance(candidate_witnesses, dict):
        raise ContractError("problem.candidate_witnesses must be an object")
    if not isinstance(candidate_proofs, dict):
        raise ContractError("problem.candidate_proofs must be an object")
    if not isinstance(candidate_rejections, dict):
        raise ContractError("problem.candidate_rejections must be an object")

    requirement_by_id = {item["id"]: item for item in requirements}
    for card_id, card_witnesses in candidate_witnesses.items():
        card = _validate_card_target(
            card_id,
            problem=problem,
            cards=cards,
            signal_ids=signal_ids,
            field="candidate_witnesses",
        )
        if not isinstance(card_witnesses, list):
            raise ContractError(f"candidate_witnesses.{card_id} must be a list")
        seen_witness_ids: set[str] = set()
        for index, witness in enumerate(card_witnesses):
            field = f"candidate_witnesses.{card_id}[{index}]"
            required = {
                "requirement_id",
                "dimension",
                "claim_mode",
                "claim_scope",
                "claim",
                "evidence",
            }
            if not isinstance(witness, dict) or set(witness) != required:
                raise ContractError(
                    f"{field} must contain exactly {', '.join(sorted(required))}"
                )
            req_id = witness["requirement_id"]
            if req_id not in requirement_by_id:
                raise ContractError(f"{field} references unknown requirement: {req_id}")
            if req_id in ordinary_ids:
                raise ContractError(
                    f"{field} targets a requirement already guaranteed by the ordinary candidate"
                )
            if req_id in seen_witness_ids:
                raise ContractError(
                    f"{field} duplicates a candidate witness for requirement: {req_id}"
                )
            seen_witness_ids.add(req_id)
            requirement = requirement_by_id[req_id]
            if witness["dimension"] != requirement["dimension"]:
                raise ContractError(
                    f"{field}.dimension must equal the targeted requirement dimension"
                )
            if witness["dimension"] not in card["guarantees"]:
                raise ContractError(
                    f"{field}.dimension is not guaranteed by card {card_id}"
                )
            if witness["claim_mode"] != problem["claim_mode"]:
                raise ContractError(
                    f"{field}.claim_mode does not match the problem claim mode"
                )
            if witness["claim_scope"] != problem["claim_scope"]:
                raise ContractError(
                    f"{field}.claim_scope does not match the problem claim scope"
                )
            if not isinstance(witness["claim"], str) or not witness["claim"].strip():
                raise ContractError(f"{field}.claim must be non-empty")
            _validate_evidence_refs(
                witness["evidence"], registry, field=f"{field}.evidence"
            )

    proof_profiles = registry["proof_profiles"]
    for card_id, proof_packet in candidate_proofs.items():
        card = _validate_card_target(
            card_id,
            problem=problem,
            cards=cards,
            signal_ids=signal_ids,
            field="candidate_proofs",
        )
        if not isinstance(proof_packet, dict):
            raise ContractError(f"candidate_proofs.{card_id} must be an object")
        admitted = set(proof_profiles[card["proof_profile"]])
        admitted.update(registry["scope_obligations"][problem["claim_scope"]])
        extras = sorted(set(proof_packet) - admitted)
        if extras:
            raise ContractError(
                f"candidate_proofs.{card_id} contains unknown obligations: {', '.join(extras)}"
            )
        for obligation, proof_claim in proof_packet.items():
            _validate_claim(
                proof_claim,
                registry,
                field=f"candidate_proofs.{card_id}.{obligation}",
            )

    for card_id, rejection in candidate_rejections.items():
        _validate_card_target(
            card_id,
            problem=problem,
            cards=cards,
            signal_ids=signal_ids,
            field="candidate_rejections",
        )
        if (
            problem["claim_mode"] == "verification"
            and card_id == problem["verification_target"]
        ):
            raise ContractError("verification_target cannot be explicitly rejected")
        if not isinstance(rejection, dict) or set(rejection) != {
            "basis",
            "claim",
            "evidence",
        }:
            raise ContractError(
                f"candidate_rejections.{card_id} must contain exactly basis, claim, and evidence"
            )
        if rejection["basis"] not in registry["rejection_bases"]:
            raise ContractError(
                f"candidate_rejections.{card_id}.basis is not admitted by the registry"
            )
        if not isinstance(rejection["claim"], str) or not rejection["claim"].strip():
            raise ContractError(
                f"candidate_rejections.{card_id}.claim must be non-empty"
            )
        _validate_evidence_refs(
            rejection["evidence"],
            registry,
            field=f"candidate_rejections.{card_id}.evidence",
        )
        if candidate_witnesses.get(card_id):
            raise ContractError(
                f"candidate_rejections.{card_id} cannot coexist with candidate witnesses"
            )
        if candidate_proofs.get(card_id):
            raise ContractError(
                f"candidate_rejections.{card_id} cannot coexist with candidate proofs"
            )


def _fact_state(facts: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    fact = facts.get(key)
    if fact is None:
        return {"fact": key, "state": "missing", "reason": "no fact packet supplied"}
    status = fact["status"]
    if status == "evidenced":
        return {
            "fact": key,
            "state": "satisfied",
            "evidence": list(fact["evidence"]),
            "value": fact.get("value"),
        }
    if status == "absent":
        return {
            "fact": key,
            "state": "absent",
            "evidence": list(fact["evidence"]),
            "value": fact.get("value"),
        }
    return {
        "fact": key,
        "state": "unknown",
        "reason": fact["reason"],
        "evidence": list(fact.get("evidence", [])),
    }


def evaluate_candidates(
    problem: Mapping[str, Any], registry: Mapping[str, Any]
) -> list[CandidateEvaluation]:
    signals_by_id = {signal["id"]: signal for signal in problem["signals"]}
    facts = problem["facts"]
    requirement_ids = [item["id"] for item in problem["hole"]["requirements"]]
    ordinary_ids = {
        item["requirement_id"] for item in problem["ordinary_candidate"]["guarantees"]
    }
    unmet = tuple(req_id for req_id in requirement_ids if req_id not in ordinary_ids)
    witness_map = problem["candidate_witnesses"]
    proof_map = problem["candidate_proofs"]
    rejection_map = problem["candidate_rejections"]

    evaluations: list[CandidateEvaluation] = []
    for card in registry["constructions"]:
        matched = tuple(
            signals_by_id[signal]
            for signal in card["signals"]
            if signal in signals_by_id
        )
        prerequisites = tuple(_fact_state(facts, key) for key in card["requires"])
        witnesses = tuple(witness_map.get(card["id"], []))
        proofs = dict(proof_map.get(card["id"], {}))
        proof_obligations = tuple(
            [
                *registry["proof_profiles"][card["proof_profile"]],
                *registry["scope_obligations"][problem["claim_scope"]],
            ]
        )
        missing_proofs = tuple(
            obligation for obligation in proof_obligations if obligation not in proofs
        )
        covered = tuple(
            item["requirement_id"]
            for item in witnesses
            if item["requirement_id"] in unmet
        )
        missing_requirements = tuple(
            req_id for req_id in unmet if req_id not in covered
        )
        incompatible: list[str] = []
        if problem["hole"]["axis"] not in card["axes"]:
            incompatible.append(f"axis {problem['hole']['axis']} is not supported")
        if problem["hole"]["kind"] not in card["hole_kinds"]:
            incompatible.append(f"hole kind {problem['hole']['kind']} is not supported")
        if problem["claim_mode"] not in card["claim_modes"]:
            incompatible.append(f"claim mode {problem['claim_mode']} is not supported")
        if problem["claim_scope"] not in card["claim_scopes"]:
            incompatible.append(
                f"claim scope {problem['claim_scope']} is not supported"
            )
        evaluations.append(
            CandidateEvaluation(
                card=card,
                matched_signals=matched,
                prerequisite_states=prerequisites,
                witnesses=witnesses,
                proofs=proofs,
                missing_proof_obligations=missing_proofs,
                rejection=rejection_map.get(card["id"]),
                covered_requirement_ids=covered,
                missing_requirement_ids=missing_requirements,
                incompatible_reasons=tuple(incompatible),
            )
        )
    return sorted(
        evaluations,
        key=lambda item: (int(item.card["diagnostic_order"]), str(item.card["id"])),
    )


def _material_delta(
    problem: Mapping[str, Any], nominee: CandidateEvaluation | None
) -> Mapping[str, Any]:
    if nominee is None:
        return {}
    requirement_by_id = {item["id"]: item for item in problem["hole"]["requirements"]}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for witness in nominee.witnesses:
        requirement = requirement_by_id[witness["requirement_id"]]
        grouped.setdefault(requirement["dimension"], []).append(
            {
                "requirement_id": requirement["id"],
                "requirement": requirement["claim"],
                "candidate_claim": witness["claim"],
                "evidence": list(witness["evidence"]),
            }
        )
    return grouped


def _candidate_record(
    candidate: CandidateEvaluation, *, explain_theory: bool
) -> dict[str, Any]:
    card = candidate.card
    if candidate.explicitly_rejected:
        resolution = "rejected"
    elif candidate.contradicted:
        resolution = "contradicted"
    elif candidate.eligible:
        resolution = "eligible"
    elif candidate.epistemically_blocked:
        resolution = "epistemically-blocked"
    elif candidate.missing_requirement_ids:
        resolution = "witness-incomplete"
    elif candidate.missing_proof_obligations:
        resolution = "proof-incomplete"
    else:
        resolution = "ineligible"
    record: dict[str, Any] = {
        "construction_key": card["id"],
        "plain_construction": card["public_name"],
        "selection_mode": card["selection_mode"],
        "route": card["route"],
        "axes": list(card["axes"]),
        "proof_profile": card["proof_profile"],
        "matched_signals": [dict(signal) for signal in candidate.matched_signals],
        "prerequisites": [dict(state) for state in candidate.prerequisite_states],
        "covered_requirement_ids": list(candidate.covered_requirement_ids),
        "missing_requirement_ids": list(candidate.missing_requirement_ids),
        "submitted_proofs": {
            key: dict(value) for key, value in candidate.proofs.items()
        },
        "missing_proof_obligations": list(candidate.missing_proof_obligations),
        "rejection": dict(candidate.rejection) if candidate.rejection else None,
        "incompatible_reasons": list(candidate.incompatible_reasons),
        "resolution": resolution,
        "eligible": candidate.eligible,
        "emits": list(card["emits"]),
        "fallback": card["fallback"],
    }
    if explain_theory:
        record.update(
            {
                "expert_name": card["expert_name"],
                "moves": list(card["moves"]),
                "universal": dict(card["universal"]),
                "theory_refs": list(card["theory_refs"]),
                "theorem_laws": list(card["laws"]),
                "theorem_falsifiers": list(card["falsifiers"]),
            }
        )
    return record


def _ordinary_route(disposition: str) -> str:
    if disposition == "preserved":
        return "UNI-PRESERVE"
    if disposition == "bypass-justified":
        return "UNI-OBSTRUCT"
    return "UNI-ORDINARY"


def _nomination(
    *,
    status: str,
    reason: str,
    route: str | None = None,
    artifact: str | None = None,
    candidate: CandidateEvaluation | None = None,
    candidates: Sequence[CandidateEvaluation] = (),
    explain_theory: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": status,
        "route_nomination": route,
        "selected_artifact": artifact,
        "advanced_mechanics": "none",
        "reason": reason,
    }
    if candidate is not None:
        result["construction_key"] = candidate.card["id"]
        if candidate.card["route"] == "UNI-CANONICAL":
            result["advanced_mechanics"] = candidate.card["id"]
        if explain_theory:
            result["expert_name"] = candidate.card["expert_name"]
    if candidates:
        result["candidate_keys"] = [item.card["id"] for item in candidates]
    return result


def compile_problem(
    problem: Mapping[str, Any],
    registry: Mapping[str, Any],
    *,
    explain_theory: bool = False,
) -> dict[str, Any]:
    validate_problem(problem, registry)
    evaluations = evaluate_candidates(problem, registry)
    requirements = problem["hole"]["requirements"]
    ordinary_ids = {
        item["requirement_id"] for item in problem["ordinary_candidate"]["guarantees"]
    }
    unmet = [item for item in requirements if item["id"] not in ordinary_ids]
    support = [
        item
        for item in evaluations
        if item.support_only and item.matched_signals and not item.incompatible_reasons
    ]
    relevant = [
        item
        for item in evaluations
        if not item.support_only
        and item.matched_signals
        and not item.incompatible_reasons
    ]
    obstructive = [item for item in relevant if item.obstruction]
    constructive = [item for item in relevant if not item.obstruction]

    nominee: CandidateEvaluation | None = None
    nomination: dict[str, Any]

    if problem["claim_mode"] == "verification":
        target = next(
            item
            for item in evaluations
            if item.card["id"] == problem["verification_target"]
        )
        active_obstructions = [
            item
            for item in obstructive
            if item.card["id"] != target.card["id"]
            and not item.resolved_against_nomination
        ]
        active_alternatives = [
            item
            for item in relevant
            if item.card["id"] != target.card["id"]
            and not item.resolved_against_nomination
        ]
        if not unmet:
            nomination = _nomination(
                status="verification-ordinary-sufficient",
                artifact=problem["ordinary_candidate"]["artifact"],
                reason=(
                    "The ordinary candidate already guarantees every requirement, so the target theorem card "
                    "has no evidenced material requirement to verify."
                ),
            )
        elif target.obstruction:
            if target.eligible and active_alternatives:
                nomination = _nomination(
                    status="verification-alternative-unresolved",
                    candidates=[target, *active_alternatives],
                    reason=(
                        "The target obstruction is complete, but another constructive or obstruction alternative "
                        "remains active. Verification cannot silently dismiss it."
                    ),
                )
            elif target.eligible:
                nominee = target
                nomination = _nomination(
                    status="verified",
                    artifact=target.card["public_name"],
                    candidate=target,
                    explain_theory=explain_theory,
                    reason=(
                        "The named obstruction target satisfies its exact requirement witnesses and complete "
                        "obstruction proof profile, with every alternative resolved."
                    ),
                )
                nomination["verified_route"] = target.card["route"]
            else:
                nomination = _nomination(
                    status="verification-failed",
                    candidates=[target],
                    reason=(
                        "The named obstruction target is contradicted, epistemically blocked, witness-incomplete, "
                        "or proof-incomplete."
                    ),
                )
        elif active_obstructions:
            nomination = _nomination(
                status="verification-conflict",
                candidates=[target, *active_obstructions],
                reason=(
                    "An active nonexistence or obstruction account conflicts with the constructive verification "
                    "target and must be resolved first."
                ),
            )
        elif target.eligible and active_alternatives:
            nomination = _nomination(
                status="verification-alternative-unresolved",
                candidates=[target, *active_alternatives],
                reason=(
                    "The target proof is complete, but another attributed alternative remains unresolved. "
                    "Verification cannot silently dismiss it."
                ),
            )
        elif target.eligible:
            nominee = target
            nomination = _nomination(
                status="verified",
                artifact=target.card["public_name"],
                candidate=target,
                explain_theory=explain_theory,
                reason=(
                    "The named verification target covers every unmet requirement, completes the required proof "
                    "profile, and every competing attributed alternative is contradicted or rejected with evidence."
                ),
            )
            nomination["verified_route"] = target.card["route"]
        else:
            nomination = _nomination(
                status="verification-failed",
                candidates=[target],
                reason=(
                    "The named verification target is contradicted, epistemically blocked, witness-incomplete, "
                    "proof-incomplete, or incompatible with the exact hole."
                ),
            )
    elif not unmet:
        route = _ordinary_route(problem["boundary_disposition"])
        status = (
            "ordinary-sufficient"
            if problem["boundary_disposition"] != "bypass-justified"
            else "bypass-justified"
        )
        nomination = _nomination(
            status=status,
            route=route,
            artifact=problem["ordinary_candidate"]["artifact"],
            reason=(
                "The ordinary candidate already guarantees every evidenced requirement; the route reflects "
                "the boundary disposition and its attributed rationale."
            ),
        )
    else:
        active_obstructions = [
            item for item in obstructive if not item.resolved_against_nomination
        ]
        eligible_obstructions = [item for item in active_obstructions if item.eligible]
        active_constructive = [
            item for item in constructive if not item.resolved_against_nomination
        ]
        eligible_constructive = [item for item in active_constructive if item.eligible]
        unresolved_constructive = [
            item for item in active_constructive if item.unresolved
        ]

        if active_obstructions:
            unresolved_obstructions = [item for item in active_obstructions if not item.eligible]
            if eligible_obstructions and (
                eligible_constructive or unresolved_constructive
            ):
                nomination = _nomination(
                    status="evidence-conflict",
                    candidates=[
                        *eligible_obstructions,
                        *eligible_constructive,
                        *unresolved_constructive,
                    ],
                    reason=(
                        "A nonexistence/obstruction claim and a constructive alternative are both active. "
                        "The root must resolve the contradictory evidence before any route can be nominated."
                    ),
                )
            elif len(eligible_obstructions) > 1:
                nomination = _nomination(
                    status="underdetermined-obstruction",
                    candidates=eligible_obstructions,
                    reason="Several complete obstruction accounts remain; no ranking may manufacture one.",
                )
            elif len(eligible_obstructions) == 1 and unresolved_obstructions:
                nomination = _nomination(
                    status="obstruction-alternative-unresolved",
                    candidates=[eligible_obstructions[0], *unresolved_obstructions],
                    reason=(
                        "One obstruction account is complete, but another attributed obstruction alternative remains "
                        "unresolved. Resolve, contradict, or reject it before nomination."
                    ),
                )
            elif len(eligible_obstructions) == 1:
                nominee = eligible_obstructions[0]
                nomination = _nomination(
                    status="nominated",
                    route=nominee.card["route"],
                    artifact=nominee.card["public_name"],
                    candidate=nominee,
                    explain_theory=explain_theory,
                    reason=(
                        "The witnessed obstruction covers the complete hole, includes the required counterexample "
                        "and reopening condition, and no constructive or obstruction alternative remains active."
                    ),
                )
            else:
                nomination = _nomination(
                    status="obstruction-unresolved",
                    candidates=active_obstructions,
                    reason=(
                        "An obstruction signal is active but its prerequisites, requirement witnesses, or proof "
                        "obligations are incomplete. Missing evidence is not itself an obstruction."
                    ),
                )
        elif len(eligible_constructive) > 1:
            nomination = _nomination(
                status="underdetermined",
                candidates=eligible_constructive,
                reason=(
                    "Several constructions satisfy the complete hole. Signal count, evidence count, and diagnostic "
                    "order may not manufacture a winner; reject alternatives with evidence or split the question."
                ),
            )
        elif len(eligible_constructive) == 1 and unresolved_constructive:
            nomination = _nomination(
                status="alternative-unresolved",
                candidates=[eligible_constructive[0], *unresolved_constructive],
                reason=(
                    "One construction is complete, but another attributed alternative remains unresolved. Supply "
                    "its evidence, contradict a prerequisite, or reject it with evidence before nomination."
                ),
            )
        elif len(eligible_constructive) == 1:
            nominee = eligible_constructive[0]
            nomination = _nomination(
                status="nominated",
                route=nominee.card["route"],
                artifact=nominee.card["public_name"],
                candidate=nominee,
                explain_theory=explain_theory,
                reason=(
                    "Exactly one construction covers every unmet requirement, completes its proof profile, and all "
                    "other attributed alternatives are contradicted or explicitly rejected."
                ),
            )
        elif unresolved_constructive:
            if any(item.epistemically_blocked for item in unresolved_constructive):
                status = "epistemically-blocked"
                reason = "A relevant construction lacks inspected prerequisite evidence. Evidence debt is not an obstruction."
            else:
                status = "evidence-incomplete"
                reason = "Relevant constructions lack exact requirement-level witnesses or evidence-bound proof obligations."
            nomination = _nomination(
                status=status, candidates=unresolved_constructive, reason=reason
            )
        elif relevant:
            nomination = _nomination(
                status="no-admissible-construction",
                candidates=relevant,
                reason=(
                    "Every attributed theorem-card alternative is contradicted or explicitly rejected, while exact "
                    "hole requirements remain unmet. Revise the requirements, classify another candidate, or provide "
                    "a witnessed obstruction; the ordinary candidate cannot be retained as though it were sufficient."
                ),
            )
        else:
            nomination = _nomination(
                status="unclassified-hole",
                reason=(
                    "The ordinary candidate leaves exact requirements unmet, but no compatible selectable theorem-card "
                    "signal classifies the hole. Add an attributed known signal or revise the packet; no route is nominated."
                ),
            )

    evidence_debt: list[dict[str, Any]] = []
    for candidate in relevant:
        for state in candidate.prerequisite_states:
            if state["state"] != "satisfied":
                evidence_debt.append(
                    {
                        "construction_key": candidate.card["id"],
                        "kind": "prerequisite",
                        "fact": state["fact"],
                        "state": state["state"],
                        "reason": state.get("reason"),
                    }
                )
        for requirement_id in candidate.missing_requirement_ids:
            evidence_debt.append(
                {
                    "construction_key": candidate.card["id"],
                    "kind": "candidate-witness",
                    "requirement_id": requirement_id,
                    "state": "missing",
                }
            )
        for obligation in candidate.missing_proof_obligations:
            evidence_debt.append(
                {
                    "construction_key": candidate.card["id"],
                    "kind": "proof-obligation",
                    "obligation": obligation,
                    "state": "missing",
                }
            )
        if candidate.unresolved:
            evidence_debt.append(
                {
                    "construction_key": candidate.card["id"],
                    "kind": "alternative-resolution",
                    "state": "unresolved",
                    "reason": "no evidence-bound rejection or contradicted prerequisite",
                }
            )

    if unmet and nominee is None:
        for requirement in unmet:
            evidence_debt.append(
                {
                    "kind": "unmet-hole-requirement",
                    "requirement_id": requirement["id"],
                    "dimension": requirement["dimension"],
                    "state": "unresolved",
                    "reason": nomination["status"],
                }
            )

    alternatives = {
        "considered": [item.card["id"] for item in relevant],
        "eligible": [item.card["id"] for item in relevant if item.eligible],
        "rejected": [
            {"construction_key": item.card["id"], "rejection": dict(item.rejection)}
            for item in relevant
            if item.rejection
        ],
        "contradicted": [item.card["id"] for item in relevant if item.contradicted],
        "unresolved": [item.card["id"] for item in relevant if item.unresolved],
    }
    selected_proof = (
        {key: dict(value) for key, value in nominee.proofs.items()} if nominee else {}
    )
    route_present = nomination.get("route_nomination") is not None

    return {
        "schema": CERTIFICATE_SCHEMA,
        "claim_mode": problem["claim_mode"],
        "claim_scope": problem["claim_scope"],
        "verification_target": problem["verification_target"],
        "boundary_disposition": problem["boundary_disposition"],
        "disposition_rationale": dict(problem["disposition_rationale"]),
        "seam": dict(problem["seam"]),
        "owner": dict(problem["owner"]),
        "hole": {
            "axis": problem["hole"]["axis"],
            "kind": problem["hole"]["kind"],
            "claim": dict(problem["hole"]["claim"]),
            "requirements": [dict(item) for item in requirements],
            "unmet_requirement_ids": [item["id"] for item in unmet],
        },
        "comparison_universe": {
            key: [dict(item) for item in claims]
            for key, claims in problem["comparison_universe"].items()
        },
        "ordinary_candidate": dict(problem["ordinary_candidate"]),
        "support_cards": [
            _candidate_record(item, explain_theory=explain_theory) for item in support
        ],
        "candidates": [
            _candidate_record(item, explain_theory=explain_theory) for item in relevant
        ],
        "alternatives": alternatives,
        "nomination": nomination,
        "selected_proof": selected_proof,
        "material_delta": _material_delta(problem, nominee),
        "evidence_debt": evidence_debt,
        "root_adjudication_required": True,
        "root_decision_evidence_ready": bool(
            problem["claim_mode"] == "nomination" and route_present
        ),
        "compiler_authority": "nomination-only",
        "decision_authority": "root-workflow",
        "theory_exposed": explain_theory,
    }


def _markdown_list(values: Iterable[Any]) -> str:
    items = list(values)
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def _render_claim_list(claims: Sequence[Mapping[str, Any]]) -> list[str]:
    return [
        f"- {item['claim']} — evidence: {', '.join(item['evidence'])}"
        for item in claims
    ]


def render_markdown(certificate: Mapping[str, Any]) -> str:
    nomination = certificate["nomination"]
    selected_proof = certificate["selected_proof"]
    proof_headings = [
        ("Existence / nonexistence", ("existence", "nonexistence")),
        ("Commutation / preservation", ("commutation",)),
        ("Competitor mediation", ("mediation",)),
        ("Canonicality / uniqueness-up-to", ("canonicality",)),
        ("Effective presentation", ("effectivity",)),
        ("Falsifier", ("falsifier",)),
        ("Counterexample", ("counterexample",)),
        ("Obstruction stability", ("stability",)),
        ("Reopening condition", ("reopening_condition",)),
        ("Approximation boundary", ("approximation_boundary",)),
        ("Refinement condition", ("refinement_condition",)),
    ]
    lines = [
        "# Universal Problem Nomination",
        "",
        "## Seam",
        f"- claim: {certificate['seam']['claim']}",
        f"- evidence: {', '.join(certificate['seam']['evidence'])}",
        "",
        "## Claim contract",
        f"- claim mode: {certificate['claim_mode']}",
        f"- claim scope: {certificate['claim_scope']}",
        f"- verification target: {certificate.get('verification_target') or 'none'}",
        "",
        "## Owner and boundary disposition",
        f"- owner: {certificate['owner']['claim']}",
        f"- owner evidence: {', '.join(certificate['owner']['evidence'])}",
        f"- disposition: {certificate['boundary_disposition']}",
        f"- disposition rationale: {certificate['disposition_rationale']['claim']}",
        f"- disposition evidence: {', '.join(certificate['disposition_rationale']['evidence'])}",
        "",
        "## Comparison universe",
    ]
    for key in (
        "objects",
        "transformations",
        "observations",
        "equivalence",
        "effects",
        "authority",
        "resources",
    ):
        lines.append(f"### {key.replace('_', ' ').title()}")
        lines.extend(_render_claim_list(certificate["comparison_universe"][key]))
    lines.extend(
        [
            "",
            "## Architectural hole",
            f"- axis: {certificate['hole']['axis']}",
            f"- kind: {certificate['hole']['kind']}",
            f"- claim: {certificate['hole']['claim']['claim']}",
            f"- unmet requirements: {', '.join(certificate['hole']['unmet_requirement_ids']) or 'none'}",
            "",
            "## Ordinary candidate",
            f"- artifact: {certificate['ordinary_candidate']['artifact']}",
            f"- law: {certificate['ordinary_candidate']['law']['claim']}",
            f"- falsifier: {certificate['ordinary_candidate']['falsifier']['claim']}",
            f"- resource impact: {certificate['ordinary_candidate']['resource_impact']['claim']}",
            "",
            "## Alternatives considered",
            f"- considered: {', '.join(certificate['alternatives']['considered']) or 'none'}",
            f"- eligible: {', '.join(certificate['alternatives']['eligible']) or 'none'}",
            f"- contradicted: {', '.join(certificate['alternatives']['contradicted']) or 'none'}",
            f"- unresolved: {', '.join(certificate['alternatives']['unresolved']) or 'none'}",
        ]
    )
    if certificate["alternatives"]["rejected"]:
        for rejection in certificate["alternatives"]["rejected"]:
            detail = rejection["rejection"]
            lines.append(
                f"- rejected {rejection['construction_key']} ({detail['basis']}): {detail['claim']} — "
                f"evidence: {', '.join(detail['evidence'])}"
            )
    else:
        lines.append("- rejected: none")
    lines.extend(
        [
            "",
            "## Nomination",
            f"- status: {nomination['status']}",
            f"- route nomination: {nomination.get('route_nomination') or 'none'}",
            f"- selected artifact: {nomination.get('selected_artifact') or 'none'}",
            f"- advanced mechanics: {nomination.get('advanced_mechanics', 'none')}",
            f"- reason: {nomination['reason']}",
        ]
    )
    if "construction_key" in nomination:
        lines.append(f"- construction key: {nomination['construction_key']}")
    if "expert_name" in nomination:
        lines.append(f"- expert name: {nomination['expert_name']}")

    lines.extend(["", "## Proof stack"])
    for heading, keys in proof_headings:
        lines.append(f"### {heading}")
        proof = next(
            (selected_proof[key] for key in keys if key in selected_proof), None
        )
        if proof is None:
            lines.append("- none")
        else:
            lines.append(f"- claim: {proof['claim']}")
            lines.append(f"- evidence: {', '.join(proof['evidence'])}")

    lines.extend(["", "## Material architectural delta"])
    for dimension, items in certificate["material_delta"].items():
        lines.append(f"### {dimension.replace('_', ' ').title()}")
        lines.extend(
            f"- {item['requirement_id']}: {item['candidate_claim']} — evidence: {', '.join(item['evidence'])}"
            for item in items
        )
    if not certificate["material_delta"]:
        lines.append("- none")

    lines.extend(["", "## Evidence debt"])
    lines.append(
        _markdown_list(
            json.dumps(item, sort_keys=True) for item in certificate["evidence_debt"]
        )
    )
    lines.extend(
        [
            "",
            "## Authority boundary",
            f"- compiler authority: {certificate['compiler_authority']}",
            f"- decision authority: {certificate['decision_authority']}",
            "- The compiler validates, nominates, or verifies evidence; the root workflow adjudicates and owns any consequential Ledger/Seq receipt.",
            "- Independent architectural axes require separate linked Universal Problem packets under the same root seam/plan.",
            f"- root adjudication required: {str(certificate['root_adjudication_required']).lower()}",
            f"- root decision evidence ready: {str(certificate['root_decision_evidence_ready']).lower()}",
            f"- theory exposed: {str(certificate['theory_exposed']).lower()}",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--problem", type=Path, help=f"Path to a {PROBLEM_SCHEMA} JSON file"
    )
    parser.add_argument("--registry", type=Path, default=_default_registry_path())
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--explain-theory", action="store_true")
    parser.add_argument("--validate-registry", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        registry = load_registry(args.registry)
        if args.validate_registry:
            output = (
                json.dumps(
                    {
                        "schema": registry["schema"],
                        "valid": True,
                        "constructions": len(registry["constructions"]),
                        "selectable": sum(
                            card["selection_mode"] == "selectable"
                            for card in registry["constructions"]
                        ),
                        "support_only": sum(
                            card["selection_mode"] == "support_only"
                            for card in registry["constructions"]
                        ),
                        "axes": list(registry["axes"]),
                        "proof_profiles": registry["proof_profiles"],
                        "scope_obligations": registry["scope_obligations"],
                        "rejection_bases": list(registry["rejection_bases"]),
                        "derived_mechanics": registry["derived_mechanics"],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
        else:
            if args.problem is None:
                raise ContractError(
                    "--problem is required unless --validate-registry is used"
                )
            problem = load_problem(args.problem, registry)
            certificate = compile_problem(
                problem, registry, explain_theory=args.explain_theory
            )
            output = (
                render_markdown(certificate)
                if args.format == "markdown"
                else json.dumps(certificate, indent=2, sort_keys=True) + "\n"
            )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 0
    except ContractError as exc:
        print(f"universal-problem: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
