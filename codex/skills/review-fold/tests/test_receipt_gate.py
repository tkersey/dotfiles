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


def valid_kernel(**overrides):
    kernel = {
        "status": "point",
        "pressure": "low",
        "equivalence_class": "not-applicable",
        "owner_boundary": "input validation",
        "law_family": "validation-boundary",
        "falsifier": "comment-1 shows missing owner validation",
        "point_safety": "proven",
        "evidence_refs": ["repo:file.py:10"],
    }
    kernel.update(overrides)
    return kernel


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
        "disposition": "accepted-liability",
        "owner_boundary": "input validation",
        "law_family": "validation-boundary",
        "kernel_fold": valid_kernel(),
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
                "version": "RF-v1.4",
                "source": {"backend": "github-comments"},
                "findings": [valid_finding()],
                "compression": {"kernel_pressure": "low"},
                "recommended_resolution": {
                    "clean_run_accounting": {
                        "normalized_clean_this_source": "no",
                        "count_effect": "reset",
                    }
                },
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "pass")
        self.assertEqual(report["finding_count"], 1)

    def test_compact_receipt_missing_source_ref_fails(self) -> None:
        receipt = {
            "rf_v14_compact": {
                "validity": "valid",
                "liability": "blocks-goal",
                "intent_relation": "core",
                "disposition": "accepted-liability",
                "owner_boundary": "input validation",
                "law_family": "validation-boundary",
                "kernel_fold": valid_kernel(),
                "evidence_refs": [],
                "code_change_candidate": "yes",
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
                "version": "RF-v1.4",
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

    def test_structural_kernel_requires_equivalence_class_or_owner_boundary(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.4",
                "findings": [
                    valid_finding(
                        kernel_fold=valid_kernel(
                            status="structural",
                            pressure="high",
                            equivalence_class="",
                            owner_boundary="",
                            point_safety="not-applicable",
                        )
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].kernel_fold.structural:missing-equivalence-class-or-owner-boundary",
            report["errors"],
        )

    def test_high_pressure_point_requires_proven_point_safety(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.4",
                "findings": [
                    valid_finding(
                        kernel_fold=valid_kernel(
                            pressure="high",
                            point_safety="not-proven",
                            evidence_refs=[],
                        )
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].kernel_fold.point_safety:point-status-requires-proven",
            report["errors"],
        )
        self.assertIn(
            "review_fold.findings[0].kernel_fold.point_safety:high-pressure-point-requires-proof",
            report["errors"],
        )

    def test_rf_v13_receipt_fails(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.3",
                "findings": [valid_finding()],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold.version:expected-RF-v1.4", report["errors"])

    def test_repair_level_is_forbidden(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.4",
                "findings": [valid_finding(repair_level="minimal-fix")],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold.findings[0].repair_level:forbidden-in-RF-v1.4", report["errors"])

    def test_minimal_fix_disposition_fails(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.4",
                "findings": [valid_finding(disposition="minimal-fix")],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold.findings[0].disposition:invalid", report["errors"])

    def test_action_plan_is_forbidden(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.4",
                "findings": [valid_finding()],
                "action_plan": {"mode": "refactor-kernel"},
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold.action_plan:forbidden-in-RF-v1.4", report["errors"])


if __name__ == "__main__":
    unittest.main()
