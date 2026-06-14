#!/usr/bin/env python3
"""Lightweight gate for review_compression_packet artifacts."""

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
    r"negative_evidence\s*:",
    r"query_status\s*:\s*(not-run|no-applicable-negative-evidence|active|stale|reopened|blocked)",
    r"universalist_check\s*:",
    r"considered\s*:\s*(yes|no)",
    r"decision\s*:\s*(use-universalist|not-needed|blocked)",
    r"falsification\s*:",
    r"prior_decision_invalidated\s*:\s*(yes|no)",
    r"selected_normal_form\s*:",
    r"kind\s*:\s*(no-change-proof|validate-only|delete-collapse-canonicalize|refactor-existing-owner|mutate-existing-owner|add-new-surface|distill-from-lab|blocked)",
    r"owner\s*:",
    r"abstraction_rent\s*:",
    r"rent_status\s*:\s*(paid|unpaid|not-applicable)",
    r"proof_matrix\s*:",
    r"implementation_handoff\s*:",
    r"surface_budget\s*:",
    r"commit_boundary\s*:",
    r"route_wave_ref\s*:",
    r"closure_rule\s*:",
]

def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text) is not None

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: rcp_gate.py <packet-file>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    text = path.read_text(encoding="utf-8")

    missing = [pat for pat in REQUIRED_PATTERNS if not has(pat, text)]
    if missing:
        print("RCP gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    if has(r"kind\s*:\s*add-new-surface", text) and has(r"rent_status\s*:\s*unpaid", text):
        print("RCP gate: FAIL")
        print("add-new-surface requires paid abstraction rent")
        return 1

    if has(r"packet_status\s*:\s*accepted", text) and has(r"rent_status\s*:\s*unpaid", text):
        print("RCP gate: FAIL")
        print("accepted packet cannot have unpaid abstraction rent")
        return 1

    if has(r"kind\s*:\s*add-new-surface", text) and has(r"considered\s*:\s*no", text):
        print("RCP gate: FAIL")
        print("add-new-surface requires universalist_check.considered: yes")
        return 1

    if has(r"decision\s*:\s*blocked", text) and has(r"packet_status\s*:\s*accepted", text):
        print("RCP gate: FAIL")
        print("accepted packet cannot have universalist_check.decision: blocked")
        return 1

    if has(r"prior_decision_invalidated\s*:\s*yes", text) and has(r"decision\s*:\s*not-needed", text):
        print("RCP gate: FAIL")
        print("falsified universalist not-needed cannot remain not-needed")
        return 1

    if has(r"negative_capture_candidate\s*:\s*yes", text) and has(r"query_status\s*:\s*not-run", text):
        print("RCP gate: FAIL")
        print("negative capture candidate requires negative-ledger query/map status")
        return 1

    print("RCP gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
