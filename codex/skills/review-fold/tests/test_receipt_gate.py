import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "tools" / "review_fold_receipt_gate.py"
sys.path.insert(0, str(ROOT / "tools"))
from review_fold_receipt_gate import validate  # noqa: E402


def receipt() -> dict:
    return {
        "version": "RF-v2",
        "fold_id": "rf-1",
        "goal_id": "goal-1",
        "source": {
            "backend": "cas",
            "source_batch_id": "batch-1",
            "source_state": "findings",
            "artifact": {
                "repo": "/repo",
                "base_sha": "base",
                "branch": "main",
                "head_sha": "abc",
                "state_fingerprint": "sha256:state",
            },
            "source_ref": "cas:batch-1",
        },
        "intent_anchor": {
            "original_goal": "fix the invariant",
            "accepted_scope": ["src"],
            "non_goals": [],
        },
        "findings": [
            {
                "finding_id": "finding-1",
                "source_ref": "cas:finding-1",
                "claim": "owner validation is missing",
                "observed_fact": "transition bypasses owner",
                "suggested_repair": "add validation",
                "validity": "valid",
                "liability": "invariant-gap",
                "intent_relation": "core",
                "novelty": "new-class",
                "disposition": "resolution-input",
                "quotient_key": "owner-validation",
                "owner_boundary": "state-owner",
                "law_family": "transition-preservation",
                "falsifier": "invalid transition is accepted",
                "evidence_refs": ["test:transition"],
                "mutation_authority": {
                    "allowed": False,
                    "reason": "resolution selects work",
                },
            }
        ],
        "compression": {
            "equivalence_classes": [
                {
                    "quotient_key": "owner-validation",
                    "finding_ids": ["finding-1"],
                    "owner_boundary": "state-owner",
                    "law_family": "transition-preservation",
                }
            ]
        },
        "routing_obligations": [
            {
                "trigger": "invariant-gap",
                "finding_ids": ["finding-1"],
                "owner_lens": "invariant-ace",
            }
        ],
    }


