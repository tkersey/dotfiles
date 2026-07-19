#!/usr/bin/env -S uv run python
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
NORMALIZED_SKILL = " ".join(SKILL.split())
EXAMPLE = json.loads(
    (ROOT / "assets" / "counterexample-set.valid.example.json").read_text(
        encoding="utf-8"
    )
)
LEGACY_EXAMPLE = json.loads(
    (ROOT / "assets" / "review-fold.valid.example.json").read_text(
        encoding="utf-8"
    )
)


class ReviewFoldContractTests(unittest.TestCase):
    def test_artifact_kernel_is_the_primary_write_route(self) -> None:
        self.assertIn("protocol: artifact-kernel-v1", SKILL)
        self.assertIn("schema: counterexample-set/v1", SKILL)
        self.assertIn("semantic_author: review-fold", SKILL)
        self.assertIn("$ledger ensure", SKILL)
        self.assertIn("ledger validate counterexample-set", SKILL)
        self.assertIn("Counterexample Set", AGENT)

    def test_facts_suggestions_and_authority_are_separate(self) -> None:
        for phrase in (
            "claim != observed fact",
            "observed fact != liability",
            "accepted scope != selected repair",
            "Counterexample Set != mutation authority",
            "Never copy a suggestion",
            "successor Construction Contract before mutation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, SKILL)

    def test_class_identity_excludes_transient_coordinates(self) -> None:
        for coordinate in (
            "filenames",
            "commits",
            "attempt IDs",
            "request IDs",
            "publication epochs",
            "proposed patch",
        ):
            with self.subTest(coordinate=coordinate):
                self.assertIn(coordinate, SKILL)
        self.assertIn("A class may recur across construction", NORMALIZED_SKILL)

    def test_rejected_classes_require_evidence(self) -> None:
        self.assertIn("A rejected class requires evidence", NORMALIZED_SKILL)
        self.assertIn("Do not omit rejection evidence", SKILL)

    def test_legacy_route_is_protocol_isolated(self) -> None:
        self.assertIn("Evidence Ledger admits the current goal as `legacy-actuating-v1`", NORMALIZED_SKILL)
        self.assertIn("Never mix legacy and artifact-kernel", NORMALIZED_SKILL)
        self.assertIn("Read or author RF-v2 only", NORMALIZED_SKILL)
        self.assertIn("do not convert an in-flight goal", NORMALIZED_SKILL)
        self.assertIn("do not", SKILL.split("## Legacy compatibility", 1)[1])
        self.assertEqual("RF-v2", LEGACY_EXAMPLE["review_fold"]["version"])
        self.assertIn("frozen legacy shape example", NORMALIZED_SKILL)
        self.assertIn("Production Phase 3 blocks new artifact-kernel admission", NORMALIZED_SKILL)
        self.assertIn("never infer protocol", NORMALIZED_SKILL)

    def test_example_has_exact_counterexample_shape(self) -> None:
        artifact = EXAMPLE["artifact"]
        self.assertEqual(
            {
                "schema",
                "artifact_id",
                "goal_id",
                "semantic_author",
                "created_at",
                "predecessor_refs",
                "supporting_refs",
                "payload",
            },
            set(artifact),
        )
        self.assertEqual("counterexample-set/v1", artifact["schema"])
        self.assertEqual("review-fold", artifact["semantic_author"])
        counterexample = artifact["payload"]["classes"][0]
        self.assertEqual(
            {
                "class_id",
                "boundary_key",
                "law_ref",
                "discrepancy",
                "owner_boundary",
                "severity",
                "status",
                "observed_facts",
                "evidence_refs",
                "finding_refs",
                "witness",
                "falsifier_ref",
                "applicability",
                "quotient_basis",
            },
            set(counterexample),
        )
        self.assertNotIn("suggested_repair", json.dumps(EXAMPLE))
        self.assertNotIn("mutation_authority", json.dumps(EXAMPLE))

    def test_example_artifact_id_is_content_addressed(self) -> None:
        artifact = copy.deepcopy(EXAMPLE["artifact"])
        claimed = artifact.pop("artifact_id")
        preimage = json.dumps(
            {"artifact": artifact},
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
        digest = hashlib.sha256(b"actuating-artifact/v1\n" + preimage).hexdigest()
        self.assertEqual(f"sha256:{digest}", claimed)


if __name__ == "__main__":
    unittest.main()
