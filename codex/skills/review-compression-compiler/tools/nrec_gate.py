#!/usr/bin/env python3
"""Lightweight gate for negative_route_exclusion_card artifacts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_PATTERNS = [
    r"negative_route_exclusion_card\s*:",
    r"card_version\s*:\s*NREC-v1",
    r"neg_id\s*:",
    r"card_id\s*:",
    r"artifact_state_id\s*:",
    r"cluster_id\s*:",
    r"excluded_route\s*:",
    r"hypothesis\s*:",
    r"attempted_change_or_decision\s*:",
    r"falsifying_evidence\s*:",
    r"applicability\s*:",
    r"current_status\s*:\s*(active|stale|superseded|reopened|unknown)",
    r"exclusion_rule\s*:",
    r"reopening_test\s*:",
    r"next_allowed_routes\s*:",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: nrec_gate.py <nrec-file>", file=sys.stderr)
        return 2

    text = Path(argv[1]).read_text(encoding="utf-8")
    missing = [pat for pat in REQUIRED_PATTERNS if not re.search(pat, text)]
    if missing:
        print("NREC gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    print("NREC gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
