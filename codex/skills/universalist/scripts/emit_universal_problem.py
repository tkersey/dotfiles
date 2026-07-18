#!/usr/bin/env python3
"""Emit a Universalist certificate from the compact theorem-card registry."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

FIELDS = ["id", "name", "family", "ops", "question", "requires", "lower", "witness", "falsifier", "fallback", "delta"]
FAMILY_FIELDS = ["competitors", "mediator", "unique", "cost", "refs"]


def load_registry(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("concept_fields") != FIELDS:
        raise SystemExit(f"invalid compact registry: {path}")
    return data


def cards(data: dict[str, Any], registry_path: Path) -> list[dict[str, Any]]:
    shards = data.get("shards")
    if not isinstance(shards, dict) or not shards:
        raise SystemExit("invalid registry shards")
    result: list[dict[str, Any]] = []
    for family_id, relative in sorted(shards.items()):
        shard_path = registry_path.parent.parent / relative
        shard = yaml.safe_load(shard_path.read_text(encoding="utf-8"))
        if not isinstance(shard, dict) or shard.get("schema") != "universal-construction-family/v1" or shard.get("family") != family_id:
            raise SystemExit(f"invalid concept shard: {relative}")
        for index, row in enumerate(shard.get("concepts", [])):
            if not isinstance(row, list) or len(row) != len(FIELDS):
                raise SystemExit(f"invalid concept row {relative}:{index}")
            result.append(dict(zip(FIELDS, row, strict=True)))
    return result


def find_card(data: dict[str, Any], registry_path: Path, concept_id: str) -> dict[str, Any]:
    all_cards = cards(data, registry_path)
    for card in all_cards:
        if card["id"] == concept_id:
            return card
    known = ", ".join(sorted(card["id"] for card in all_cards))
    raise SystemExit(f"unknown concept id {concept_id!r}; known concepts: {known}")


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def render(data: dict[str, Any], card: dict[str, Any], *, expert: bool) -> str:
    family = dict(zip(FAMILY_FIELDS, data["families"][card["family"]], strict=True))
    refs = family["refs"]
    expert_line = f"\n**Expert construction:** {card['name']}\n" if expert else ""
    expert_note = f"\n## Expert references\n\n{bullets(refs)}\n" if expert else ""
    return f"""# Universal Problem Certificate: {card['id']}

## Architectural hole

- Seam:
- Owner:
- Hole kind / polarity:
- Required observations:
- Effects / authority / resources:
{expert_line}
## Boring candidate

- Artifact:
- Law:
- Falsifier:

## Hidden architectural question

{card['question']}

## Preconditions

{card['requires']}

## Admissible competitors

{family['competitors']}

## Universal completion

- Bytecode: {', '.join(card['ops'])}
- Mediator: {family['mediator']}
- Canonicality: {family['unique']}

## Effective repository-native lowering

{card['lower']}

## Proof obligations

### Existence

- Effective constructor / interpreter / query / representation:

### Commutation / preservation

- {card['witness']}

### Mediation / factorization

- Every admissible competitor reaches or is reached from the owner through:

### Canonicality

- Unique up to observations / normal form / one public construction path:

### Effectivity

- {family['cost']}

### Falsifier

- {card['falsifier']}

## Boring fallback

{card['fallback']}

## Material delta

The card is retained only when it changes at least one of:

{bullets(card['delta'])}

- Actual changed dimensions:
- Selected: ordinary / universal / obstruction
- Rationale:
{expert_note}"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("concept_id", nargs="?")
    parser.add_argument("--expert", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--registry", type=Path, default=Path(__file__).resolve().parents[1] / "references" / "universal-construction-registry.yaml")
    args = parser.parse_args()
    data = load_registry(args.registry)
    if args.list:
        for card in cards(data, args.registry):
            print(f"{card['id']}\t{card['name']}")
        return 0
    if not args.concept_id:
        parser.error("concept_id is required unless --list is used")
    card = find_card(data, args.registry, args.concept_id)
    if args.as_json:
        json.dump(card, sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        print(render(data, card, expert=args.expert))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
