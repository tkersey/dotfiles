#!/usr/bin/env -S uv run python
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
DECISION = (ROOT / "references" / "decision-contract.yaml").read_text(encoding="utf-8")
GOAL = (ROOT.parent / "goal-actuating" / "SKILL.md").read_text(encoding="utf-8")
GOAL_AGENT = (ROOT.parent / "goal-actuating" / "agents" / "openai.yaml").read_text(encoding="utf-8")
NORMALIZED = " ".join((SKILL + "\n" + AGENT + "\n" + DECISION + "\n" + GOAL + "\n" + GOAL_AGENT).split())


class ReviewModeContractTests(unittest.TestCase):
    def test_no_code_review_route_is_explicit_and_terminal(self) -> None:
        self.assertIn("ACT-REVIEW-NO-CODE", DECISION)
        self.assertIn("triage-report", NORMALIZED)
        self.assertIn("mode-terminal", NORMALIZED)

    def test_triage_and_remediation_plan_do_not_require_material_closeout_gates(self) -> None:
        required = [
            "No-code review modes do not require material loop receipts, proof-patch, three clean CAS attempts, or ATCG",
            "ATCG is not required for a `triage` report or `remediation-plan`",
            "triage and remediation-plan stop without material mutation or completion claims",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

    def test_review_closeout_without_tuple_routes_to_cas_acquisition(self) -> None:
        required = [
            "Missing tuple-bound CAS evidence is a `$cas` acquisition node",
            "review-closeout with missing tuple-bound CAS evidence routes to `$cas`",
            "terminal completion still requires tuple-bound",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

    def test_terminal_clean_cas_and_atcg_apply_only_to_material_closeout(self) -> None:
        required = [
            "loop receipts, proof-patch, three clean normalized standard CAS review attempts, and ATCG only for review-closeout or material closure",
            "ACT-REVIEW-NO-CODE terminal=yes means mode-terminal route stop, not ATCG terminal completion",
            "No-code review mode is incorrectly blocked on positive interlock, HSR-v1, proof-patch, or ATCG",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, DECISION)

    def test_existing_review_source_can_feed_no_code_modes(self) -> None:
        required = [
            "Use supplied existing GitHub, human, or CAS findings when present",
            "CAS runs only when no current review source exists or fresh review is explicitly requested",
            "No-code outputs must report review source/currentness",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)


if __name__ == "__main__":
    unittest.main()
