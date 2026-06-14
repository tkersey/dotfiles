#!/usr/bin/env python3
"""Lightweight gate for review_distillation_packet artifacts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_PATTERNS = [
    r"review_distillation_packet\s*:",
    r"packet_version\s*:\s*RDP-v1",
    r"packet_id\s*:",
    r"packet_status\s*:\s*(accepted|blocked)",
    r"delivery_base\s*:",
    r"review_lab\s*:",
    r"counterexample_corpus\s*:",
    r"negative_evidence\s*:",
    r"scar_tissue_inventory\s*:",
    r"universalist_check\s*:",
    r"selected_normal_form\s*:",
    r"abstraction_rent\s*:",
    r"proof_matrix\s*:",
    r"delivery_patch_plan\s*:",
    r"must_not_cherry_pick_lab_commits\s*:\s*true",
    r"dominance_check\s*:",
    r"implementation_handoff\s*:",
    r"route_wave_ref\s*:",
    r"closure_rule\s*:",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: rdp_gate.py <packet-file>", file=sys.stderr)
        return 2

    text = Path(argv[1]).read_text(encoding="utf-8")
    missing = [pat for pat in REQUIRED_PATTERNS if not re.search(pat, text)]
    if missing:
        print("RDP gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    fail_fields = [
        r"rent_status\s*:\s*unpaid",
        r"lab_counterexamples_covered_by_delivery\s*:\s*no",
        r"delivery_surface_smaller_or_warranted\s*:\s*no",
        r"no_unpaid_lab_surface_transplanted\s*:\s*no",
    ]
    for pat in fail_fields:
        if re.search(pat, text):
            print("RDP gate: FAIL")
            print(f"failing field: {pat}")
            return 1

    print("RDP gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
