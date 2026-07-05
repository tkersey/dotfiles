#!/usr/bin/env -S uv run python
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "review_fold_receipt_gate.py"
SPEC = importlib.util.spec_from_file_location("review_fold_receipt_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_finding(**overrides):
    finding = {
        "id": "finding-1",
        "source_ref": {
            "backend": "github-comments",
            "source_batch_id": "thread-batch-1",
            "finding_id": "comment-1",
            "finding_fingerprint": "fp-1",
            "review_attempt_id": "",
            "review_thread_id": "thread-1",
            "review_turn_id": "",
            "lane_role": "human",
            "head_sha": "abc123",
            "target_fingerprint": "diff:abc",
            "backend_specific": {},
        },
        "validity": "valid",
        "liability": "blocks-goal",
        "intent_relation": "core",
        "disposition": "minimal-fix",
        "repair_level": "minimal-fix",
        "owner_boundary": "input validation",
        "law_family": "validation-boundary",
        "evidence_refs": ["repo:file.py:10"],
        "code_change_candidate": "yes",
        "finding_mutation_authority": {"allowed": "no", "reason": "resolution fold owns mutation"},
    }
    finding.update(overrides)
    return finding


class ReviewFoldReceiptGateTests(unittest.TestCase):
    def test_valid_full_receipt_passes(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.3",
                "source": {"backend": "github-comments"},
                "findings": [valid_finding()],
                "compression": {"one_patch_per_comment_risk": "low"},
                "recommended_resolution": {
                    "clean_run_accounting": {
                        "normalized_clean_this_source": "no",
                        "count_effect": "reset",
                    }
                },
                "action_plan": {"mode": "minimal-fix"},
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "pass")
        self.assertEqual(report["finding_count"], 1)

    def test_compact_receipt_missing_source_ref_fails(self) -> None:
        receipt = {
            "rf_v13_compact": {
                "validity": "valid",
                "liability": "blocks-goal",
                "intent_relation": "core",
                "disposition": "minimal-fix",
                "repair_level": "minimal-fix",
                "owner_boundary": "input validation",
                "law_family": "validation-boundary",
                "evidence_refs": [],
                "clean_run": {"normalized_clean": "not-applicable", "count_effect": "none"},
                "finding_mutation_authority": {"allowed": "no", "reason": "not authority"},
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("compact.source_ref:missing", report["errors"])

    def test_mutation_authority_allowed_fails(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.3",
                "findings": [
                    valid_finding(
                        finding_mutation_authority={"allowed": "yes", "reason": "bad"}
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].finding_mutation_authority.allowed:must-be-no",
            report["errors"],
        )

    def test_refactor_kernel_requires_equivalence_class_or_owner_boundary(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.3",
                "findings": [
                    valid_finding(
                        disposition="refactor-kernel",
                        repair_level="refactor-kernel",
                    )
                ],
                "compression": {"one_patch_per_comment_risk": "high"},
                "action_plan": {"mode": "refactor-kernel"},
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "compression.refactor-kernel:missing-equivalence-class-or-owner-boundary",
            report["errors"],
        )

    def test_reject_cannot_be_code_change_candidate(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.3",
                "findings": [
                    valid_finding(
                        validity="invalid",
                        liability="out-of-scope",
                        intent_relation="unrelated",
                        disposition="reject",
                        repair_level="none",
                        code_change_candidate="yes",
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].code_change_candidate:reject-cannot-be-code-change",
            report["errors"],
        )


if __name__ == "__main__":
    unittest.main()
