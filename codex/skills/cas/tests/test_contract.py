#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
BOUNDARY = (ROOT / "references" / "review-proof-boundary.md").read_text(
    encoding="utf-8"
)
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
NORMALIZED_CONTRACT = " ".join((SKILL + "\n" + BOUNDARY).split())
NORMALIZED_AGENT = " ".join(AGENT.split())
NORMALIZED_DOCUMENTATION = " ".join(
    (
        SKILL
        + "\n"
        + AGENT
        + "\n"
        + "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "references").rglob("*.md"))
        )
    ).split()
)
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

    def test_cas_states_its_positive_transport_contract(self) -> None:
        required = [
            "starts, waits for, recovers, normalizes, and reports review attempts",
            "attempt lifecycle",
            "tuple identity",
            "normalized verdict facts",
            "stable finding provenance",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED_CONTRACT)

    def test_agent_prompt_mentions_finding_identity_boundary(self) -> None:
        required = [
            "drive tuple-bound review attempts",
            "opaque request identity",
            "finding provenance",
            "normalized transport outcomes",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED_AGENT)

    def test_finding_identity_fixture_carries_join_keys(self) -> None:
        verdict = FINDING_IDENTITY["reviewVerdict"]
        finding = verdict["findings"][0]
        self.assertEqual(verdict["status"], "findings")
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
        for key in ["lane", "laneRole", "contributesToStandardStreak"]:
            with self.subTest(key=key):
                self.assertNotIn(key, finding)

    def test_optional_workflow_binding_is_opaque_request_identity(self) -> None:
        required = [
            "workflowBinding",
            "requestId",
            "requestFingerprint",
            "non-empty strings",
            "returns it unchanged",
            "import-only historical evidence",
            "cas_rer_opaque_request_binding_v1=true",
            "cas_review_history_v2=true",
            "cas_review_scoped_instructions_v1=true",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED_CONTRACT)

    def test_active_cas_contract_contains_no_review_policy_vocabulary(self) -> None:
        forbidden = [
            "selectedLenses",
            "reviewLane",
            "lensContract",
            "laneRole",
            "contributesToStandardStreak",
            "three-clean",
            "clean-streak",
            "footgun-finder",
            "invariant-ace",
            "complexity-mitigator",
            "Repeated-review eligibility",
            "closeout accounting",
            "policy threshold",
            "review-batch authority",
            "Kernel review",
            "Terminal holdout",
        ]
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, NORMALIZED_DOCUMENTATION)

    def test_exhaustive_list_surface_is_canonical_and_complete(self) -> None:
        required = [
            "cas review list --cwd <repo> --base <base> --codex-thread-id <id> --json",
            "complete `CAS-LIST-v2`",
            "`records` and `recordRefs`",
            "`status --latest`",
            "exact action is advertised",
            "never falls back",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED_CONTRACT)

    def test_real_review_wait_budget_is_explicit(self) -> None:
        required = [
            "### Review wait budget",
            "--timeout-ms 1800000",
            "review run",
            "review_session run",
            "start --wait",
            "lane review",
            "Keep lane smoke and smoke-suite waits at `300000`",
            "never start a duplicate review for the tuple",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED_CONTRACT)


if __name__ == "__main__":
    unittest.main()
