#!/usr/bin/env python3
"""Structural gate for counterexample_contract / CEC-v1."""

from __future__ import annotations
import re, sys
from pathlib import Path

REQUIRED = [
    r"counterexample_contract\s*:",
    r"contract_version\s*:\s*CEC-v1",
    r"contract_id\s*:",
    r"frozen_delivery_base\s*:",
    r"branch_liabilities\s*:",
    r"non_branch_liabilities\s*:",
    r"counterexample_families\s*:",
    r"proof_matrix\s*:",
    r"gate\s*:",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: counterexample_contract_gate.py <cec.yml>", file=sys.stderr)
        return 1
    text = Path(argv[1]).read_text(encoding="utf-8")
    errors = [f"missing:{pat}" for pat in REQUIRED if re.search(pat, text, re.M) is None]
    if re.search(r"non_branch_liabilities\s*:.*include_in_contract", text, re.S):
        errors.append("non-branch liability included in contract")
    if re.search(r"all_findings_classified\s*:\s*fail", text):
        errors.append("not all findings classified")
    if errors:
        print("Counterexample contract gate: FAIL")
        for error in errors:
            print(error)
        return 2
    print("Counterexample contract gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
