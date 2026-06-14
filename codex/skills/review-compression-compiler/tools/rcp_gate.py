#!/usr/bin/env python3
"""Lightweight gate for review_compression_packet artifacts.

This intentionally avoids PyYAML. It checks for required textual keys so it can
run in minimal Codex environments.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_PATTERNS = [
    r"review_compression_packet\s*:",
    r"packet_version\s*:\s*RCP-v1",
    r"packet_id\s*:",
    r"packet_status\s*:\s*(accepted|blocked|not-required)",
    r"artifact_state_id\s*:",
    r"cluster_id\s*:",
    r"selected_normal_form\s*:",
    r"kind\s*:\s*(no-change-proof|validate-only|delete-collapse-canonicalize|refactor-existing-owner|mutate-existing-owner|add-new-surface|blocked)",
    r"owner\s*:",
    r"abstraction_rent\s*:",
    r"rent_status\s*:\s*(paid|unpaid|not-applicable)",
    r"proof_matrix\s*:",
    r"implementation_handoff\s*:",
    r"surface_budget\s*:",
    r"commit_boundary\s*:",
    r"closure_rule\s*:",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: rcp_gate.py <packet-file>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    text = path.read_text(encoding="utf-8")

    missing = [pat for pat in REQUIRED_PATTERNS if not re.search(pat, text)]
    if missing:
        print("RCP gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    # Hard fail for add-new-surface with unpaid rent.
    if re.search(r"kind\s*:\s*add-new-surface", text) and re.search(r"rent_status\s*:\s*unpaid", text):
        print("RCP gate: FAIL")
        print("add-new-surface requires paid abstraction rent")
        return 1

    # Hard fail for accepted packet with unpaid rent.
    if re.search(r"packet_status\s*:\s*accepted", text) and re.search(r"rent_status\s*:\s*unpaid", text):
        print("RCP gate: FAIL")
        print("accepted packet cannot have unpaid abstraction rent")
        return 1

    print("RCP gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
