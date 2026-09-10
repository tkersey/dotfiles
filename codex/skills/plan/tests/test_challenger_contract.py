"""Source-contract regressions only; these tests do not run or judge a model.

Run: uv run codex/skills/plan/tests/test_challenger_contract.py
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return " ".join((ROOT / path).read_text(encoding="utf-8").split())


class ChallengerContractTests(unittest.TestCase):
    def test_material_decision_not_incumbent_confidence_owns_the_gate(self):
        for path in ("SKILL.md", "references/policy-synthesis-fixed-point.md"):
            with self.subTest(path=path):
                value = text(path)
                self.assertIn("not fixed by accepted source authority", value)
                self.assertIn("strongest non-obvious admissible private challenger", value)
                self.assertIn("Confidence in the incumbent", value)
                self.assertNotIn("skip alternative generation for already-dispositive work", value)
        self.assertIn("every required challenger is dispositioned",
                      text("references/policy-synthesis-fixed-point.md"))

    def test_reuse_and_mechanical_exemption_preserve_source_authority(self):
        value = text("references/policy-synthesis-fixed-point.md")
        for rule in (
            "existing Metanoetic trigger also requires the challenge",
            "Mechanical realization of source-fixed decisions requires no additional challenger",
            "source reread and invariant challenge still apply",
            "A contradiction in fixed authority returns to governance, not unauthorized redesign",
            "Adoption is not required",
            "Reuse an equivalent challenge already evaluated over the same unchanged decision surface",
        ):
            self.assertIn(rule, value)

    def test_machine_contract_retains_both_positive_and_negative_boundaries(self):
        contract = json.loads((ROOT / "references/decision-contract.json").read_text())
        contract = contract["skill_decision_contract"]
        self.assertEqual(contract["contract_version"], "SKDC-v1")
        clause = next(c for c in contract["clauses"] if c["clause_id"] == "PLAN-REFINEMENT-001")
        self.assertIn("material non-source-fixed decisions and live Metanoetic triggers receive a dispositioned challenger",
                      clause["success_signals"])
        self.assertIn("mechanical source-fixed realization needs no additional challenger",
                      clause["success_signals"])
        self.assertIn("confidence in the incumbent or no recognized alternative waives a required challenge",
                      clause["failure_signals"])
        self.assertIn("equivalent challenges reused", clause["success_signals"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
