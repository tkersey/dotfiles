#!/usr/bin/env python3
"""Structural consistency gate for RGR-v3."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    r"review_governor_record\s*:",
    r"record_version\s*:\s*RGR-v3",
    r"review_charter\s*:",
    r"finding_liabilities\s*:",
    r"normal_form_register\s*:",
    r"owner_pressure\s*:",
    r"production_net_gate\s*:",
    r"governor_fuse\s*:",
    r"negative_route_gate\s*:",
    r"proof_matrix_gate\s*:",
    r"selected_route\s*:",
    r"gate\s*:",
]

def has(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.M) is not None

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: rgr_gate.py <rgr.yml>", file=sys.stderr)
        return 1
    text = Path(argv[1]).read_text(encoding="utf-8")
    errors = [f"missing:{pattern}" for pattern in REQUIRED if not has(text, pattern)]

    if has(text, r"same_family_after_normal_form\s*:\s*yes") and not has(text, r"fuse_state\s*:\s*tripped"):
        errors.append("same-family recurrence after normal form must trip fuse")
    if has(text, r"status\s*:\s*falsified") and has(text, r"route\s*:\s*normal-form-decision"):
        errors.append("falsified normal form cannot select another ordinary normal form")
    if has(text, r"fuse_state\s*:\s*tripped") and has(text, r"implementation_handoff_allowed\s*:\s*yes"):
        allowed = any(has(text, rf"route\s*:\s*{route}") for route in (
            "delete-collapse-canonicalize",
            "review-distillation-mode",
            "boundary-redesign",
            "distilled-normal-form",
        ))
        if not allowed:
            errors.append("tripped fuse handoff uses prohibited route")
    if has(text, r"relation\s*:\s*(adjacent_preexisting|reviewer_preference|unknown)") and has(text, r"mutation_allowed\s*:\s*yes"):
        errors.append("non-liable finding cannot authorize mutation")

    if errors:
        print("RGR gate: FAIL")
        for error in errors:
            print(error)
        return 2
    print("RGR gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
