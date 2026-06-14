#!/usr/bin/env python3
"""Lightweight gate for resolve_review_wave_packet artifacts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_PATTERNS = [
    r"resolve_review_wave_packet\s*:",
    r"packet_version\s*:\s*RRW-v1",
    r"resolve_run_id\s*:",
    r"artifact_state_id\s*:",
    r"review_wave\s*:",
    r"route_receipts\s*:",
    r"rcp_packets\s*:",
    r"rdp_packets\s*:",
    r"negative_evidence\s*:",
    r"negative_route_exclusion_cards\s*:",
    r"universalist_checks\s*:",
    r"falsification_rules\s*:",
    r"gate\s*:",
    r"route_receipts_complete\s*:\s*(pass|fail)",
    r"negative_evidence_complete\s*:\s*(pass|fail|not-required)",
    r"negative_route_gate\s*:\s*(pass|fail|not-required)",
    r"rcp_required_packets_present\s*:\s*(pass|fail|not-required)",
    r"distillation_required_packets_present\s*:\s*(pass|fail|not-required)",
    r"universalist_checks_complete\s*:\s*(pass|fail|not-required)",
    r"implementation_handoff_allowed\s*:\s*(yes|no)",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: route_wave_gate.py <route-wave-file>", file=sys.stderr)
        return 2

    text = Path(argv[1]).read_text(encoding="utf-8")
    missing = [pat for pat in REQUIRED_PATTERNS if not re.search(pat, text)]
    if missing:
        print("Route-wave gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    fail_fields = [
        r"route_receipts_complete\s*:\s*fail",
        r"negative_evidence_complete\s*:\s*fail",
        r"negative_route_gate\s*:\s*fail",
        r"rcp_required_packets_present\s*:\s*fail",
        r"distillation_required_packets_present\s*:\s*fail",
        r"universalist_checks_complete\s*:\s*fail",
        r"rent_paid_or_not_applicable\s*:\s*fail",
        r"implementation_handoff_allowed\s*:\s*no",
    ]
    for pat in fail_fields:
        if re.search(pat, text):
            print("Route-wave gate: FAIL")
            print(f"failing gate field: {pat}")
            return 1

    print("Route-wave gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
