#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def run(tool: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(TOOLS / tool), *args],
        check=False,
        text=True,
        capture_output=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        handoff = tmp_path / "handoff.md"
        handoff.write_text(
            """
goal: build ledger
problem_layer: storage
target_user_or_maintainer: maintainer
scope: ledger
non_goals: network sync
locked_decisions: repo local
primary_invariant: cluster-only cannot block
success_criteria: tests pass
proof_bar: zig build test-ledger
compatibility_posture: preserve existing files
rollout_rollback_posture: revert commit
default_assumptions: none
grill_rounds: 1
plan_allowed: true
We are building ledger for maintainers by changing route gating while explicitly not doing network sync, and success means tests pass.
open_questions: none
""",
            encoding="utf-8",
        )
        gate = run("spec_gate.py", "--strict-receipts", str(handoff))
        assert gate.returncode == 0, gate.stdout + gate.stderr
        assert json.loads(gate.stdout)["spec_gate_receipt"]["plan_allowed"] == "yes"

        incomplete = tmp_path / "incomplete.md"
        incomplete.write_text("plan_allowed: true\n", encoding="utf-8")
        gate_fail = run("spec_gate.py", "--strict-receipts", str(incomplete))
        assert gate_fail.returncode == 2

        sgr = tmp_path / "sgr.md"
        sgr.write_text(
            """
## Spec Pipeline Receipt
spec_governance_receipt:
  receipt_version: SGR-v2
  spec_id: spec-1
  mode: gate-only
  profile: balanced
  lane: spec_only
  status: audit-only
  phase_presence:
    gate: yes
  execution_control:
    plan_allowed: yes
    mutation_allowed: no
    execution_handoff: no
""",
            encoding="utf-8",
        )
        sgr_result = run("sgr_gate.py", str(sgr))
        assert sgr_result.returncode == 0, sgr_result.stdout + sgr_result.stderr

    print("spec-pipeline tool tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
