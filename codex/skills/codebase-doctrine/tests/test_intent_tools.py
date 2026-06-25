#!/usr/bin/env -S uv run --with pyyaml python
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"
sys.path.insert(0, str(TOOLS))

import common
import intent_compile
import intent_gate


class IntentToolsTests(unittest.TestCase):
    def load(self, name: str):
        return yaml.safe_load((ASSETS / name).read_text(encoding="utf-8"))

    def test_direct_gate_compiles_deterministically(self) -> None:
        gate = self.load("doctrine-intent-gate.direct.example.yaml")
        kind, errors, _warnings = intent_gate.validate_value(gate, kind="dig")
        self.assertEqual(kind, "dig")
        self.assertEqual(errors, [])
        left = intent_compile.compile_intent(gate)
        right = intent_compile.compile_intent(copy.deepcopy(gate))
        self.assertEqual(left, right)
        kind, errors, _warnings = intent_gate.validate_value(left, kind="cdi")
        self.assertEqual(errors, [])

    def test_grill_gate_closes_exact_gaps(self) -> None:
        gate = self.load("doctrine-intent-gate.grill.example.yaml")
        grill = self.load("grill-decision-packet.example.yaml")
        compiled = intent_compile.compile_intent(gate, grill)
        self.assertEqual(compiled["codebase_doctrine_intent"]["source"]["kind"], "grill")
        self.assertEqual(intent_gate.validate_value(compiled, kind="cdi")[1], [])

    def test_direct_seed_is_fully_validated(self) -> None:
        gate = self.load("doctrine-intent-gate.direct.example.yaml")
        del gate["doctrine_intent_gate"]["direct_intent_seed"]["proof_bar"]
        errors = intent_gate.validate_value(gate, kind="dig")[1]
        self.assertTrue(any("intent_seed.proof_bar:missing" in item for item in errors))

    def test_repository_law_is_not_required_at_intake(self) -> None:
        gate = self.load("doctrine-intent-gate.direct.example.yaml")
        seed = gate["doctrine_intent_gate"]["direct_intent_seed"]
        self.assertNotIn("primary_invariant", seed)
        self.assertIn("primary_correctness_question", seed)
        self.assertEqual(intent_gate.validate_value(gate, kind="dig")[1], [])

    def test_grill_closure_must_bind_handoff_digest(self) -> None:
        gate = self.load("doctrine-intent-gate.grill.example.yaml")
        grill = self.load("grill-decision-packet.example.yaml")
        grill["grill_decision_packet"]["codebase_doctrine_closure"][
            "source_handoff_digest"
        ] = "sha256:wrong"
        with self.assertRaisesRegex(ValueError, "handoff_digest"):
            intent_compile.compile_intent(gate, grill)

    def test_material_gap_cannot_remain_deferred(self) -> None:
        gate = self.load("doctrine-intent-gate.grill.example.yaml")
        grill = self.load("grill-decision-packet.example.yaml")
        closure = grill["grill_decision_packet"]["codebase_doctrine_closure"]
        closure["resolved_gap_ids"].remove("GAP-TARGET")
        closure["deferred_gap_ids"] = ["GAP-TARGET"]
        with self.assertRaisesRegex(ValueError, "invalid grill closure|deferred"):
            intent_compile.compile_intent(gate, grill)


if __name__ == "__main__":
    unittest.main()
