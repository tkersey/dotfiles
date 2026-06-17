#!/usr/bin/env python3
"""Lightweight gate for spec_governance_receipt artifacts.

Avoids PyYAML; checks required textual keys.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    r"spec_governance_receipt\s*:",
    r"receipt_version\s*:\s*SGR-v1",
    r"phase_presence\s*:",
    r"evidence_brief\s*:\s*(yes|no)",
    r"decision_packet\s*:\s*(yes|no)",
    r"gate_result\s*:\s*(yes|no)",
    r"invariant_challenge\s*:\s*(yes|no)",
    r"fresh_eyes\s*:\s*(yes|no)",
    r"spec_lint\s*:\s*(yes|no)",
    r"execution_handoff\s*:\s*(yes|no)",
    r"gate\s*:",
    r"challenge\s*:",
    r"fresh_eyes\s*:",
    r"lint\s*:",
    r"execution_control\s*:",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: sgr_gate.py <spec-file-or-receipt>", file=sys.stderr)
        return 2

    text = Path(argv[1]).read_text(encoding="utf-8")
    missing = [pat for pat in REQUIRED if not re.search(pat, text)]
    if missing:
        print("SGR gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    if re.search(r"handoff_allowed\s*:\s*yes", text):
        for pat in [
            r"evidence_brief\s*:\s*yes",
            r"decision_packet\s*:\s*yes",
            r"gate_result\s*:\s*yes",
            r"invariant_challenge\s*:\s*yes",
            r"fresh_eyes\s*:\s*yes",
            r"spec_lint\s*:\s*yes",
            r"execution_handoff\s*:\s*yes",
        ]:
            if not re.search(pat, text):
                print("SGR gate: FAIL")
                print(f"handoff allowed but missing required phase: {pat}")
                return 1

    print("SGR gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
