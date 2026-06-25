#!/usr/bin/env -S uv run --with pyyaml python
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"
EVALS = ROOT / "evals"
sys.path.insert(0, str(TOOLS))

import mode_gate


class ModeAndRoutingTests(unittest.TestCase):
    def load(self, name: str):
        return yaml.safe_load((ASSETS / name).read_text(encoding="utf-8"))

    def test_mode_examples(self) -> None:
        examples = (
            ("codebase-survey.example.yaml", "survey"),
            ("codebase-portfolio.example.yaml", "portfolio"),
            ("codebase-doctrine-audit.example.yaml", "audit"),
            ("codebase-doctrine-delta.example.yaml", "delta"),
        )
        for name, expected in examples:
            with self.subTest(name=name):
                selected, errors, warnings = mode_gate.validate_value(self.load(name))
                self.assertEqual(selected, expected)
                self.assertEqual(errors, [])
                self.assertEqual(warnings, [])

    def test_routing_corpus_has_compound_positives_and_near_misses(self) -> None:
        corpus = json.loads((EVALS / "routing-cases.json").read_text())
        positives = [row for row in corpus["cases"] if row["activate"]]
        negatives = [row for row in corpus["cases"] if not row["activate"]]
        self.assertGreaterEqual(len(positives), 6)
        self.assertGreaterEqual(len(negatives), 6)
        modes = {row.get("mode") for row in positives}
        self.assertEqual(
            modes,
            {"survey", "doctrine", "deep", "refresh", "portfolio", "audit"},
        )
        owners = {row.get("owner") for row in negatives}
        self.assertTrue({"direct", "implementation", "ms"} <= owners)


    def test_root_activation_matches_interface(self) -> None:
        codex_root = ROOT.parents[1]
        agents = (codex_root / "AGENTS.md").read_text(encoding="utf-8")
        interface = yaml.safe_load(
            (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        )
        self.assertTrue(interface["policy"]["allow_implicit_invocation"])
        self.assertIn("- `$codebase-doctrine` — use when the user asks for both", agents)
        self.assertIn("Do not activate for quick onboarding", agents)

    def test_decision_contract_references_close(self) -> None:
        contract = yaml.safe_load(
            (ROOT / "references/decision-contract.yaml").read_text(encoding="utf-8")
        )["skill_decision_contract"]
        self.assertEqual(contract["contract_version"], "SKDC-v1")
        trigger_ids = {row["trigger_id"] for row in contract["triggers"]}
        route_ids = {row["route_id"] for row in contract["routes"]}
        self.assertGreaterEqual(len(trigger_ids), 6)
        self.assertGreaterEqual(len(route_ids), 8)
        for clause in contract["clauses"]:
            self.assertTrue(set(clause["trigger_refs"]) <= trigger_ids)
            self.assertTrue(set(clause["expected_routes"]) <= route_ids)
            self.assertTrue(set(clause["prohibited_routes"]) <= route_ids)
        self.assertEqual(contract["instrumentation"]["decision_receipt"], "required")


if __name__ == "__main__":
    unittest.main()
