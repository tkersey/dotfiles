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
    r"record_version\s*:\s*RGR-v2",
    r"artifact_state\s*:",
    r"sensor_input\s*:",
    r"state_estimate\s*:",
    r"owner_coarseness_gate\s*:",
    r"boundary_inventory\s*:",
    r"candidate_routes\s*:",
    r"negative_memory\s*:",
    r"mutation_permit\s*:",
    r"selected_route\s*:",
    r"proof_matrix_gate\s*:",
    r"production_embargo\s*:",
    r"outcome_metrics\s*:",
    r"gate\s*:",
]

def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text) is not None

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: rgr_gate.py <review-governor-record.yml>", file=sys.stderr)
        return 2

    text = Path(argv[1]).read_text(encoding="utf-8")
    missing = [pat for pat in REQUIRED if not has(pat, text)]
    if missing:
        print("RGR gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    if has(r"same_cluster_count\s*:\s*[2-9]", text) and has(r"emitted\s*:\s*no", text):
        print("RGR gate: FAIL")
        print("same-cluster recurrence requires mutation permit before mutation")
        return 1

    if has(r"same_cluster_count\s*:\s*[2-9]", text) and has(r"selected_route:\s*\n\s*route\s*:\s*mutate-existing-owner", text):
        print("RGR gate: FAIL")
        print("same-cluster recurrence cannot select mutate-existing-owner directly")
        return 1

    if has(r"production_embargo\s*:\s*fail", text):
        print("RGR gate: FAIL")
        print("production embargo failed")
        return 1

    if has(r"owner_coarseness_gate\s*:\s*fail", text):
        print("RGR gate: FAIL")
        print("owner coarseness gate failed")
        return 1

    if has(r"negative_route_gate\s*:\s*fail", text):
        print("RGR gate: FAIL")
        print("negative route gate failed")
        return 1

    if has(r"proof_matrix_gate\s*:\s*fail", text):
        print("RGR gate: FAIL")
        print("proof matrix gate failed")
        return 1

    if has(r"query_or_map\s*:\s*no", text) and has(r"same_cluster_count\s*:\s*[2-9]", text):
        print("RGR gate: FAIL")
        print("same-cluster recurrence requires operational negative-ledger query/map")
        return 1

    print("RGR gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
