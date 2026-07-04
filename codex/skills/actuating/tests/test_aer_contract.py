#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
DECISION = (ROOT / "references" / "decision-contract.yaml").read_text(encoding="utf-8")
FIXTURE = json.loads((ROOT / "assets" / "aer-v1.example.json").read_text(encoding="utf-8"))
NORMALIZED = " ".join((SKILL + "\n" + AGENT + "\n" + DECISION).split())


class ActuationEscalationReceiptContractTests(unittest.TestCase):
    def test_aer_v1_fields_are_documented(self) -> None:
        required = [
            "actuation_escalation_receipt:",
            "version: AER-v1",
            "owner_boundary:",
            "repeated_finding_class:",
            "accepted_liabilities:",
            "prior_resolution_mode:",
            "next_resolution_mode:",
            "escalation_trigger:",
            "alternatives_considered:",
            "selected_route:",
            "verifier:",
            "current_artifact_scope:",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_aer_v1_boundary_is_explicit(self) -> None:
        required = [
            "AER-v1 is not review adjudication and not mutation authority",
            "`$seq` may later audit whether this receipt existed",
            "$actuating` owns the active escalation decision",
            "AER-v1 is treated as review finding acceptance or mutation authority",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

    def test_aer_v1_fixture_carries_joinable_liability(self) -> None:
        receipt = FIXTURE["actuation_escalation_receipt"]
        self.assertEqual(receipt["version"], "AER-v1")
        self.assertEqual(receipt["next_resolution_mode"], "refactor-kernel")
        liability = receipt["accepted_liabilities"][0]
        for key in ["cas_finding_id", "finding_fingerprint", "review_fold_ref", "liability"]:
            with self.subTest(key=key):
                self.assertIn(key, liability)
        for key in ["branch", "head_sha", "target_fingerprint"]:
            with self.subTest(key=key):
                self.assertIn(key, receipt["current_artifact_scope"])


if __name__ == "__main__":
    unittest.main()
