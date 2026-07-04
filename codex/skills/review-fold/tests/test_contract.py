#!/usr/bin/env -S uv run python
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_ROOT = ROOT.parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
CONTRACT = (ROOT / "references" / "decision-contract.yaml").read_text(encoding="utf-8")
REDUCER = (CODEX_ROOT / "agents" / "review-reducer.toml").read_text(encoding="utf-8")
NORMALIZED = " ".join((AGENT + "\n" + REDUCER).split())


class ReviewFoldContractTests(unittest.TestCase):
    def test_rf_v13_schema_has_joinable_source_refs(self) -> None:
        required = [
            "version: RF-v1.3",
            "source_ref:",
            "cas_finding_id",
            "finding_fingerprint",
            "review_attempt_id",
            "review_thread_id",
            "review_turn_id",
            "lane_role: standard|auxiliary|unknown",
            "head_sha",
            "target_fingerprint",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_rf_v13_schema_names_law_model_and_repair_fields(self) -> None:
        required = [
            "law_family",
            "falsified_law",
            "owner_boundary",
            "model_state: intact|local-gap|boundary-gap|unknown",
            "repair_level:",
            "alternatives_considered: []",
            "evidence_refs: []",
            "kernel_pressure:",
            "refactor_trigger:",
            "minimal_fix_regret_risk:",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_high_one_patch_risk_requires_explicit_route(self) -> None:
        required = [
            "When `one_patch_per_comment_risk: high`",
            "refactor-kernel",
            "branch-race",
            "remediation-plan",
            "blocked",
            "explicit owner-boundary exception",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_prompts_request_rf_v13_receipts(self) -> None:
        required = [
            "RF-v1.3",
            "RF-v1.3 compact",
            "cas_finding_id",
            "finding_fingerprint",
            "review_attempt_id",
            "law_family",
            "falsified_law",
            "owner_boundary",
            "repair_level",
            "one_patch_per_comment_risk is high",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

    def test_compact_receipt_floor_preserves_material_fold_observability(self) -> None:
        required = [
            "## Compact receipt floor",
            "RF-v1.3 compact:",
            "source_ref:",
            "validity:",
            "liability:",
            "intent_relation:",
            "disposition:",
            "repair_level:",
            "owner_boundary:",
            "law_family:",
            "clean_run:",
            "finding_mutation_authority:",
            "Do not let accepted liabilities, blockers, or clean-run decisions leave only as unjoinable prose.",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_decision_contract_exposes_review_fold_routes_for_seq_tune(self) -> None:
        required = [
            "contract_version: SKDC-v1",
            "name: review-fold",
            "kind: mixed",
            "RF-SOURCE-001",
            "RF-CLASSIFY-001",
            "RF-RECEIPT-001",
            "RF-KERNEL-001",
            "RF-CAS-REVIEW",
            "RF-MINIMAL-FIX",
            "RF-REFACTOR-KERNEL",
            "decision_receipt: required",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)


if __name__ == "__main__":
    unittest.main()
