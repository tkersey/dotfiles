#!/usr/bin/env python3
"""Classify candidate ADD operations/laws into likely algebraic structures.

Input JSON shape:
{
  "carrier": "EvidenceSet",
  "operations": [
    {
      "name": "mergeEvidence",
      "arity": 2,
      "identity": "emptyEvidence",
      "laws": ["associativity", "commutativity", "idempotency"]
    }
  ]
}

Usage:
  python scripts/classify_algebra.py --input domain.json
  echo '{...}' | python scripts/classify_algebra.py
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any

LAW_ALIASES = {
    "assoc": "associativity",
    "associative": "associativity",
    "associativity": "associativity",
    "identity": "identity",
    "left_identity": "left_identity",
    "right_identity": "right_identity",
    "comm": "commutativity",
    "commutative": "commutativity",
    "commutativity": "commutativity",
    "idem": "idempotency",
    "idempotent": "idempotency",
    "idempotency": "idempotency",
    "inverse": "inverse",
    "invertible": "inverse",
    "annihilator": "annihilator",
    "absorbing": "annihilator",
    "distributive": "distributivity",
    "distributivity": "distributivity",
    "monotone": "monotonicity",
    "monotonicity": "monotonicity",
    "closure": "closure",
}

@dataclass
class Classification:
    structure: str
    confidence: str
    rationale: str
    implications: list[str]
    tests: list[str]


def normalize_laws(raw: Any) -> set[str]:
    if not raw:
        return set()
    if isinstance(raw, str):
        raw = [raw]
    result: set[str] = set()
    for item in raw:
        key = str(item).strip().lower().replace("-", "_").replace(" ", "_")
        result.add(LAW_ALIASES.get(key, key))
    if "identity" in result:
        result.add("left_identity")
        result.add("right_identity")
    return result


def classify_operation(op: dict[str, Any]) -> list[Classification]:
    name = op.get("name", "<unnamed>")
    laws = normalize_laws(op.get("laws", []))
    has_identity = bool(op.get("identity")) or {"left_identity", "right_identity"}.issubset(laws)
    arity = int(op.get("arity", 2) or 2)
    out: list[Classification] = []

    if arity == 2 and "associativity" in laws:
        if has_identity:
            out.append(Classification(
                "monoid",
                "high",
                f"{name} is associative and has an identity.",
                ["supports folding zero or more values", "enables safe empty/default value if identity is truly unobservable"],
                ["left identity", "right identity", "associativity"],
            ))
        else:
            out.append(Classification(
                "semigroup",
                "high",
                f"{name} is associative but no identity was supplied.",
                ["supports combining non-empty collections", "supports chunking if no hidden effects break grouping"],
                ["associativity"],
            ))

    if arity == 2 and "associativity" in laws and "commutativity" in laws and has_identity:
        out.append(Classification(
            "commutative monoid",
            "high",
            f"{name} is associative, commutative, and has an identity.",
            ["order-insensitive accumulation", "parallel aggregation", "reconciliation from unordered inputs"],
            ["associativity", "commutativity", "left/right identity"],
        ))

    if arity == 2 and {"associativity", "commutativity", "idempotency"}.issubset(laws):
        out.append(Classification(
            "join semilattice / idempotent commutative semigroup",
            "high" if has_identity else "medium",
            f"{name} is associative, commutative, and idempotent.",
            ["duplicate-tolerant merge", "distributed convergence if partial order is valid", "safe evidence/config/set-style accumulation"],
            ["associativity", "commutativity", "idempotency", "merge convergence"],
        ))

    if has_identity and "inverse" in laws:
        out.append(Classification(
            "group-like structure",
            "medium",
            f"{name} has an identity and inverse law. Verify the observation excludes irreversible effects.",
            ["undo may be possible", "round-trip tests are required", "audit/external effects may invalidate invertibility"],
            ["left inverse", "right inverse", "round-trip observation equality"],
        ))

    if "annihilator" in laws:
        out.append(Classification(
            "annihilator / absorbing element",
            "high",
            f"{name} has a blocking or absorbing value.",
            ["model validation blockers, deny-overrides, missing approval, or fatal errors", "enforce with runtime guards"],
            ["absorbing left", "absorbing right", "blocked trace has no external effect"],
        ))

    if "distributivity" in laws:
        out.append(Classification(
            "distributive operation candidate",
            "medium",
            f"{name} participates in a distributive law.",
            ["query optimization", "pipeline fusion", "push computation to source"],
            ["compare distributed vs non-distributed evaluation paths"],
        ))

    if "monotonicity" in laws:
        out.append(Classification(
            "monotone computation",
            "medium",
            f"{name} appears monotone under an ordering.",
            ["append-only/event/dataflow designs", "incremental projections", "fewer retractions"],
            ["if a <= b, assert f(a) <= f(b)"],
        ))

    if not out:
        out.append(Classification(
            "unclassified",
            "low",
            f"Not enough laws were supplied for {name}.",
            ["identify observations", "test associativity, identity, commutativity, idempotency, and counterexamples"],
            ["closure", "example-based laws", "counterexample tests"],
        ))

    return out


def load_input(path: str | None) -> dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify ADD operations by laws.")
    parser.add_argument("--input", "-i", help="Path to JSON input. Reads stdin if omitted.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    try:
        data = load_input(args.input)
    except Exception as exc:  # noqa: BLE001
        print(f"error: failed to read input JSON: {exc}", file=sys.stderr)
        return 2

    operations = data.get("operations", [])
    if not isinstance(operations, list):
        print("error: input field 'operations' must be a list", file=sys.stderr)
        return 2

    result = {
        "carrier": data.get("carrier"),
        "classifications": [],
    }
    for op in operations:
        if not isinstance(op, dict):
            continue
        result["classifications"].append({
            "operation": op.get("name", "<unnamed>"),
            "candidates": [c.__dict__ for c in classify_operation(op)],
        })

    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
