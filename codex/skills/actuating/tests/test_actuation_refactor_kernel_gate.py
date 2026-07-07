#!/usr/bin/env -S uv run python
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "actuation_refactor_kernel_gate.py"
ASSETS = ROOT / "assets"
SPEC = importlib.util.spec_from_file_location("actuation_refactor_kernel_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RefactorKernelGateTests(unittest.TestCase):
    def decision(self):
        return json.loads((ASSETS / "aer-v1.example.json").read_text())

    def outcome(self):
        return json.loads((ASSETS / "rko-v1.effective.example.json").read_text())

    def test_valid_decision_passes(self) -> None:
        result = MODULE.validate_decision(self.decision())["refactor_kernel_decision_gate"]
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["selected_route"], "refactor-kernel")
        self.assertEqual(result["liability_count"], 2)

    def test_decision_requires_named_owner_boundary(self) -> None:
        value = self.decision()
        value["actuation_escalation_receipt"]["owner_boundary"] = "unknown"
        result = MODULE.validate_decision(value)["refactor_kernel_decision_gate"]
        self.assertEqual(result["verdict"], "fail")
        self.assertIn("owner_boundary:must-name-real-boundary", result["errors"])

    def test_valid_outcome_passes_with_decision(self) -> None:
        result = MODULE.validate_outcome(self.outcome(), self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["assessment"], "effective")
        self.assertEqual(result["effectiveness_score"], 2)

    def test_outcome_rejects_graph_bypass_even_with_proof(self) -> None:
        outcome = self.outcome()
        outcome["refactor_kernel_outcome"]["governance"]["graph_bypass"] = "yes"
        result = MODULE.validate_outcome(outcome, self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(result["verdict"], "fail")
        self.assertIn("governance.graph_bypass:yes", result["errors"])

    def test_outcome_must_join_decision(self) -> None:
        outcome = self.outcome()
        outcome["refactor_kernel_outcome"]["decision_ref"] = "AER-v1:other"
        result = MODULE.validate_outcome(outcome, self.decision())["refactor_kernel_outcome_gate"]
        self.assertEqual(result["verdict"], "fail")
        self.assertIn("decision_ref:does-not-reference-AER-run", result["errors"])


if __name__ == "__main__":
    unittest.main()
