#!/usr/bin/env -S uv run python
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "actuation_refactor_kernel_gate.py"
ASSETS = ROOT / "assets"
SPEC = importlib.util.spec_from_file_location("actuation_refactor_kernel_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ActuationRefactorKernelGateTests(unittest.TestCase):
    def decision(self, name: str = "aer-v1.example.json"):
        return json.loads((ASSETS / name).read_text())

    def outcome(self, name: str = "rko-v1.effective.example.json"):
        return json.loads((ASSETS / name).read_text())

    def test_refactor_kernel_decision_fixture_passes(self) -> None:
        report = MODULE.validate_decision(self.decision())["refactor_kernel_decision_gate"]
        self.assertEqual(report["verdict"], "pass")
        self.assertEqual(report["selected_route"], "refactor-kernel")
        self.assertEqual(report["liability_count"], 2)

    def test_decision_blocks_hidden_kernel_without_route(self) -> None:
        value = self.decision()
        receipt = value["actuation_escalation_receipt"]
        receipt["selected_route"] = "minimal-fix"
        report = MODULE.validate_decision(value)["refactor_kernel_decision_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("refactor-kernel:selected_route-and-next_resolution_mode-required", report["errors"])

    def test_decision_requires_joinable_liabilities(self) -> None:
        value = self.decision()
        value["actuation_escalation_receipt"]["accepted_liabilities"][0].pop("review_fold_ref")
        report = MODULE.validate_decision(value)["refactor_kernel_decision_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold_ref:missing", report["errors"])

    def test_decision_rejects_missing_required_alternatives(self) -> None:
        value = self.decision()
        value["actuation_escalation_receipt"]["alternatives_considered"] = ["minimal-fix"]
        report = MODULE.validate_decision(value)["refactor_kernel_decision_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("alternatives_considered:branch-race:missing", report["errors"])
        self.assertIn("alternatives_considered:remediation-plan:missing", report["errors"])

    def test_decision_rejects_duplicate_liabilities(self) -> None:
        value = self.decision()
        liabilities = value["actuation_escalation_receipt"]["accepted_liabilities"]
        liabilities[1] = dict(liabilities[0])
        report = MODULE.validate_decision(value)["refactor_kernel_decision_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("accepted_liabilities[1]:duplicate", report["errors"])

    def test_outcome_fixture_passes_and_scores(self) -> None:
        report = MODULE.validate_outcome(self.outcome(), self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(report["verdict"], "pass")
        self.assertEqual(report["assessment"], "effective")
        self.assertGreaterEqual(report["effectiveness_score"], 2)

    def test_outcome_requires_joinable_decision(self) -> None:
        report = MODULE.validate_outcome(self.outcome())["refactor_kernel_outcome_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("decision_ref:decision-required", report["errors"])

    def test_outcome_requires_issued_at(self) -> None:
        value = self.outcome()
        value["refactor_kernel_outcome"].pop("issued_at")
        report = MODULE.validate_outcome(value, self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("issued_at:missing", report["errors"])

    def test_outcome_blocks_graph_bypass(self) -> None:
        value = self.outcome()
        body = value["refactor_kernel_outcome"]
        body["governance"]["graph_bypass"] = "yes"
        body["governance"]["mutations_without_graph_control_receipt"] = 53
        report = MODULE.validate_outcome(value, self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("governance.graph_bypass:yes", report["errors"])
        self.assertIn("governance.mutations_without_graph_control_receipt:nonzero", report["errors"])

    def test_effective_outcome_cannot_hide_new_liabilities(self) -> None:
        value = self.outcome()
        value["refactor_kernel_outcome"]["review_after"]["new_liabilities"] = 1
        report = MODULE.validate_outcome(value, self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("assessment:effective-with-new-liabilities", report["errors"])

    def test_effective_outcome_requires_local_proof_evidence(self) -> None:
        value = self.outcome()
        value["refactor_kernel_outcome"]["local_proof"]["passed"] = []
        report = MODULE.validate_outcome(value, self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("assessment:effective-without-local-proof", report["errors"])

    def test_outcome_requires_governance_fields(self) -> None:
        value = self.outcome()
        value["refactor_kernel_outcome"]["governance"] = {}
        report = MODULE.validate_outcome(value, self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("governance.graph_bypass:missing", report["errors"])
        self.assertIn("governance.mutations_without_graph_control_receipt:missing", report["errors"])

    def test_make_outcome_binds_decision_scope(self) -> None:
        context = {
            "head_after": "def456",
            "patch_calls": 4,
            "files_changed": 3,
            "covered_liabilities": 2,
            "local_proof": {"passed": ["zig build test"], "failed": []},
            "review_after": {"new_liabilities": 0, "clean_runs": 3, "blocked_reason": ""},
            "closure_state": "complete",
            "assessment": "effective",
            "governance": {"graph_bypass": "no", "mutations_without_graph_control_receipt": 0},
        }
        outcome = MODULE.make_outcome(context, self.decision())
        body = outcome["refactor_kernel_outcome"]
        self.assertEqual(body["decision_ref"], "AER-v1:ACT-example-001")
        self.assertEqual(body["head_before"], "head456")
        report = MODULE.validate_outcome(outcome, self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(report["verdict"], "pass")

    def test_cli_check_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.json"
            code = MODULE.main([
                "check-outcome",
                "--outcome",
                str(ASSETS / "rko-v1.effective.example.json"),
                "--decision",
                str(ASSETS / "aer-v1.example.json"),
                "--out",
                str(out),
            ])
            self.assertEqual(code, 0)
            body = json.loads(out.read_text())["refactor_kernel_outcome_gate"]
            self.assertEqual(body["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()
