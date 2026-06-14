#!/usr/bin/env python3
"""Lightweight gate for resolve_decision_record artifacts.

Avoids PyYAML; checks for required textual keys.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    r"resolve_decision_record\s*:",
    r"record_version\s*:\s*RDR-v1",
    r"artifact_state\s*:",
    r"review_wave\s*:",
    r"cluster\s*:",
    r"selected_route\s*:",
    r"negative_evidence\s*:",
    r"surface_delta\s*:",
    r"proof_matrix\s*:",
    r"material_improvement\s*:",
    r"gate\s*:",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: rdr_gate.py <resolve-decision-record>", file=sys.stderr)
        return 2
    text = Path(argv[1]).read_text(encoding="utf-8")
    missing = [pat for pat in REQUIRED if re.search(pat, text) is None]
    if missing:
        print("RDR gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    if re.search(r"stop_rule\s*:\s*triggered", text) and re.search(r"implementation_handoff_allowed\s*:\s*yes", text) and re.search(r"selected_route:\s*\n\s*kind:\s*mutate-existing-owner", text) and re.search(r"why_not_point_fix\s*:\s*[\"']?[\"']?\s*(\n|$)", text):
        print("RDR gate: FAIL")
        print("triggered stop rule requires why_not_point_fix")
        return 1

    if re.search(r"active_exclusion_match\s*:\s*yes", text) and re.search(r"handoff_allowed\s*:\s*yes", text):
        print("RDR gate: FAIL")
        print("active negative exclusion cannot allow handoff")
        return 1

    print("RDR gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
