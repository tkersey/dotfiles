#!/usr/bin/env python3
"""Structural gate for Review Distillation Receipt RDR-v1."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    r"review_distillation_receipt\s*:",
    r"receipt_version\s*:\s*RDR-v1",
    r"frozen_delivery_base\s*:",
    r"branch_liability_boundary\s*:",
    r"canonical_owner\s*:",
    r"normal_forms_falsified\s*:",
    r"route_families_eliminated\s*:",
    r"counterexamples\s*:",
    r"surfaces_to_retire\s*:",
    r"candidate_routes\s*:",
    r"selected_route\s*:",
    r"proof_matrix\s*:",
    r"delivery_rederivation\s*:",
    r"rederive_from_frozen_base\s*:\s*yes",
    r"cherry_pick_lab_commits\s*:\s*no",
    r"distillation_complete\s*:\s*pass",
    r"delivery_mutation_allowed\s*:\s*(yes|no)",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: distillation_gate.py <rdr.yml>", file=sys.stderr)
        return 1
    text = Path(argv[1]).read_text(encoding="utf-8")
    errors = [f"missing:{pattern}" for pattern in REQUIRED if re.search(pattern, text, re.M) is None]
    if re.search(r"route\s*:\s*normal-form-decision", text):
        errors.append("distillation must emit distilled-normal-form, not ordinary normal-form-decision")
    if re.search(r"delivery_mutation_allowed\s*:\s*no", text):
        errors.append("distillation does not authorize delivery mutation")

    if errors:
        print("Distillation gate: FAIL")
        for error in errors:
            print(error)
        return 2
    print("Distillation gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
