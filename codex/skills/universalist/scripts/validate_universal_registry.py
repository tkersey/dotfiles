#!/usr/bin/env python3
"""Validate Universalist's compact theorem-card registry."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

SCHEMA = "universal-construction-registry/v1"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXPECTED_FIELDS = [
    "id", "name", "family", "ops", "question", "requires", "lower",
    "witness", "falsifier", "fallback", "delta",
]
EXPECTED_FAMILY_FIELDS = ["competitors", "mediator", "unique", "cost", "refs"]
EXPECTED_GUARD_FIELDS = ["id", "protects", "question", "failure"]
REQUIRED_CONCEPTS = {
    "category-world", "functor", "natural-transformation", "profunctor", "category-pivot",
    "product", "coproduct", "refinement-equalizer", "pullback", "quotient-coequalizer",
    "pushout", "double-pushout", "exponential", "free-construction",
    "adjunction-free-builder", "left-kan-extension", "right-kan-extension", "kan-lift",
    "residual-internal-hom", "representability", "obstruction", "algebra-interpreter",
    "algebraic-effects", "monad", "free-applicative", "behavioral-coalgebra", "yoneda",
    "coyoneda", "defunctionalization", "codensity-dense-dual", "monoidal-category",
    "freyd-category", "colored-operad", "prop-properad", "traced-feedback",
    "resource-sensitive-category", "pointwise-product", "day-convolution",
    "promonoidal-convolution", "operadic-substitution", "resource-convolution",
    "spatial-day-convolution", "coend-normalization", "tambara-module", "mixed-tambara",
    "optic-residual", "free-tambara", "cofree-tambara", "dependent-tambara",
    "contextual-representability", "day-center-tambara", "comonad-space",
    "comonad-coalgebra", "density-comonad", "halo-germ", "continuous-comonadic-map",
    "presheaf-site", "sheafification", "categorical-data", "delta-sigma-pi",
    "chase-closure", "exact-context", "algebraic-presentation", "primitive-presentation",
}


def load_registry(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"registry not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise SystemExit(f"invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"registry root must be a mapping: {path}")
    return data


def expand_rows(data: dict[str, Any], rows_key: str, fields_key: str) -> list[dict[str, Any]]:
    fields = data.get(fields_key)
    rows = data.get(rows_key)
    if not isinstance(fields, list) or not all(isinstance(x, str) for x in fields):
        raise ValueError(f"{fields_key} must be a string list")
    if not isinstance(rows, list):
        raise ValueError(f"{rows_key} must be a list")
    expanded: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != len(fields):
            raise ValueError(f"{rows_key}[{index}] must have {len(fields)} fields")
        expanded.append(dict(zip(fields, row, strict=True)))
    return expanded


def concept_cards(data: dict[str, Any], registry_path: Path) -> list[dict[str, Any]]:
    shards = data.get("shards")
    if not isinstance(shards, dict) or not shards:
        raise ValueError("shards must be a non-empty mapping")
    cards: list[dict[str, Any]] = []
    for family_id, relative in sorted(shards.items()):
        if not isinstance(relative, str) or not relative:
            raise ValueError(f"shard path for {family_id!r} must be non-empty text")
        shard_path = registry_path.parent.parent / relative
        shard = load_registry(shard_path)
        if shard.get("schema") != "universal-construction-family/v1":
            raise ValueError(f"{relative}: invalid family schema")
        if shard.get("family") != family_id:
            raise ValueError(f"{relative}: family id mismatch")
        if shard.get("concept_fields") != EXPECTED_FIELDS:
            raise ValueError(f"{relative}: concept_fields contract mismatch")
        cards.extend(expand_rows(shard, "concepts", "concept_fields"))
    return cards


def hypothesis_guards(data: dict[str, Any]) -> list[dict[str, Any]]:
    return expand_rows(data, "hypothesis_guards", "guard_fields")


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(path: Path, *, check_references: bool, root: Path | None) -> list[str]:
    data = load_registry(path)
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA!r}")
    if data.get("concept_fields") != EXPECTED_FIELDS:
        errors.append("concept_fields contract mismatch")
    if data.get("family_fields") != EXPECTED_FAMILY_FIELDS:
        errors.append("family_fields contract mismatch")
    if data.get("guard_fields") != EXPECTED_GUARD_FIELDS:
        errors.append("guard_fields contract mismatch")

    bytecode = data.get("bytecode")
    material = data.get("material_dimensions")
    bytecode_set = set(bytecode) if isinstance(bytecode, list) else set()
    material_set = set(material) if isinstance(material, list) else set()
    if not bytecode_set or len(bytecode_set) != len(bytecode or []):
        errors.append("bytecode must be a non-empty unique list")
    if not material_set or len(material_set) != len(material or []):
        errors.append("material_dimensions must be a non-empty unique list")

    try:
        cards = concept_cards(data, path)
        guards = hypothesis_guards(data)
    except ValueError as exc:
        return errors + [str(exc)]

    families_raw = data.get("families")
    if not isinstance(families_raw, dict):
        errors.append("families must be a mapping")
        families_raw = {}
    families: dict[str, dict[str, Any]] = {}
    for family_id, row in families_raw.items():
        if not isinstance(row, list) or len(row) != len(EXPECTED_FAMILY_FIELDS):
            errors.append(f"family {family_id!r} must have {len(EXPECTED_FAMILY_FIELDS)} fields")
            continue
        family = dict(zip(EXPECTED_FAMILY_FIELDS, row, strict=True))
        for key in ("competitors", "mediator", "unique", "cost"):
            if not nonempty_text(family[key]):
                errors.append(f"family {family_id!r}: {key} must be non-empty text")
        if not isinstance(family["refs"], list) or not family["refs"]:
            errors.append(f"family {family_id!r}: refs must be non-empty")
        elif check_references:
            assert root is not None
            for ref in family["refs"]:
                if not (root / ref).is_file():
                    errors.append(f"family {family_id!r}: missing reference {ref}")
        families[family_id] = family

    ids: set[str] = set()
    for card in cards:
        card_id = card["id"]
        if not isinstance(card_id, str) or not ID_RE.fullmatch(card_id):
            errors.append(f"invalid concept id: {card_id!r}")
            continue
        if card_id in ids:
            errors.append(f"duplicate concept id: {card_id}")
        ids.add(card_id)
        for key in ("name", "family", "question", "requires", "lower", "witness", "falsifier", "fallback"):
            if not nonempty_text(card[key]):
                errors.append(f"{card_id}: {key} must be non-empty text")
        if not isinstance(card["ops"], list) or not card["ops"]:
            errors.append(f"{card_id}: ops must be non-empty")
        else:
            for opcode in card["ops"]:
                if opcode not in bytecode_set:
                    errors.append(f"{card_id}: unknown opcode {opcode!r}")
        if not isinstance(card["delta"], list) or not card["delta"]:
            errors.append(f"{card_id}: delta must be non-empty")
        else:
            for dimension in card["delta"]:
                if dimension not in material_set:
                    errors.append(f"{card_id}: unknown material dimension {dimension!r}")
        if card["family"] not in families:
            errors.append(f"{card_id}: unknown family {card['family']!r}")

    missing = sorted(REQUIRED_CONCEPTS - ids)
    if missing:
        errors.append("missing required concepts: " + ", ".join(missing))

    guard_ids: set[str] = set()
    for guard in guards:
        guard_id = guard["id"]
        if not isinstance(guard_id, str) or not ID_RE.fullmatch(guard_id):
            errors.append(f"invalid guard id: {guard_id!r}")
            continue
        if guard_id in guard_ids:
            errors.append(f"duplicate guard id: {guard_id}")
        guard_ids.add(guard_id)
        if not isinstance(guard["protects"], list) or not guard["protects"]:
            errors.append(f"{guard_id}: protects must be non-empty")
        for concept_id in guard.get("protects", []):
            if concept_id not in ids:
                errors.append(f"{guard_id}: protects unknown concept {concept_id!r}")
        for key in ("question", "failure"):
            if not nonempty_text(guard[key]):
                errors.append(f"{guard_id}: {key} must be non-empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", nargs="?", type=Path, default=Path(__file__).resolve().parents[1] / "references" / "universal-construction-registry.yaml")
    parser.add_argument("--check-references", action="store_true")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.registry, check_references=args.check_references, root=args.root if args.check_references else None)
    if errors:
        print("universal construction registry: invalid", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    data = load_registry(args.registry)
    print(f"universal construction registry: ok ({len(concept_cards(data, args.registry))} concepts, {len(hypothesis_guards(data))} guards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
