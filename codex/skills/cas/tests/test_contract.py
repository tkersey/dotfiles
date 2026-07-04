#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
BOUNDARY = (ROOT / "references" / "review-proof-boundary.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
NORMALIZED_CONTRACT = " ".join((SKILL + "\n" + BOUNDARY).split())
NORMALIZED_AGENT = " ".join(AGENT.split())
FINDING_IDENTITY = json.loads(
    (ROOT / "assets" / "finding-identity.example.json").read_text(encoding="utf-8")
)


class CasContractTests(unittest.TestCase):
    def test_per_finding_identity_fields_are_documented(self) -> None:
        required = [
            "## Per-finding identity projection",
            "findingId",
            "findingFingerprint",
            "reviewAttemptId",
            "laneRole",
            "contributesToStandardStreak",
            "reviewThreadId",
            "reviewTurnId",
            "baseSha",
            "headSha",
            "targetFingerprint",
            "titleHash",
            "bodyHash",
            "normalizedLocation",
            "verdictStatus",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_cas_does_not_claim_workflow_authority(self) -> None:
        required = [
            "CAS records evidence.",
            "Workflows certify meaning.",
            "It does not decide whether a finding is accepted",
            "Do not treat per-finding identity as acceptance",
            "Per-finding identity is not acceptance",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED_CONTRACT)

    def test_agent_prompt_mentions_finding_identity_boundary(self) -> None:
        required = [
            "per-finding identity fields",
            "findingId",
            "findingFingerprint",
            "reviewAttemptId",
            "laneRole",
            "caller workflows certify meaning",
            "mutation authority",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED_AGENT)

    def test_finding_identity_fixture_carries_join_keys(self) -> None:
        verdict = FINDING_IDENTITY["reviewVerdict"]
        finding = verdict["findings"][0]
        self.assertEqual(verdict["status"], "findings")
        self.assertEqual(finding["laneRole"], "standard")
        self.assertFalse(finding["contributesToStandardStreak"])
        for key in [
            "findingId",
            "findingFingerprint",
            "reviewAttemptId",
            "reviewThreadId",
            "reviewTurnId",
            "baseSha",
            "headSha",
            "targetFingerprint",
            "titleHash",
            "bodyHash",
            "normalizedLocation",
            "verdictStatus",
        ]:
            with self.subTest(key=key):
                self.assertIn(key, finding)


if __name__ == "__main__":
    unittest.main()