class ReceiptTests(unittest.TestCase):
    def test_gate_is_dependency_provisioned_and_directly_executable(self) -> None:
        self.assertTrue(os.access(GATE, os.X_OK))
        self.assertEqual(
            GATE.read_text(encoding="utf-8").splitlines()[:4],
            [
                "#!/usr/bin/env -S uv run --script",
                "# /// script",
                '# dependencies = ["pyyaml"]',
                "# ///",
            ],
        )
        result = subprocess.run(
            [str(GATE), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_valid_material_receipt(self) -> None:
        self.assertEqual(validate(receipt()), [])

    def test_zero_finding_clean_receipt(self) -> None:
        value = receipt()
        value["source"]["source_state"] = "clean"
        value["findings"] = []
        value["compression"]["equivalence_classes"] = []
        value["routing_obligations"] = []
        self.assertEqual(validate(value), [])

    def test_resolution_input_requires_findings_source(self) -> None:
        for source_state in ("invalid-proof", "incomplete"):
            value = receipt()
            value["source"]["source_state"] = source_state
            with self.subTest(source_state=source_state):
                self.assertIn("resolution-input-source-state", validate(value))

            value["findings"][0]["disposition"] = "blocked"
            self.assertNotIn("resolution-input-source-state", validate(value))

    def test_review_fold_cannot_grant_mutation_or_select_work(self) -> None:
        value = receipt()
        value["findings"][0]["mutation_authority"]["allowed"] = True
        value["findings"][0]["selected_work_node"] = {"node_id": "bad"}
        errors = validate(value)
        self.assertIn("finding-mutation-authority", errors)
        self.assertIn("finding-owned-field", errors)

    def test_resolution_input_requires_current_material_evidence(self) -> None:
        value = receipt()
        value["findings"][0]["validity"] = "unproven"
        value["findings"][0]["evidence_refs"] = []
        errors = validate(value)
        self.assertIn("resolution-input-validity", errors)
        self.assertIn("material-evidence", errors)

    def test_resolution_input_rejects_blank_evidence_references(self) -> None:
        for evidence_refs in ([""], ["   "], ["test:transition", " "]):
            value = receipt()
            value["findings"][0]["evidence_refs"] = evidence_refs
            with self.subTest(evidence_refs=evidence_refs):
                self.assertIn("material-evidence", validate(value))

    def test_core_finding_cannot_be_deferred_as_follow_up(self) -> None:
        value = receipt()
        value["findings"][0]["disposition"] = "follow-up"
        self.assertIn("follow-up-intent", validate(value))

        value["findings"][0]["intent_relation"] = "adjacent"
        self.assertNotIn("follow-up-intent", validate(value))

    def test_core_material_disposition_tracks_validity(self) -> None:
        cases = (
            ("valid", "resolution-input", False),
            ("valid", "reject", True),
            ("valid", "proof-only", True),
            ("unproven", "proof-only", False),
            ("unproven", "reject", True),
            ("needs-owner", "ask-human", False),
            ("needs-owner", "proof-only", True),
            ("invalid", "reject", False),
            ("invalid", "resolution-input", True),
        )
        for validity, disposition, rejected in cases:
            value = receipt()
            finding = value["findings"][0]
            finding["validity"] = validity
            finding["liability"] = "blocks-goal"
            finding["disposition"] = disposition
            value["routing_obligations"] = []
            errors = validate(value)
            with self.subTest(validity=validity, disposition=disposition):
                self.assertEqual("core-material-disposition" in errors, rejected)

    def test_duplicate_reject_requires_a_routed_quotient_member(self) -> None:
        value = receipt()
        duplicate = value["findings"][0].copy()
        duplicate["mutation_authority"] = value["findings"][0][
            "mutation_authority"
        ].copy()
        duplicate.update(
            {
                "finding_id": "finding-2",
                "source_ref": "cas:finding-2",
                "novelty": "duplicate",
                "disposition": "reject",
            }
        )
        value["findings"].append(duplicate)
        value["compression"]["equivalence_classes"][0]["finding_ids"] = [
            "finding-1",
            "finding-2",
        ]
        value["routing_obligations"][0]["finding_ids"] = [
            "finding-1",
            "finding-2",
        ]
        self.assertNotIn("core-material-disposition", validate(value))

        value["findings"][0]["disposition"] = "proof-only"
        self.assertIn("core-material-disposition", validate(value))

    def test_every_material_disposition_requires_evidence_bundle(self) -> None:
        cases = (
            ("unproven", "proof-only"),
            ("needs-owner", "ask-human"),
            ("valid", "blocked"),
        )
        fields = {
            "observed_fact": "material-observed-fact",
            "owner_boundary": "material-owner_boundary",
            "law_family": "material-law_family",
            "falsifier": "material-falsifier",
            "evidence_refs": "material-evidence",
        }
        for validity, disposition in cases:
            for field, expected in fields.items():
                value = receipt()
                finding = value["findings"][0]
                finding["validity"] = validity
                finding["disposition"] = disposition
                finding.pop(field)
                with self.subTest(
                    validity=validity, disposition=disposition, field=field
                ):
                    self.assertIn(expected, validate(value))

        value = receipt()
        finding = value["findings"][0]
        finding["validity"] = "invalid"
        finding["liability"] = "style"
        finding["disposition"] = "reject"
        for field in fields:
            finding.pop(field)
        value["routing_obligations"] = []
        self.assertEqual(validate(value), [])

    def test_resolution_input_requires_a_substantive_observed_fact(self) -> None:
        for observed_fact in (None, "", "   "):
            value = receipt()
            if observed_fact is None:
                value["findings"][0].pop("observed_fact")
            else:
                value["findings"][0]["observed_fact"] = observed_fact
            with self.subTest(observed_fact=observed_fact):
                self.assertIn("material-observed-fact", validate(value))

        value = receipt()
        value["findings"][0]["observed_fact"] = value["findings"][0]["claim"]
        self.assertIn("material-observed-fact", validate(value))

    def test_observed_proof_gap_remains_a_material_fact(self) -> None:
        value = receipt()
        finding = value["findings"][0]
        finding["liability"] = "proof-gap"
        finding["observed_fact"] = (
            "The inspected transition tests contain no preservation assertion."
        )
        value["routing_obligations"] = []
        self.assertEqual(validate(value), [])

    def test_finding_identity_source_and_claim_are_substantive(self) -> None:
        for field, expected in (
            ("finding_id", "finding-id"),
            ("source_ref", "finding-source"),
            ("claim", "finding-claim"),
        ):
            value = receipt()
            value["findings"][0][field] = "   "
            if field == "finding_id":
                value["compression"]["equivalence_classes"][0]["finding_ids"] = [
                    "   "
                ]
                value["routing_obligations"][0]["finding_ids"] = ["   "]
            with self.subTest(field=field):
                self.assertIn(expected, validate(value))

        value = receipt()
        duplicate = value["findings"][0].copy()
        duplicate["mutation_authority"] = value["findings"][0][
            "mutation_authority"
        ].copy()
        duplicate.update(
            {
                "finding_id": " finding-1 ",
                "source_ref": "cas:finding-duplicate",
                "novelty": "duplicate",
                "disposition": "reject",
            }
        )
        value["findings"].append(duplicate)
        value["compression"]["equivalence_classes"][0]["finding_ids"] = [
            "finding-1",
            " finding-1 ",
        ]
        value["routing_obligations"][0]["finding_ids"] = [
            "finding-1",
            " finding-1 ",
        ]
        self.assertIn("finding-id", validate(value))

    def test_compression_metadata_matches_every_material_member(self) -> None:
        for field in ("owner_boundary", "law_family"):
            value = receipt()
            value["compression"]["equivalence_classes"][0][field] = "unrelated"
            with self.subTest(field=field):
                self.assertIn("compression-owner-law-mismatch", validate(value))

        for field in ("owner_boundary", "law_family"):
            value = receipt()
            second = value["findings"][0].copy()
            second["mutation_authority"] = value["findings"][0][
                "mutation_authority"
            ].copy()
            second.update(
                {
                    "finding_id": "finding-2",
                    "source_ref": "cas:finding-2",
                    field: "different-member-metadata",
                }
            )
            value["findings"].append(second)
            value["compression"]["equivalence_classes"][0]["finding_ids"] = [
                "finding-1",
                "finding-2",
            ]
            value["routing_obligations"][0]["finding_ids"] = [
                "finding-1",
                "finding-2",
            ]
            with self.subTest(conflicting_member=field):
                self.assertIn("compression-owner-law-mismatch", validate(value))

    def test_quotient_and_routing_must_cover_findings(self) -> None:
        value = receipt()
        value["compression"]["equivalence_classes"] = []
        value["routing_obligations"] = []
        errors = validate(value)
        self.assertIn("compression-coverage", errors)
        self.assertIn("routing-coverage", errors)


if __name__ == "__main__":
    unittest.main()
