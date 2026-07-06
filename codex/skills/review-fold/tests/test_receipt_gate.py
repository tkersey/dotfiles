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
        "status": "refactor-kernel",
        "pressure": "low",
        "equivalence_class": "input-validation-class",
        "owner_boundary": "input validation",
        "law_family": "validation-boundary",
        "falsifier": "comment-1 shows missing owner validation",
        "boundary_proof": "proven",
        "evidence_refs": ["repo:file.py:10"],
    }
    kernel.update(overrides)
    return kernel


def unknown_kernel(**overrides):
    kernel = valid_kernel(
        status="unknown",
        pressure="medium",
        equivalence_class="unknown",
        owner_boundary="unknown",
        boundary_proof="not-proven",
        proof_gap="missing owner-boundary evidence",
        next_evidence_action="inspect-more",
    )
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
        "disposition": "blocked",
        "owner_boundary": "input validation",
        "law_family": "validation-boundary",
        "kernel_fold": valid_kernel(),
        "evidence_refs": ["repo:file.py:10"],
        "finding_mutation_authority": {"allowed": "no", "reason": "review fold is not mutation authority"},
    }
    finding.update(overrides)
    return finding


class ReviewFoldReceiptGateTests(unittest.TestCase):
    def test_valid_full_receipt_passes(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
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

    def test_valid_compact_unknown_quarantine_passes(self) -> None:
        receipt = {
            "rf_v15_compact": valid_finding(
                kernel_fold=unknown_kernel(),
                clean_run={"normalized_clean": "no", "count_effect": "blocked"},
            )
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "pass")

    def test_compact_receipt_missing_source_ref_fails(self) -> None:
        finding = valid_finding(clean_run={"normalized_clean": "not-applicable", "count_effect": "none"})
        del finding["source_ref"]
        receipt = {"rf_v15_compact": finding}
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("compact.source_ref:missing", report["errors"])

    def test_mutation_authority_allowed_fails(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
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
                "version": "RF-v1.5",
                "findings": [
                    valid_finding(
                        kernel_fold=valid_kernel(
                            pressure="high",
                            equivalence_class="",
                            owner_boundary="",
                            boundary_proof="not-applicable",
                        )
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].kernel_fold.refactor-kernel:missing-equivalence-class-or-owner-boundary",
            report["errors"],
        )

    def test_refactor_kernel_requires_blocked_control_disposition(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [valid_finding(disposition="proof-only")],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].disposition:refactor-kernel-requires-blocked-control",
            report["errors"],
        )

    def test_unknown_requires_proof_gap_and_next_evidence_action(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [
                    valid_finding(
                        kernel_fold=unknown_kernel(proof_gap="", next_evidence_action="")
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].kernel_fold.proof_gap:required-for-unknown",
            report["errors"],
        )
        self.assertIn(
            "review_fold.findings[0].kernel_fold.next_evidence_action:missing",
            report["errors"],
        )

    def test_unknown_requires_blocked_or_ask_human_control_disposition(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [
                    valid_finding(
                        disposition="follow-up",
                        intent_relation="adjacent",
                        kernel_fold=unknown_kernel(),
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].disposition:unknown-requires-blocked-or-ask-human",
            report["errors"],
        )

    def test_unknown_cannot_be_clean_or_increment_clean_run(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [
                    valid_finding(
                        kernel_fold=unknown_kernel(),
                        clean_run={"normalized_clean": "yes", "count_effect": "increment"},
                    )
                ],
                "recommended_resolution": {
                    "clean_run_accounting": {
                        "normalized_clean_this_source": "yes",
                        "count_effect": "increment",
                    }
                },
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].clean_run.normalized_clean:unknown-cannot-be-clean",
            report["errors"],
        )
        self.assertIn(
            "review_fold.findings[0].clean_run.count_effect:unknown-cannot-increment-clean-run",
            report["errors"],
        )
        self.assertIn(
            "recommended_resolution.clean_run_accounting.normalized_clean_this_source:unknown-cannot-be-clean",
            report["errors"],
        )
        self.assertIn(
            "recommended_resolution.clean_run_accounting.count_effect:unknown-cannot-increment-clean-run",
            report["errors"],
        )

    def test_ownerless_specialized_liability_cannot_be_clean_or_increment(self) -> None:
        source_ref = valid_finding()["source_ref"]
        source_ref["lane"] = "standard"
        source_ref["lane_role"] = "standard"
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [
                    valid_finding(
                        source_ref=source_ref,
                        liability="invariant-gap",
                        clean_run={"normalized_clean": "yes", "count_effect": "increment"},
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].clean_run.normalized_clean:specialized-owner-lens-required",
            report["errors"],
        )
        self.assertIn(
            "review_fold.findings[0].clean_run.count_effect:specialized-owner-lens-required",
            report["errors"],
        )

    def test_auxiliary_owner_lens_specialized_liability_can_be_clean(self) -> None:
        source_ref = valid_finding()["source_ref"]
        source_ref["lane"] = "invariant-ace"
        source_ref["lane_role"] = "auxiliary"
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [
                    valid_finding(
                        source_ref=source_ref,
                        liability="invariant-gap",
                        disposition="proof-only",
                        kernel_fold=valid_kernel(status="none", boundary_proof="not-applicable"),
                        clean_run={"normalized_clean": "yes", "count_effect": "increment"},
                    )
                ],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "pass")

    def test_rf_v14_receipt_fails(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.4",
                "findings": [valid_finding()],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold.version:expected-RF-v1.5", report["errors"])

    def test_rf_v14_compact_fails(self) -> None:
        report = MODULE.validate({"rf_v14_compact": valid_finding()})["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("receipt: expected RF-v1.5 compact object", report["errors"])

    def test_repair_level_is_forbidden(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [valid_finding(repair_level="minimal-fix")],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold.findings[0].repair_level:forbidden-in-RF-v1.5", report["errors"])

    def test_code_change_candidate_is_forbidden(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [valid_finding(code_change_candidate="yes")],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn(
            "review_fold.findings[0].code_change_candidate:forbidden-in-RF-v1.5",
            report["errors"],
        )

    def test_retired_disposition_and_kernel_statuses_fail(self) -> None:
        cases = [
            ("accepted-liability", valid_finding(disposition="accepted-liability"), "review_fold.findings[0].disposition:invalid"),
            ("point", valid_finding(kernel_fold=valid_kernel(status="point")), "review_fold.findings[0].kernel_fold.status:invalid"),
            ("structural", valid_finding(kernel_fold=valid_kernel(status="structural")), "review_fold.findings[0].kernel_fold.status:invalid"),
        ]
        for _label, finding, expected in cases:
            with self.subTest(expected=expected):
                receipt = {"review_fold": {"version": "RF-v1.5", "findings": [finding]}}
                report = MODULE.validate(receipt)["review_fold_receipt_gate"]
                self.assertEqual(report["verdict"], "fail")
                self.assertIn(expected, report["errors"])

    def test_minimal_fix_disposition_fails(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [valid_finding(disposition="minimal-fix")],
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold.findings[0].disposition:invalid", report["errors"])

    def test_action_plan_is_forbidden(self) -> None:
        receipt = {
            "review_fold": {
                "version": "RF-v1.5",
                "findings": [valid_finding()],
                "action_plan": {"mode": "refactor-kernel"},
            }
        }
        report = MODULE.validate(receipt)["review_fold_receipt_gate"]
        self.assertEqual(report["verdict"], "fail")
        self.assertIn("review_fold.action_plan:forbidden-in-RF-v1.5", report["errors"])


if __name__ == "__main__":
    unittest.main()
