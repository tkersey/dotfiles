#!/usr/bin/env python3
"""Standalone structural/semantic gate for MRPC-v1."""

from __future__ import annotations
import json
from pathlib import Path
import sys

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: mrpc_gate.py <mrpc.json>", file=sys.stderr)
        return 1
    try:
        value = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"MRPC gate: FAIL\ninvalid JSON: {exc}")
        return 1
    body = value.get("minimal_review_patch_certificate", {})
    errors: list[str] = []
    if body.get("certificate_version") != "MRPC-v1":
        errors.append("certificate_version")
    for field in [
        "certificate_id", "stage", "run_id", "immutable_base",
        "counterexample_basis", "candidate_tournament",
        "selected_candidate", "ablation", "gate",
    ]:
        if body.get(field) in (None, "", []):
            errors.append(field)
    metrics = body.get("metrics", {})
    if metrics.get("orphan_edit_atoms"):
        errors.append("orphan_edit_atoms")
    stage = body.get("stage")
    gate = body.get("gate", {})
    if stage == "apply-certified" and gate.get("apply_allowed") is not True:
        errors.append("apply_gate")
    if stage == "final-certified" and gate.get("commit_allowed") is not True:
        errors.append("commit_gate")
    if stage == "committed" and gate.get("push_allowed") is not True:
        errors.append("push_gate")
    if errors:
        print("MRPC gate: FAIL")
        for error in errors:
            print(error)
        return 2
    print("MRPC gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
