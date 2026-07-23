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
CONTRACT = " ".join((SKILL + "\n" + BOUNDARY + "\n" + AGENT).split())
FINDING_IDENTITY = json.loads(
    (ROOT / "assets" / "finding-identity.example.json").read_text(encoding="utf-8")
)


class CasContractTests(unittest.TestCase):
    def test_review_surface_is_run_start_wait_only(self) -> None:
        self.assertIn("cas review <run|start|wait>", SKILL)
        for command in [
            "cas review run",
            "cas review start",
            "cas review wait",
        ]:
            with self.subTest(command=command):
                self.assertIn(command, CONTRACT)

        forbidden = [
            "cas review current",
            "cas review list",
            "cas review import",
            "cas review inspect",
            "cas review validate-record",
            "cas review status",
            "cas review interrupt",
            "cas review lane",
            "cas review receipt",
            "review_session",
            "review-session",
            "--fallback",
            "native-review",
            "CAS-LIST-v2",
            "CAS-RER-v1",
        ]
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, CONTRACT)

    def test_cas_owns_attempt_facts_not_actuating_policy(self) -> None:
        required = [
            "target capture",
            "attempt lifecycle",
            "principal quality",
            "structured tuple-bound verdicts",
            "finding provenance",
            "does not own Actuating's review topology",
            "CAS reports owner facts",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

    def test_opaque_binding_is_preserved_without_semantic_decoding(self) -> None:
        required = [
            "directly to `--workflow-binding-json`",
            "The flag input is not wrapped in a `workflowBinding` object",
            "workflowBinding",
            "requestId",
            "requestFingerprint",
            "two non-empty strings",
            "returns it unchanged under the owner receipt's",
            "does not decode a lens",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

    def test_review_target_capture_is_cas_local(self) -> None:
        for token in [
            "--base",
            "--commit",
            "--uncommitted",
            "This target capture belongs to CAS",
            "not repository mutation or a general Git-subject service",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

    def test_actuating_concurrent_wave_keeps_the_published_subject(self) -> None:
        self.assertIn("post-Ship Actuating wave", CONTRACT)
        self.assertIn("normally this is `--base <bound-base>`", CONTRACT)
        self.assertIn("Never substitute `--uncommitted`", CONTRACT)

    def test_real_review_wait_and_recovery_are_explicit(self) -> None:
        for token in [
            "--timeout-ms 2700000",
            "recover with `wait`",
            "--fresh-attempt <source-bound-reason>",
            "zero semantic credit",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

    def test_structured_verdict_cannot_be_inferred_from_exit_status(self) -> None:
        for token in [
            "reviewVerdict.tupleVerdictExists=true",
            "principalStrength",
            "accountFingerprintReducedProtection",
            "backendClass",
            'principalStrength == "strong"',
            'backendClass == "cas-start-wait"',
            "Process exit status is transport evidence only",
            "Missing structured output is not clean",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

    def test_codex_0145_review_requires_structured_compatibility_capability(self) -> None:
        for token in [
            "cas capabilities --json",
            "cas_capabilities.features.cas_codex_0145_structured_review_v4=true",
            "CAS 0.2.87 through 0.2.92",
            "Stop before `review/start` when the feature is absent",
            "exited_review_mode.review_output",
            "Do not pass `--parent-thread-id` on the 0.145+ route",
            "unique persisted attempt handle",
            "structured non-terminal state",
            "exact review turn before accepting a terminal result",
            "partially materialized `completed` turn",
            "has not emitted its structured exit",
            "attempt's recorded Codex runtime",
            "currently installed runtime is used only for tuple-currentness checks",
            "Process completion and prose remain non-proof",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

    def test_compact_finding_fixture_uses_enclosing_receipt_provenance(self) -> None:
        verdict = FINDING_IDENTITY["reviewVerdict"]
        self.assertEqual(verdict["backendClass"], "cas-start-wait")
        finding = verdict["findings"][0]
        self.assertEqual(
            set(finding),
            {"title", "body", "file", "line", "priority"},
        )
        for key in [
            "reviewThreadId",
            "reviewTurnId",
            "baseSha",
            "headSha",
            "targetFingerprint",
        ]:
            with self.subTest(key=key):
                self.assertIn(key, verdict)

    def test_review_contract_contains_no_retired_policy_or_kernel_artifacts(self) -> None:
        forbidden = [
            "RF-v2",
            "review-resolution/v1",
            "actuation-review-policy",
            "auxiliary-remediation",
            "closure-decision/v1",
            "actuation-kernel-state",
        ]
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, CONTRACT)


if __name__ == "__main__":
    unittest.main()
