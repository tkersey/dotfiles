#!/usr/bin/env python3
"""Lightweight gate for review_governor_record artifacts.

This avoids PyYAML and checks for required textual keys so it can run in
minimal Codex environments.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    r"review_governor_record\s*:",
    r"record_version\s*:\s*RGR-v1",
    r"artifact_state\s*:",
    r"sensor_input\s*:",
    r"state_estimate\s*:",
    r"candidate_routes\s*:",
    r"negative_memory\s*:",
    r"selected_route\s*:",
    r"outcome_metrics\s*:",
    r"gate\s*:",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: rgr_gate.py <review-governor-record.yml>", file=sys.stderr)
        return 2

    text = Path(argv[1]).read_text(encoding="utf-8")
    missing = [pat for pat in REQUIRED if re.search(pat, text) is None]
    if missing:
        print("RGR gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    if re.search(r"active_exclusion_match\s*:\s*yes", text) and re.search(r"handoff_allowed\s*:\s*yes", text):
        print("RGR gate: FAIL")
        print("active negative exclusion cannot allow handoff")
        return 1

    if re.search(r"local_patch_allowed\s*:\s*no", text) and re.search(r"route\s*:\s*mutate-existing-owner", text):
        print("RGR gate: FAIL")
        print("cybernetic local_patch_allowed=no conflicts with mutate-existing-owner")
        return 1

    print("RGR gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
