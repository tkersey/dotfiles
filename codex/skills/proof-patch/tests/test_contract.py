#!/usr/bin/env -S uv run python
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
NORMALIZED_AGENT = " ".join(AGENT.split())


class ProofPatchContractTests(unittest.TestCase):
    def test_loop_governance_fields_are_required(self) -> None:
        fields = [
            "## Loop governance",
            "- ALSR-v1:",
            "- HYL-v1:",
            "- latest HSR-v1:",
            "- selected loop:",
            "- fused/unfused:",
            "- verifier:",
            "- stop rule:",
            "- terminal fold:",
            "- ATCG-v1:",
            "- residual loop risk:",
        ]
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, SKILL)

    def test_review_closure_fields_are_required(self) -> None:
        fields = [
            "## Review closure",
            "- CAS review source:",
            "- review-fold disposition:",
            "- resolve pass:",
            "- accepted liabilities:",
            "- no-code dispositions:",
            "- clean normalized CAS runs:",
            "- cached CAS receipts counted as fresh: no",
        ]
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, SKILL)

    def test_parallelism_fields_are_required(self) -> None:
        fields = [
            "## Parallelism",
            "- mode:",
            "- safe frontier:",
            "- subagents used:",
            "- fan-in reducer:",
            "- accepted/rejected results:",
            "- integration order:",
            "- CAS clean-run reset:",
        ]
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, SKILL)

    def test_completion_and_publication_boundaries_are_explicit(self) -> None:
        required_phrases = [
            "direct-action fused exemption",
            "Do not claim completion unless ATCG-v1 permits it.",
            "Do not count cached CAS receipts as fresh clean CAS runs.",
            "Do not publish, update PR state, resolve GitHub threads",
            "$ship` owns that boundary",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, SKILL)

    def test_agent_prompt_mentions_new_receipt_surfaces(self) -> None:
        required_phrases = [
            "loop governance receipts",
            "review closure",
            "parallelism",
            "direct-action fused exemption",
            "never count cached CAS receipts as fresh clean runs",
            "do not claim completion unless ATCG-v1 permits it",
            "Escalate to $ship only",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, NORMALIZED_AGENT)


if __name__ == "__main__":
    unittest.main()
