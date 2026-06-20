#!/usr/bin/env python3
"""Structural and relational lint for minimum_behavioral_kernel / MBK-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if "minimum_behavioral_kernel" in value:
        value = value["minimum_behavioral_kernel"]
    if not isinstance(value, dict):
        raise ValueError("kernel must be a JSON object")
    return value


def ids(rows: Any, field: str, errors: list[str], prefix: str) -> set[str]:
    if not isinstance(rows, list):
        errors.append(f"{prefix}:must-be-list")
        return set()
    values: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{prefix}[{index}]:must-be-object")
            continue
        value = row.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{prefix}[{index}].{field}:missing")
            continue
        if value in values:
            errors.append(f"{prefix}:{field}:duplicate:{value}")
        values.add(value)
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    try:
        kernel = load(args.file)
    except Exception as exc:
        print(json.dumps({"kernel_lint": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    if kernel.get("kernel_version") != "MBK-v1":
        errors.append("kernel_version:expected-MBK-v1")
    for field in ["campaign_id", "campaign_base_sha", "acceptance_contract", "gate"]:
        if kernel.get(field) in (None, "", [], {}):
            errors.append(f"{field}:missing")

    authority_ids = ids(kernel.get("authorities"), "authority_id", errors, "authorities")
    carrier_ids = ids(kernel.get("carriers"), "carrier_id", errors, "carriers")
    observation_ids = ids(kernel.get("observations"), "observation_id", errors, "observations")
    class_ids = ids(kernel.get("equivalence_classes"), "class_id", errors, "equivalence_classes")
    operation_ids = ids(kernel.get("operations"), "operation_id", errors, "operations")
    transition_ids = ids(kernel.get("transitions"), "transition_id", errors, "transitions")
    law_ids = ids(kernel.get("laws"), "law_id", errors, "laws")
    family_ids = ids(kernel.get("counterexample_families"), "family_id", errors, "counterexample_families")

    if not authority_ids:
        errors.append("authorities:empty")
    if not observation_ids:
        errors.append("observations:empty")
    if not law_ids:
        errors.append("laws:empty")

    for row in kernel.get("operations", []) if isinstance(kernel.get("operations"), list) else []:
        owner = row.get("authority_id")
        if owner not in authority_ids:
            errors.append(f"operation:{row.get('operation_id')}:unknown-authority:{owner}")

    for row in kernel.get("transitions", []) if isinstance(kernel.get("transitions"), list) else []:
        operation = row.get("operation_id")
        if operation not in operation_ids:
            errors.append(f"transition:{row.get('transition_id')}:unknown-operation:{operation}")
        for key in ("from_classes", "to_classes"):
            values = row.get(key, [])
            if not isinstance(values, list):
                errors.append(f"transition:{row.get('transition_id')}:{key}:must-be-list")
                continue
            for value in values:
                if value not in class_ids:
                    errors.append(f"transition:{row.get('transition_id')}:{key}:unknown-class:{value}")

    for row in kernel.get("laws", []) if isinstance(kernel.get("laws"), list) else []:
        owner = row.get("owner")
        if owner not in authority_ids:
            errors.append(f"law:{row.get('law_id')}:unknown-owner:{owner}")
        obs = row.get("observation_ids", [])
        if not isinstance(obs, list) or not obs:
            errors.append(f"law:{row.get('law_id')}:observation_ids:empty")
        else:
            for value in obs:
                if value not in observation_ids:
                    errors.append(f"law:{row.get('law_id')}:unknown-observation:{value}")
        obligations = row.get("proof_obligations", [])
        if not isinstance(obligations, list) or not obligations:
            errors.append(f"law:{row.get('law_id')}:proof_obligations:empty")

    for row in kernel.get("counterexample_families", []) if isinstance(kernel.get("counterexample_families"), list) else []:
        governing = row.get("governing_law_ids", [])
        if not isinstance(governing, list) or not governing:
            errors.append(f"family:{row.get('family_id')}:governing_law_ids:empty")
        else:
            for value in governing:
                if value not in law_ids:
                    errors.append(f"family:{row.get('family_id')}:unknown-law:{value}")
        if not row.get("independent_witnesses"):
            warnings.append(f"family:{row.get('family_id')}:no-independent-witness")

    for row in kernel.get("equivalence_classes", []) if isinstance(kernel.get("equivalence_classes"), list) else []:
        distinctions = row.get("distinguished_from", [])
        if not isinstance(distinctions, list):
            errors.append(f"class:{row.get('class_id')}:distinguished_from:must-be-list")
            continue
        for distinction in distinctions:
            if not isinstance(distinction, dict):
                errors.append(f"class:{row.get('class_id')}:invalid-distinction")
                continue
            other = distinction.get("class_id")
            if other not in class_ids:
                errors.append(f"class:{row.get('class_id')}:unknown-distinguished-class:{other}")
            witness_ids = distinction.get("witness_observation_ids", [])
            if not isinstance(witness_ids, list) or not witness_ids:
                errors.append(f"class:{row.get('class_id')}:distinction-without-witness:{other}")
            else:
                for value in witness_ids:
                    if value not in observation_ids:
                        errors.append(f"class:{row.get('class_id')}:unknown-witness:{value}")

    quotient = kernel.get("quotient", {})
    if not isinstance(quotient, dict):
        errors.append("quotient:must-be-object")
    elif quotient.get("method") not in {
        "exact_partition_refinement",
        "exact_bisimulation",
        "witness_checked_manual",
        "not_applicable",
    }:
        errors.append("quotient.method:invalid")

    gate = kernel.get("gate", {})
    required_gate = [
        "all_branch_liabilities_covered",
        "every_distinction_has_witness",
        "every_family_maps_to_law",
        "no_local_surface_family_without_governing_law",
        "non_goals_preserved",
    ]
    if not isinstance(gate, dict):
        errors.append("gate:must-be-object")
    else:
        for field in required_gate:
            if gate.get(field) != "pass":
                errors.append(f"gate.{field}:not-pass")
        if gate.get("kernel_review_allowed") != "yes":
            errors.append("gate.kernel_review_allowed:not-yes")

    result = {
        "kernel_lint": {
            "verdict": "pass" if not errors else "fail",
            "counts": {
                "authorities": len(authority_ids),
                "carriers": len(carrier_ids),
                "observations": len(observation_ids),
                "equivalence_classes": len(class_ids),
                "operations": len(operation_ids),
                "transitions": len(transition_ids),
                "laws": len(law_ids),
                "families": len(family_ids),
            },
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
