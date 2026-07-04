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

    def test_shortcut_liability_labels_do_not_replace_receipts(self) -> None:
        skill_required = [
            "Shortcut labels do not relax the floor.",
            "straightforward liability",
            "obvious fix",
            "valid P1",
            "valid P2",
            "accepted P1",
            "accepted P2",
            "Review fold:",
            "implementation starts",
            "Do not use `straightforward liability`, `obvious fix`, or severity labels as substitutes for RF-v1.3 receipt fields.",
        ]
        for token in skill_required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

        prompt_required = [
            "straightforward liability",
            "obvious fix",
            "valid P1",
            "valid P2",
            "accepted P1",
            "accepted P2",
            "Review fold:",
            "grouped liability prose",
            "substitutes for RF-v1.3 receipt fields before implementation",
        ]
        for token in prompt_required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

    def test_followup_cas_batches_need_fresh_receipts(self) -> None:
        skill_required = [
            "Receipt scope is per review result, not per closeout.",
            "does not cover later CAS attempts",
            "follow-up finding batches",
            "dirty clean-streak attempts",
            "terminal CAS list",
            "compact follow-up patch",
            "Treat each new CAS attempt result, follow-up finding batch, reopened thread batch, or dirty clean-streak attempt as a new receipt scope",
            "Do not let one RF receipt for an earlier CAS batch stand in for later follow-up findings",
        ]
        for token in skill_required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

        prompt_required = [
            "Earlier RF receipts do not cover later CAS attempts",
            "follow-up finding batches",
            "dirty clean-streak attempts",
            "fresh RF-v1.3 compact/full receipt for each new source batch",
        ]
        for token in prompt_required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

    def test_single_finding_cas_prose_needs_fresh_receipts(self) -> None:
        skill_required = [
            "Fresh CAS-result prose has the same floor even when there is only one finding.",
            "Treat the pattern class, not only the exact examples, as receipt-triggering:",
            "CAS attempt ... found ... P1/P2",
            "attempt ... found ... P1/P2",
            "CAS attempt ... returned ... P1/P2",
            "findings",
            "CAS found ... valid items",
            "CAS found ... valid classes",
            "CAS found two valid classes",
            "CAS found one remaining valid P1/P2",
            "CAS attempt ... returned another accepted P1/P2",
            "the finding is valid",
            "this finding is valid too",
            "CAS is right",
            "accepted code-change liabilities",
            "accepted code-change liability",
            "the owner fix is",
            "owner-correct fix is",
            "the clean fix is",
            "CAS found ... proof gaps",
            "straightforward proof gaps",
            "proof gaps now",
            "concrete gaps remain",
            "gaps remain",
            "clean streak stays at 0",
            "clean streak resets to zero",
            "clean streak resets to 0",
            "streak remains 0",
            "RF-v1.3 compact/full receipt before",
            "fix",
            "next mutation",
            "Treat single or small-batch CAS prose like `CAS attempt found a P1/P2`, `attempt found a P1/P2`, `CAS attempt returned P1/P2 findings`, `CAS found valid items`, `CAS found valid classes`, `CAS found two valid classes`, `CAS found one remaining valid P1/P2`, `CAS attempt returned another accepted P1/P2`, `the finding is valid`, `this finding is valid too`, `CAS is right`, `accepted code-change liabilities`, `accepted code-change liability`, `the owner fix is`, `owner-correct fix is`, `the clean fix is`, `CAS found proof gaps`, `straightforward proof gaps`, `proof gaps now`, `concrete gaps remain`, `gaps remain`, `clean streak stays at 0`, `clean streak resets to zero`, `clean streak resets to 0`, or `streak remains 0` as receipt-triggering folds",
            "Fresh PR-thread prose has the same floor.",
            "unresolved PR review threads ... P1/P2",
            "unresolved PR comments are valid",
            "PR comments are valid",
            "they are both P1/P2",
            "accepted liabilities",
            "describing the repair path or patching review-thread findings",
            "Thread-disposition prose has the same floor.",
            "targeted threads report resolved",
            "PR thread sweep is clean",
            "no unresolved threads",
            "unresolved thread count is 0",
            "no unresolved threads across both pages",
            "receipt-triggering closure folds before advancing review closeout",
            "Grouped or same-boundary CAS prose has the same requirement.",
            "CAS found ... more",
            "CAS found a larger class",
            "CAS found a broader class",
            "CAS is still finding",
            "CAS continues to find",
            "CAS has narrowed this to one remaining class",
            "one remaining class",
            "same ... boundary",
            "same owner-boundary refactor",
            "same owner boundary",
            "same ... class",
            "forms of the same ... class",
            "same-class finding",
            "Treat the pattern class, not only the exact examples, as receipt-triggering:",
            "describing the refactor",
            "replacement strategy, or next patch",
            "Treat grouped CAS prose like `CAS found ... more`, `CAS found a larger class`, `CAS found a broader class`, `CAS is still finding`, `CAS continues to find`, `CAS has narrowed this to one remaining class`, `one remaining class`, `same ... boundary`, `same owner-boundary refactor`, `same ... class`, `forms of the same ... class`, or `same-class finding` as a receipt-triggering fold",
            "Clean CAS-run prose has the same floor.",
            "CAS attempt ... is clean",
            "clean streak is N/3",
            "clean streak is 1/3",
            "starting fresh attempt N",
            "receipt-triggering clean-run accounting before advancing the closeout loop",
        ]
        for token in skill_required:
            with self.subTest(token=token):
                self.assertIn(token, SKILL)

        prompt_required = [
            "CAS attempt found a P1/P2",
            "attempt found a P1/P2",
            "CAS attempt returned P1/P2 findings",
            "CAS found valid items",
            "CAS found valid classes",
            "CAS found two valid classes",
            "CAS found one remaining valid P1/P2",
            "CAS attempt returned another accepted P1/P2",
            "the finding is valid",
            "this finding is valid too",
            "CAS is right",
            "accepted code-change liabilities",
            "accepted code-change liability",
            "the owner fix is",
            "owner-correct fix is",
            "the clean fix is",
            "CAS found proof gaps",
            "straightforward proof gaps",
            "proof gaps now",
            "concrete gaps remain",
            "gaps remain",
            "clean streak stays at 0",
            "clean streak resets to zero",
            "clean streak resets to 0",
            "streak remains 0",
            "require a fresh RF-v1.3 compact/full receipt before describing the repair path or patching it",
            "PR-thread review prose patterns like",
            "unresolved PR review threads ... P1/P2",
            "unresolved PR comments are valid",
            "PR comments are valid",
            "they are both P1/P2",
            "accepted liabilities",
            "require a fresh RF-v1.3 compact/full receipt before describing the repair path or patching review-thread findings",
            "Thread-disposition prose patterns like",
            "targeted threads report resolved",
            "PR thread sweep is clean",
            "no unresolved threads",
            "unresolved thread count is 0",
            "no unresolved threads across both pages",
            "require a fresh RF-v1.3 compact/full receipt before advancing review closeout",
            "Grouped CAS prose patterns like",
            "CAS found ... more",
            "CAS found a larger class",
            "CAS found a broader class",
            "CAS continues to find",
            "CAS has narrowed this to one remaining class",
            "one remaining class",
            "same ... boundary",
            "same owner-boundary refactor",
            "same owner boundary",
            "same ... class",
            "forms of the same ... class",
            "same-class finding",
            "require a fresh RF-v1.3 compact/full receipt before describing a refactor, replacement strategy, or next patch",
            "Clean CAS-run prose patterns like",
            "CAS attempt ... is clean",
            "clean streak is N/3",
            "clean streak is 1/3",
            "starting fresh attempt N",
            "require a fresh RF-v1.3 compact/full receipt before advancing the closeout loop or launching the next review attempt",
        ]
        for token in prompt_required:
            with self.subTest(token=token):
                self.assertIn(token, NORMALIZED)

        contract_required = [
            "review-fold-v1.4.22-review-fold-label-pattern",
            "fresh receipt before single-finding CAS repair prose",
            "PR-thread accepted liabilities have a receipt before repair planning",
            "thread disposition has a receipt before review closeout advances",
            "single fresh or remaining severity acceptance has a joinable receipt before repair planning",
            "dirty severity attempts have a receipt before streak reset and repair planning",
            "valid class batches have a receipt before repair planning",
            "proof-gap batches have a receipt before repair planning",
            "small-batch remaining gaps have a receipt before repair planning",
            "grouped same-boundary or same-class CAS acceptance has a receipt before refactor planning",
            "grouped larger-class CAS acceptance has a receipt before refactor planning",
            "remaining-class CAS acceptance has a receipt before replacement planning",
            "clean CAS results have a receipt before the streak advances",
            "CAS attempt found a P1 or P2 without a receipt",
            "attempt found a P1 or P2 without a receipt",
            "CAS is right prose precedes receipt",
            "CAS attempt returned P1 or P2 findings without a receipt",
            "CAS attempt returned another accepted P1 or P2 without a receipt",
            "Review fold prefix leaves no receipt",
            "straightforward proof gaps prose precedes receipt",
            "accepted P1 or P2 shortcut leaves no receipt",
            "PR comments are valid without a receipt",
            "unresolved PR comments are valid without a receipt",
            "PR accepted liabilities prose precedes receipt",
            "PR thread sweep is clean without a receipt",
            "no unresolved threads prose precedes receipt",
            "targeted threads resolved prose precedes receipt",
            "CAS found valid items without a receipt",
            "CAS found valid classes without a receipt",
            "CAS found two valid classes without a receipt",
            "CAS found proof gaps without a receipt",
            "accepted code-change liability prose precedes receipt",
            "accepted code-change liabilities prose precedes receipt",
            "clean fix prose precedes receipt",
            "concrete gaps remain prose precedes receipt",
            "gaps remain prose precedes receipt",
            "CAS found one remaining valid P1 or P2 without a receipt",
            "CAS found more same-boundary findings without a receipt",
            "CAS found a larger class without a receipt",
            "CAS found a broader class without a receipt",
            "CAS narrowed to one remaining class without a receipt",
            "CAS found forms of the same class without a receipt",
            "same class repair prose precedes receipt",
            "CAS clean result advances the clean streak without a receipt",
            "next CAS attempt starts after clean result without a receipt",
            "clean streak resets to zero without a receipt",
            "clean streak resets to 0 without a receipt",
            "CAS is still finding prose precedes receipt",
            "same boundary refactor prose precedes receipt",
            "owner-correct fix prose precedes receipt",
            "finding is valid prose precedes receipt",
            "streak remains zero without a receipt",
        ]
        for token in contract_required:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

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
            "straightforward liability shortcut leaves no receipt",
            "follow-up CAS findings reuse an earlier receipt",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)


if __name__ == "__main__":
    unittest.main()
