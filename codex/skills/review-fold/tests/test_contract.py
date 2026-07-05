#!/usr/bin/env -S uv run python
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_ROOT = ROOT.parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
CONTRACT = (ROOT / "references" / "decision-contract.yaml").read_text(encoding="utf-8")
TRIGGERS = (ROOT / "references" / "material-fold-triggers.yaml").read_text(encoding="utf-8")
REDUCER = (CODEX_ROOT / "agents" / "review-reducer.toml").read_text(encoding="utf-8")
NORMALIZED_PROMPTS = " ".join((AGENT + "\n" + REDUCER).split())


class ReviewFoldContractTests(unittest.TestCase):
    def test_review_fold_is_backend_neutral(self) -> None:
        required = [
            "review-backend neutral",
            "does not choose the backend",
            "fresh review backend selection",
            "review-profile / auxiliary-lens selection",
            "implementation authority",
            "terminal closeout authority",
            "backend_specific: {}",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)
        self.assertNotIn("RF-CAS-REVIEW", CONTRACT)
        self.assertNotIn("CAS review lanes", SKILL)
        self.assertNotIn("Supported CAS-backed review lanes", SKILL)

    def test_rf_v13_schema_has_generic_joinable_source_refs(self) -> None:
        required = [
            "version: RF-v1.3",
            "source_ref:",
            "backend: cas|github-comments|human-review|prior-artifact|local-audit|other|unknown",
            "source_batch_id",
            "finding_id",
            "finding_fingerprint",
            "review_attempt_id",
            "review_thread_id",
            "review_turn_id",
            "lane_role: standard|auxiliary|human|prior-artifact|unknown",
            "head_sha",
            "target_fingerprint",
            "backend_specific: {}",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_minimal_review_law_and_dispositions_remain(self) -> None:
        required = [
            "claim != fact",
            "fact != liability",
            "liability != scope",
            "scope != code change",
            "code-change candidate != mutation authority",
            "`reject`",
            "`proof-only`",
            "`minimal-fix`",
            "`refactor-kernel`",
            "`ask-human`",
            "`follow-up`",
            "`blocked`",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

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
            "allowed: no",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_material_fold_trigger_taxonomy_replaces_literal_phrase_catalog(self) -> None:
        required = [
            "acceptance_shortcut",
            "repair_shortcut",
            "proof_gap_shortcut",
            "clean_run_accounting",
            "thread_disposition",
            "grouped_liability",
            "source_batch_boundary",
            "Examples are",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, TRIGGERS)
        skill_required = [
            "Material fold trigger classes",
            "Treat the semantic class, not the literal wording",
            "acceptance shortcut",
            "repair shortcut",
            "proof-gap shortcut",
            "clean-run accounting",
            "thread disposition",
            "grouped-liability / owner-boundary shortcut",
            "source-batch boundary",
        ]
        for token in skill_required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

    def test_prompt_is_not_cas_transcript_phrase_catalog(self) -> None:
        forbidden = [
            "CAS attempt found a P1/P2",
            "CAS attempt N found a new P1/P2",
            "CAS returned one current-head P1/P2 finding",
            "CAS found valid classes",
            "CAS found two valid classes",
            "CAS found one remaining valid P1/P2",
            "CAS is right",
            "I'm accepting it",
            "accepted P1",
            "accepted P2",
            "clean streak resets again",
            "forms of the same class",
        ]
        combined = SKILL + "\n" + NORMALIZED_PROMPTS + "\n" + CONTRACT
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, combined)

    def test_prompts_request_material_receipts_without_backend_overfit(self) -> None:
        required = [
            "Keep review-fold backend neutral",
            "Material fold trigger classes are semantic",
            "Shortcut prose is not a receipt",
            "finding_mutation_authority.allowed: no",
            "A finding is never mutation authority",
            "Do not post PR comments, resolve threads, mutate files, choose a fresh review backend, or claim terminal review closure",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED_PROMPTS)

    def test_decision_contract_exposes_routes_for_seq_tune(self) -> None:
        required = [
            "contract_version: SKDC-v1",
            "name: review-fold",
            "kind: mixed",
            "RF-SOURCE-001",
            "RF-CLASSIFY-001",
            "RF-RECEIPT-001",
            "RF-KERNEL-001",
            "RF-SOURCE-BLOCK",
            "RF-MINIMAL-FIX",
            "RF-REFACTOR-KERNEL",
            "decision_receipt: required",
            "validator: codex/skills/review-fold/tools/review_fold_receipt_gate.py",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)


if __name__ == "__main__":
    unittest.main()
