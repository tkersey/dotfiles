#!/usr/bin/env python3
"""Compile one boundary problem through Universalist's hidden theorem registry.

The default output deliberately uses plain engineering language. Pass
--explain-theory to include categorical names for audit or expert explanation.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

SCHEMA = "universal-problem/v1"
CERTIFICATE_SCHEMA = "universal-problem-certificate/v1"
VALID_ROUTES = {"UNI-PRESERVE", "UNI-ORDINARY", "UNI-CANONICAL", "UNI-OBSTRUCT"}


class ContractError(ValueError):
    """Raised when a registry or problem violates its contract."""


@dataclass(frozen=True)
class Candidate:
    card: Mapping[str, Any]
    matched_signals: tuple[str, ...]
    missing_prerequisites: tuple[str, ...]

    @property
    def available(self) -> bool:
        return not self.missing_prerequisites

    @property
    def rank(self) -> tuple[int, int, str]:
        # More matched signals first, then the weakest/lower-priority construction.
        return (-len(self.matched_signals), int(self.card["priority"]), str(self.card["id"]))


def _default_registry_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "universal-construction-registry.yaml"


def _truthy_fact(facts: Mapping[str, Any], key: str) -> bool:
    value = facts.get(key)
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (str, Sequence, Mapping)):
        return bool(value)
    return bool(value)


def load_registry(path: Path) -> dict[str, Any]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"registry not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ContractError(f"invalid registry YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ContractError("registry must be a mapping")
    includes = raw.pop("includes", [])
    if includes:
        if not isinstance(includes, list) or not all(isinstance(v, str) and v for v in includes):
            raise ContractError("registry includes must be a string list")
        constructions: list[dict[str, Any]] = []
        for relative in includes:
            include_path = path.parent / relative
            try:
                fragment = yaml.safe_load(include_path.read_text(encoding="utf-8"))
            except FileNotFoundError as exc:
                raise ContractError(f"registry include not found: {include_path}") from exc
            except yaml.YAMLError as exc:
                raise ContractError(f"invalid registry include {include_path}: {exc}") from exc
            if not isinstance(fragment, dict) or not isinstance(fragment.get("constructions"), list):
                raise ContractError(f"registry include must contain constructions: {include_path}")
            constructions.extend(fragment["constructions"])
        raw["constructions"] = constructions
    validate_registry(raw)
    return raw


def validate_registry(registry: Mapping[str, Any]) -> None:
    if registry.get("schema") != "universal-construction-registry/v1":
        raise ContractError("unsupported registry schema")
    material = registry.get("material_dimensions")
    moves = registry.get("moves")
    cards = registry.get("constructions")
    if not isinstance(material, list) or not material or not all(isinstance(v, str) for v in material):
        raise ContractError("registry material_dimensions must be a non-empty string list")
    if not isinstance(moves, dict) or not moves:
        raise ContractError("registry moves must be a non-empty mapping")
    if not isinstance(cards, list) or not cards:
        raise ContractError("registry constructions must be a non-empty list")

    seen: set[str] = set()
    required_fields = {
        "id", "expert_name", "public_name", "route", "priority", "moves", "signals",
        "requires", "emits", "laws", "falsifiers", "fallback", "universal",
    }
    for index, card in enumerate(cards):
        if not isinstance(card, dict):
            raise ContractError(f"construction {index} must be a mapping")
        missing = sorted(required_fields - card.keys())
        if missing:
            raise ContractError(f"construction {index} missing fields: {', '.join(missing)}")
        card_id = card["id"]
        if not isinstance(card_id, str) or not card_id:
            raise ContractError(f"construction {index} has invalid id")
        if card_id in seen:
            raise ContractError(f"duplicate construction id: {card_id}")
        seen.add(card_id)
        if card["route"] not in VALID_ROUTES:
            raise ContractError(f"construction {card_id} has invalid route: {card['route']}")
        if not isinstance(card["priority"], int):
            raise ContractError(f"construction {card_id} priority must be an integer")
        for field in ("moves", "signals", "requires", "emits", "laws", "falsifiers"):
            if not isinstance(card[field], list) or not all(isinstance(v, str) and v for v in card[field]):
                raise ContractError(f"construction {card_id} field {field} must be a string list")
        unknown_moves = sorted(set(card["moves"]) - set(moves))
        if unknown_moves:
            raise ContractError(f"construction {card_id} uses unknown moves: {', '.join(unknown_moves)}")
        if not card["signals"]:
            raise ContractError(f"construction {card_id} must have at least one signal")
        if not card["laws"] or not card["falsifiers"]:
            raise ContractError(f"construction {card_id} must include laws and falsifiers")
        universal = card["universal"]
        if not isinstance(universal, dict):
            raise ContractError(f"construction {card_id} universal must be a mapping")
        for field in ("role", "competitors", "mediator", "canonicality", "effectivity"):
            if not isinstance(universal.get(field), str) or not universal[field].strip():
                raise ContractError(f"construction {card_id} universal.{field} must be a non-empty string")
        roles = registry.get("universal_roles")
        if not isinstance(roles, dict) or universal["role"] not in roles:
            raise ContractError(f"construction {card_id} uses unknown universal role: {universal['role']}")


def load_problem(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"problem not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid problem JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ContractError("problem must be a JSON object")
    validate_problem(raw)
    return raw


def validate_problem(problem: Mapping[str, Any]) -> None:
    if problem.get("schema") != SCHEMA:
        raise ContractError(f"problem schema must be {SCHEMA}")
    for field in ("seam", "owner"):
        if not isinstance(problem.get(field), str) or not problem[field].strip():
            raise ContractError(f"problem field {field} must be a non-empty string")
    signals = problem.get("signals")
    if not isinstance(signals, list) or not all(isinstance(v, str) and v for v in signals):
        raise ContractError("problem signals must be a string list")
    facts = problem.get("facts", {})
    if not isinstance(facts, dict):
        raise ContractError("problem facts must be an object")
    ordinary = problem.get("ordinary_candidate")
    if not isinstance(ordinary, dict):
        raise ContractError("problem ordinary_candidate must be an object")
    for field in ("artifact", "law", "falsifier"):
        if not isinstance(ordinary.get(field), str) or not ordinary[field].strip():
            raise ContractError(f"ordinary_candidate.{field} must be a non-empty string")
    delta = problem.get("material_delta", {})
    if not isinstance(delta, dict):
        raise ContractError("problem material_delta must be an object")


def _material_delta(problem: Mapping[str, Any], registry: Mapping[str, Any]) -> dict[str, Any]:
    supplied = problem.get("material_delta", {})
    result: dict[str, Any] = {}
    for dimension in registry["material_dimensions"]:
        value = supplied.get(dimension)
        if value is None or value is False or value == "" or value == [] or value == {}:
            continue
        result[dimension] = value
    return result


def candidates_for(problem: Mapping[str, Any], registry: Mapping[str, Any]) -> list[Candidate]:
    signals = set(problem.get("signals", []))
    facts = problem.get("facts", {})
    candidates: list[Candidate] = []
    for card in registry["constructions"]:
        matched = tuple(sorted(signals.intersection(card["signals"])))
        if not matched:
            continue
        missing = tuple(sorted(key for key in card["requires"] if not _truthy_fact(facts, key)))
        candidates.append(Candidate(card=card, matched_signals=matched, missing_prerequisites=missing))
    return sorted(candidates, key=lambda candidate: candidate.rank)


def compile_problem(
    problem: Mapping[str, Any],
    registry: Mapping[str, Any],
    *,
    explain_theory: bool = False,
) -> dict[str, Any]:
    validate_problem(problem)
    validate_registry(registry)

    ordinary = dict(problem["ordinary_candidate"])
    delta = _material_delta(problem, registry)
    candidates = candidates_for(problem, registry)
    available = [candidate for candidate in candidates if candidate.available]
    blocked = [candidate for candidate in candidates if not candidate.available]

    shadow: dict[str, Any]
    decision: dict[str, Any]

    if not delta:
        shadow = {
            "status": "discarded-no-material-delta",
            "considered": [candidate.card["public_name"] for candidate in candidates],
            "reason": "The hidden theorem pass changes no material architectural dimension.",
        }
        decision = {
            "route": "UNI-PRESERVE",
            "selected_artifact": ordinary["artifact"],
            "advanced_mechanics": "none",
            "material_delta": {},
        }
    elif available:
        selected = available[0]
        card = selected.card
        shadow = {
            "status": "selected",
            "construction_key": card["id"],
            "plain_construction": card["public_name"],
            "moves": list(card["moves"]),
            "matched_signals": list(selected.matched_signals),
            "emits": list(card["emits"]),
            "laws": list(card["laws"]),
            "falsifiers": list(card["falsifiers"]),
            "fallback": card["fallback"],
            "universal": dict(card["universal"]),
        }
        if explain_theory:
            shadow["expert_name"] = card["expert_name"]
        decision = {
            "route": card["route"],
            "selected_artifact": card["public_name"],
            "advanced_mechanics": card["id"] if card["route"] == "UNI-CANONICAL" else "none",
            "material_delta": delta,
        }
    elif blocked:
        strict = bool(problem.get("strict_universal", False))
        strongest = blocked[0]
        shadow = {
            "status": "blocked-missing-prerequisites",
            "candidate": strongest.card["public_name"],
            "matched_signals": list(strongest.matched_signals),
            "missing_prerequisites": list(strongest.missing_prerequisites),
            "fallback": strongest.card["fallback"],
            "universal": dict(strongest.card["universal"]),
            "laws": list(strongest.card["laws"]),
            "falsifiers": list(strongest.card["falsifiers"]),
        }
        if explain_theory:
            shadow["expert_name"] = strongest.card["expert_name"]
        if strict:
            decision = {
                "route": "UNI-OBSTRUCT",
                "selected_artifact": "explicit architectural obstruction",
                "advanced_mechanics": "none",
                "material_delta": delta,
            }
        else:
            decision = {
                "route": "UNI-ORDINARY",
                "selected_artifact": ordinary["artifact"],
                "advanced_mechanics": "none",
                "material_delta": delta,
            }
    else:
        shadow = {
            "status": "no-theorem-card-matched",
            "reason": "Keep the repository-native candidate; no registered universal problem was evidenced.",
        }
        decision = {
            "route": "UNI-ORDINARY",
            "selected_artifact": ordinary["artifact"],
            "advanced_mechanics": "none",
            "material_delta": delta,
        }

    return {
        "schema": CERTIFICATE_SCHEMA,
        "seam": problem["seam"],
        "owner": problem["owner"],
        "observations": list(problem.get("observations", [])),
        "ordinary_candidate": ordinary,
        "shadow": shadow,
        "decision": decision,
        "theory_exposed": explain_theory,
    }


def _markdown_list(values: Iterable[Any]) -> str:
    items = list(values)
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def render_markdown(certificate: Mapping[str, Any]) -> str:
    shadow = certificate["shadow"]
    decision = certificate["decision"]
    lines = [
        "# Universal Problem Certificate",
        "",
        "## Seam",
        certificate["seam"],
        "",
        "## Owner",
        certificate["owner"],
        "",
        "## Ordinary candidate",
        f"- artifact: {certificate['ordinary_candidate']['artifact']}",
        f"- law: {certificate['ordinary_candidate']['law']}",
        f"- falsifier: {certificate['ordinary_candidate']['falsifier']}",
        "",
        "## Universal shadow",
        f"- status: {shadow['status']}",
    ]
    for field in ("plain_construction", "candidate", "construction_key", "expert_name", "fallback", "reason"):
        if field in shadow:
            lines.append(f"- {field.replace('_', ' ')}: {shadow[field]}")
    if "universal" in shadow:
        universal = shadow["universal"]
        lines.extend([
            "",
            "### Universal witness",
            f"- role: {universal['role']}",
            f"- admissible competitors: {universal['competitors']}",
            f"- mediator: {universal['mediator']}",
            f"- canonicality: {universal['canonicality']}",
            f"- effectivity: {universal['effectivity']}",
        ])
    for field in ("moves", "matched_signals", "missing_prerequisites", "emits", "laws", "falsifiers"):
        if field in shadow:
            lines.extend(["", f"### {field.replace('_', ' ').title()}", _markdown_list(shadow[field])])
    lines.extend([
        "",
        "## Material delta",
        _markdown_list(f"{key}: {value}" for key, value in decision["material_delta"].items()),
        "",
        "## Decision",
        f"- route: {decision['route']}",
        f"- selected artifact: {decision['selected_artifact']}",
        f"- advanced mechanics: {decision['advanced_mechanics']}",
        f"- theory exposed: {str(certificate['theory_exposed']).lower()}",
        "",
    ])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem", type=Path, help="Path to a universal-problem/v1 JSON file")
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
            output = json.dumps({"schema": registry["schema"], "valid": True, "constructions": len(registry["constructions"])}, indent=2) + "\n"
        else:
            if args.problem is None:
                raise ContractError("--problem is required unless --validate-registry is used")
            problem = load_problem(args.problem)
            certificate = compile_problem(problem, registry, explain_theory=args.explain_theory)
            if args.format == "markdown":
                output = render_markdown(certificate)
            else:
                output = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
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
