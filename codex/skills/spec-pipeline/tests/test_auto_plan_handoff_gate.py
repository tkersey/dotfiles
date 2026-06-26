#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "auto_plan_handoff_gate.py"
ASSETS = ROOT / "assets"


class AutoPlanHandoffGateTests(unittest.TestCase):
    def run_gate(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(TOOL), str(path)], text=True, capture_output=True)

    def test_eligible_fixture_passes(self) -> None:
        result = self.run_gate(ASSETS / "sgr-auto-plan.eligible.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)["auto_plan_handoff_gate"]
        self.assertEqual(payload["verdict"], "pass")
        self.assertEqual(payload["eligible"], "yes")
        self.assertEqual(payload["next_owner"], "$plan")

    def test_do_not_execute_before_blocks(self) -> None:
        result = self.run_gate(ASSETS / "sgr-auto-plan.blocked.json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("execution_handoff.do_not_execute_before:must-be-empty", result.stdout)

    def test_gate_failure_blocks_even_when_declared_eligible(self) -> None:
        data = json.loads((ASSETS / "sgr-auto-plan.eligible.json").read_text())
        data["spec_governance_receipt"]["gate"]["plan_allowed"] = "no"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_gate(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("gate.plan_allowed:expected:yes", result.stdout)
        self.assertIn("eligible=yes-but-predicates-failed", result.stdout)

    def test_gate_only_never_tail_calls(self) -> None:
        data = json.loads((ASSETS / "sgr-auto-plan.eligible.json").read_text())
        data["spec_governance_receipt"]["mode"] = "gate-only"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "gate-only.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_gate(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("mode:expected:full-or-repair", result.stdout)

    def test_markdown_yaml_block_parses(self) -> None:
        text = """# Example\n\n## Spec Pipeline Receipt\n\nspec_governance_receipt:\n  receipt_version: SGR-v2\n  spec_id: SPEC-md\n  mode: full\n  profile: balanced\n  lane: spec_to_plan\n  status: complete\n  authoritative_brief:\n    present: yes\n    drift_detected: no\n  phase_presence:\n    evidence_brief: yes\n    decision_packet: yes\n    gate: yes\n    implementation_spec: yes\n    challenge: yes\n    fresh_eyes: yes\n    lint: yes\n    execution_handoff: yes\n  gate:\n    plan_allowed: yes\n    material_open_questions_remaining: no\n  fresh_eyes:\n    drift_detected: no\n  lint:\n    verdict: pass\n    blocked_handoff: no\n  subagents:\n    open_at_end: 0\n  execution_control:\n    plan_allowed: yes\n    execution_handoff: yes\n  execution_handoff:\n    ready_for_plan: yes\n    next_owner: $plan\n    do_not_execute_before: []\n  auto_plan_handoff:\n    eligible: yes\n    invocation: same_turn_tail_call\n"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "spec.md"
            path.write_text(text, encoding="utf-8")
            result = self.run_gate(path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
