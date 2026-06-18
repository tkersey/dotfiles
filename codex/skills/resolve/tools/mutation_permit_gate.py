#!/usr/bin/env python3
"""Structural consistency gate for RGR-V3-MUTATION-PERMIT."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    r"RGR-V3-MUTATION-PERMIT\s*:",
    r"permit_version\s*:\s*RGR-MP-v2",
    r"finding_liability\s*:",
    r"normal_form\s*:",
    r"governor_fuse\s*:",
    r"selected_route\s*:",
    r"owner_pressure\s*:",
    r"production_net_gate\s*:",
    r"negative_route_gate\s*:",
    r"proof_matrix_gate\s*:",
    r"distillation\s*:",
    r"surface_budget\s*:",
    r"handoff_allowed\s*:\s*(yes|no)",
]

def has(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.M) is not None

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: mutation_permit_gate.py <permit.yml>", file=sys.stderr)
        return 1
    text = Path(argv[1]).read_text(encoding="utf-8")
    errors = [f"missing:{pattern}" for pattern in REQUIRED if not has(text, pattern)]

    if has(text, r"mutation_allowed\s*:\s*no") and has(text, r"handoff_allowed\s*:\s*yes"):
        errors.append("liability gate forbids mutation")
    if has(text, r"status\s*:\s*falsified") and has(text, r"route\s*:\s*normal-form-decision"):
        errors.append("falsified normal form cannot be retried")
    if has(text, r"prior_normal_form_falsified\s*:\s*yes"):
        if not has(text, r"capture_created\s*:\s*yes"):
            errors.append("falsified normal form requires ledger capture")
        if not has(text, r"route_changed_at_leverage_level\s*:\s*yes"):
            errors.append("falsified normal form requires leverage-level route change")
    if has(text, r"fuse_state\s*:\s*tripped"):
        if has(text, r"route\s*:\s*(normal-form-decision|mutate-existing-owner)"):
            errors.append("tripped fuse prohibits ordinary normal form/local owner route")
        if has(text, r"change_kind\s*:\s*(predicate_accretion|helper_accretion|test_accretion)"):
            errors.append("tripped fuse prohibits accretive change kind")
        distill_ok = has(text, r"gate\s*:\s*pass") or has(text, r"route\s*:\s*(delete-collapse-canonicalize|boundary-redesign)")
        if not distill_ok:
            errors.append("tripped fuse requires distillation/deletion/boundary route")
    if has(text, r"pressure_exceeded\s*:\s*yes") and has(text, r"clearance_authority\s*:\s*measured_below_budget"):
        errors.append("owner pressure exceeded but clearance says below budget")
    if has(text, r"expected_production_net\s*:\s*positive"):
        if has(text, r"positive_net_warrant\s*:\s*none"):
            errors.append("positive net requires warrant")
        if has(text, r"change_kind\s*:\s*(predicate_accretion|helper_accretion|test_accretion)") and has(text, r"fuse_state\s*:\s*tripped"):
            errors.append("positive accretion invalid after fuse trip")
    if has(text, r"active_exclusion_match\s*:\s*yes") and has(text, r"handoff_allowed\s*:\s*yes"):
        errors.append("active negative exclusion cannot allow handoff")
    if has(text, r"one_test_per_wound\s*:\s*yes") and not has(text, r"family_matrix_present\s*:\s*yes"):
        errors.append("one-test-per-wound requires family matrix")
    if has(text, r"handoff_allowed\s*:\s*no"):
        errors.append("handoff is not allowed")

    if errors:
        print("Mutation permit gate: FAIL")
        for error in errors:
            print(error)
        return 2
    print("Mutation permit gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
