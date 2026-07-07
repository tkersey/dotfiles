#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
DECISION = (ROOT / "references" / "decision-contract.yaml").read_text(encoding="utf-8")
TERMINAL = (ROOT / "references" / "terminal-closure-gate.md").read_text(encoding="utf-8")
PRE_MUTATION = (ROOT / "references" / "pre-mutation-interlock.md").read_text(encoding="utf-8")
FIXTURE = json.loads((ROOT / "assets" / "aer-v1.example.json").read_text(encoding="utf-8"))
NORMALIZED = " ".join((SKILL + "\n" + AGENT + "\n" + DECISION + "\n" + TERMINAL + "\n" + PRE_MUTATION).split())


class ActuationContractTests(unittest.TestCase):
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

    def test_removed_controller_path_is_not_active(self) -> None:
        required = [
            "The old transaction-controller/APMA path is not active",
            "blocked-unsupported-controller",
            "Do not hand-author APMA-v1",
            "No actuation authority is claimed",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

    def test_fusion_and_goal_focus_contracts_are_documented(self) -> None:
        for token in ["FUSION-v1", "fusion_receipt:", "primary_goal_stable", "child_claimed_parent_completion", "goal_focus"]:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

    def test_versions_and_fingerprint_are_aligned(self) -> None:
        self.assertIn('version: "7.1.0"', SKILL)
        self.assertIn("actuating-v7.1-loop-receipts-focus-fusion-rko-v1", DECISION)

    def test_aer_v1_fixture_carries_joinable_liabilities(self) -> None:
        receipt = FIXTURE["actuation_escalation_receipt"]
        self.assertEqual(receipt["version"], "AER-v1")
        self.assertEqual(receipt["next_resolution_mode"], "refactor-kernel")
        self.assertGreaterEqual(len(receipt["accepted_liabilities"]), 2)
        liability = receipt["accepted_liabilities"][0]
        for key in ["cas_finding_id", "finding_fingerprint", "review_fold_ref", "liability"]:
            with self.subTest(key=key):
                self.assertIn(key, liability)
        for key in ["branch", "head_sha", "target_fingerprint"]:
            with self.subTest(key=key):
                self.assertIn(key, receipt["current_artifact_scope"])


if __name__ == "__main__":
    unittest.main()
