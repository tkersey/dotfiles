#!/usr/bin/env python3
"""Structural gate for delivery_patch_recipe / DPR-v1."""

from __future__ import annotations
import re, sys
from pathlib import Path

REQUIRED = [
    r"delivery_patch_recipe\s*:",
    r"recipe_version\s*:\s*DPR-v1",
    r"recipe_id\s*:",
    r"frozen_base\s*:",
    r"counterexample_contract_id\s*:",
    r"selected_boundary\s*:",
    r"selected_route\s*:",
    r"branch_liabilities_included\s*:",
    r"branch_liabilities_excluded\s*:",
    r"falsified_routes_excluded\s*:",
    r"surfaces_to_retire\s*:",
    r"permitted_new_surface\s*:",
    r"forbidden_lab_artifacts\s*:",
    r"expected_surface_delta\s*:",
    r"proof_matrix\s*:",
    r"gate\s*:",
]

def has(text: str, pat: str) -> bool:
    return re.search(pat, text, re.M) is not None

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: delivery_recipe_gate.py <dpr.yml>", file=sys.stderr)
        return 1
    text = Path(argv[1]).read_text(encoding="utf-8")
    errors = [f"missing:{pat}" for pat in REQUIRED if not has(text, pat)]
    if has(text, r"derived_from_contract\s*:\s*fail"):
        errors.append("recipe not derived from contract")
    if has(text, r"falsified_routes_excluded\s*:\s*fail"):
        errors.append("falsified routes not excluded")
    if has(text, r"delivery_mutation_allowed\s*:\s*no"):
        errors.append("recipe does not allow delivery mutation")
    if has(text, r"production_net\s*:\s*bounded_positive") and not has(text, r"surfaces_to_retire\s*:\s*\n\s*-"):
        errors.append("positive production net requires named retired surface or explicit permitted new surface")
    if errors:
        print("Delivery recipe gate: FAIL")
        for error in errors:
            print(error)
        return 2
    print("Delivery recipe gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
