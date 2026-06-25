#!/usr/bin/env python3
"""Validate validation_matrix / VMX-v1."""

from __future__ import annotations

import argparse
import json

from common import load_document, require_list, require_object, unwrap, yes, no

ROW_STATES = {"open", "selected", "proved", "reopened", "superseded"}
EXPECTED = {"accept", "reject", "normalize", "defer", "error"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        body = unwrap(load_document(args.file), "validation_matrix")
    except Exception as exc:
        body = {}
        errors.append(str(exc))

    if body.get("matrix_version") != "VMX-v1":
        errors.append("matrix_version")
    for key in ("matrix_id", "domain", "owner", "invariant"):
        if not body.get(key):
            errors.append(key)
    require_object(body, "artifact_state", errors)

    dimensions = require_list(body, "dimensions", errors)
    dimension_names: set[str] = set()
    for index, dim in enumerate(dimensions):
        if not isinstance(dim, dict) or not dim.get("name") or not isinstance(dim.get("values"), list):
            errors.append(f"dimensions[{index}]")
            continue
        name = dim["name"]
        if name in dimension_names:
            errors.append(f"dimensions:duplicate:{name}")
        dimension_names.add(name)

    classes = require_list(body, "equivalence_classes", errors)
    class_ids: set[str] = set()
    representatives: dict[str, str] = {}
    for index, cls in enumerate(classes):
        if not isinstance(cls, dict):
            errors.append(f"equivalence_classes[{index}]")
            continue
        cid = cls.get("class_id")
        if not cid:
            errors.append(f"equivalence_classes[{index}].class_id")
            continue
        if cid in class_ids:
            errors.append(f"equivalence_classes:duplicate:{cid}")
        class_ids.add(cid)
        if not cls.get("governing_invariant") or not cls.get("proof_obligation"):
            errors.append(f"equivalence_classes[{index}]:invariant-or-proof")
        if cls.get("representative_row"):
            representatives[cid] = cls["representative_row"]
        require_list(cls, "covered_combinations", errors)

    rows = require_list(body, "rows", errors)
    row_ids: set[str] = set()
    selected: list[str] = []
    signatures: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"rows[{index}]")
            continue
        rid = row.get("row_id")
        cid = row.get("class_id")
        if not rid:
            errors.append(f"rows[{index}].row_id")
            continue
        if rid in row_ids:
            errors.append(f"rows:duplicate-id:{rid}")
        row_ids.add(rid)
        if cid not in class_ids:
            errors.append(f"rows[{index}].class_id:unknown:{cid}")
        conditions = row.get("conditions")
        if not isinstance(conditions, dict):
            errors.append(f"rows[{index}].conditions")
            conditions = {}
        unknown_dims = set(conditions) - dimension_names
        for name in sorted(unknown_dims):
            errors.append(f"rows[{index}].conditions:unknown-dimension:{name}")
        if row.get("expected") not in EXPECTED:
            errors.append(f"rows[{index}].expected")
        for key in ("authority_owner", "producer", "validator"):
            if not row.get(key):
                errors.append(f"rows[{index}].{key}")
        require_list(row, "existing_proof_refs", errors)
        require_list(row, "missing_proof", errors)
        require_list(row, "evidence_refs", errors)
        state = row.get("status")
        if state not in ROW_STATES:
            errors.append(f"rows[{index}].status")
        if state == "selected":
            selected.append(rid)
        signature = json.dumps(
            {"conditions": conditions, "expected": row.get("expected")},
            sort_keys=True,
        )
        if signature in signatures:
            errors.append(f"rows:duplicate-semantic-row:{rid}")
        signatures.add(signature)

    for cid, rid in representatives.items():
        if rid not in row_ids:
            errors.append(f"equivalence_classes.{cid}:unknown-representative:{rid}")

    completeness = require_object(body, "completeness", errors)
    if completeness.get("boundary_classes_covered") not in {"yes", "no", True, False}:
        errors.append("completeness.boundary_classes_covered")
    for key in ("malformed_classes_covered", "transition_classes_covered"):
        if completeness.get(key) not in {"yes", "no", True, False, "not_applicable"}:
            errors.append(f"completeness.{key}")
    require_list(completeness, "known_unknowns", errors)

    gate = require_object(body, "gate", errors)
    for key in ("selected_rows_valid", "duplicate_rows_absent", "mutation_allowed"):
        if not (yes(gate.get(key)) or no(gate.get(key))):
            errors.append(f"gate.{key}")
    if yes(gate.get("selected_rows_valid")) and not selected:
        errors.append("gate.selected_rows_valid:no-selected-rows")
    if yes(gate.get("duplicate_rows_absent")) and any("duplicate-semantic-row" in e for e in errors):
        errors.append("gate.duplicate_rows_absent:contradicted")
    if yes(gate.get("mutation_allowed")):
        if not selected:
            errors.append("gate.mutation_allowed:no-selected-row")
        if not yes(gate.get("selected_rows_valid")) or not yes(gate.get("duplicate_rows_absent")):
            errors.append("gate.mutation_allowed:matrix-gates-fail")

    result = {
        "validation_matrix_gate": {
            "verdict": "pass" if not errors else "fail",
            "matrix_id": body.get("matrix_id"),
            "selected_rows": selected,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
