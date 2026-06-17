#!/usr/bin/env python3
"""Lightweight gate for RGR-V2-MUTATION-PERMIT artifacts.

This avoids PyYAML and checks for required textual keys so it can run in
minimal Codex environments.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    r"RGR-V2-MUTATION-PERMIT\s*:",
    r"permit_version\s*:\s*RGR-MP-v1",
    r"artifact_state\s*:",
    r"cluster_id\s*:",
    r"same_cluster_count\s*:",
    r"selected_route\s*:",
    r"mutate_existing_owner_as_implementation_detail\s*:\s*(yes|no)",
    r"production_embargo\s*:",
    r"expected_production_net\s*:\s*(negative|zero|positive|unknown)",
    r"positive_net_warrant\s*:",
    r"owner_coarseness_gate\s*:",
    r"owner_too_coarse\s*:\s*(yes|no|unknown)",
    r"boundary_inventory\s*:",
    r"missing_boundary_artifact\s*:\s*(yes|no|unknown)",
    r"negative_route_gate\s*:",
    r"query_or_map\s*:\s*(yes|no)",
    r"ledger_cli\s*:\s*ledger",
    r"store\s*:\s*\.ledger/negative-ledger\.jsonl",
    r"command\s*:\s*.*ledger map",
    r"exit_code\s*:\s*(0|2|3)",
    r"ledger_available\s*:\s*(yes|no)",
    r"active_exclusion_match\s*:\s*(yes|no|null)",
    r"proof_matrix_gate\s*:",
    r"family_matrix_present\s*:\s*(yes|no)",
    r"one_test_per_wound\s*:\s*(yes|no)",
    r"forbidden_actions\s*:",
    r"permitted_scope\s*:",
    r"handoff_allowed\s*:\s*(yes|no)",
]

def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text) is not None

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: mutation_permit_gate.py <mutation-permit.yml>", file=sys.stderr)
        return 2

    text = Path(argv[1]).read_text(encoding="utf-8")
    missing = [pat for pat in REQUIRED if not has(pat, text)]
    if missing:
        print("Mutation permit gate: FAIL")
        for pat in missing:
            print(f"missing pattern: {pat}")
        return 1

    if has(r"selected_route\s*:\s*mutate-existing-owner", text):
        print("Mutation permit gate: FAIL")
        print("mutate-existing-owner is not a selectable route after recurrence")
        return 1

    if has(r"mutate_existing_owner_as_implementation_detail\s*:\s*yes", text) and not has(r"selected_route\s*:\s*normal-form-decision", text):
        print("Mutation permit gate: FAIL")
        print("mutate-existing-owner implementation detail requires selected_route: normal-form-decision")
        return 1

    if has(r"expected_production_net\s*:\s*positive", text) and has(r"positive_net_warrant\s*:\s*none", text):
        print("Mutation permit gate: FAIL")
        print("positive production net requires warrant")
        return 1

    if (has(r"owner_too_coarse\s*:\s*yes", text) or has(r"owner_too_coarse\s*:\s*unknown", text)) and has(r"decision\s*:\s*continue_owner", text):
        print("Mutation permit gate: FAIL")
        print("too-coarse or unknown owner cannot continue_owner")
        return 1

    if has(r"query_or_map\s*:\s*no", text):
        print("Mutation permit gate: FAIL")
        print("mutation permit requires negative-ledger query_or_map: yes")
        return 1

    if has(r"ledger_available\s*:\s*no", text) or has(r"exit_code\s*:\s*3", text):
        print("Mutation permit gate: FAIL")
        print("mutation permit requires available ledger map evidence")
        return 1

    if has(r"one_test_per_wound\s*:\s*yes", text) and has(r"family_matrix_present\s*:\s*no", text):
        print("Mutation permit gate: FAIL")
        print("one-test-per-wound without family matrix is blocked")
        return 1

    if has(r"handoff_allowed\s*:\s*no", text):
        print("Mutation permit gate: FAIL")
        print("handoff_allowed: no")
        return 1

    print("Mutation permit gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
