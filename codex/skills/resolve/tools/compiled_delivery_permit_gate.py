#!/usr/bin/env python3
"""Structural gate for RGR-V4-COMPILED-DELIVERY-PERMIT."""

from __future__ import annotations
import re, sys
from pathlib import Path

REQUIRED = [
    r"RGR-V4-COMPILED-DELIVERY-PERMIT\s*:",
    r"permit_version\s*:\s*RGR-CDP-v1",
    r"frozen_delivery_base\s*:",
    r"counterexample_contract_id\s*:",
    r"delivery_patch_recipe_id\s*:",
    r"ablation_certificate_required\s*:\s*yes",
    r"branch_liabilities_included\s*:",
    r"non_branch_liabilities_excluded\s*:",
    r"falsified_routes_excluded\s*:",
    r"selected_route\s*:",
    r"permitted_scope\s*:",
    r"forbidden_actions\s*:",
    r"expected_surface_delta\s*:",
    r"proof_matrix\s*:",
    r"stale_if\s*:",
    r"handoff_allowed\s*:\s*(yes|no)",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: compiled_delivery_permit_gate.py <permit.yml>", file=sys.stderr)
        return 1
    text = Path(argv[1]).read_text(encoding="utf-8")
    errors = [f"missing:{pat}" for pat in REQUIRED if re.search(pat, text, re.M) is None]
    if re.search(r"handoff_allowed\s*:\s*no", text, re.M):
        errors.append("handoff_allowed:no")
    if re.search(r"non_branch_liabilities_excluded\s*:\s*\[\s*\]", text, re.M):
        # Not always an error, but a common smell. Keep as warning only.
        pass
    if errors:
        print("Compiled delivery permit gate: FAIL")
        for error in errors:
            print(error)
        return 2
    print("Compiled delivery permit gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
