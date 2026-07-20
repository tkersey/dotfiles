#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
DECISION = (ROOT / "references" / "decision-contract.yaml").read_text(
    encoding="utf-8"
)
EXAMPLE = json.loads(
    (ROOT / "assets" / "review-fold.valid.example.json").read_text(
        encoding="utf-8"
    )
)
CONTRACT = " ".join((SKILL + "\n" + AGENT + "\n" + DECISION).split())


class ReviewFoldContractTests(unittest.TestCase):
    def test_counterexample_set_is_the_only_output_artifact(self) -> None:
        for token in [
            "counterexample-set/v1",
            "semantic_author: review-fold",
            "stable Counterexample",
            "one governing law at one boundary",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

    def test_classification_does_not_select_action_or_authority(self) -> None:
        for token in [
            "`$actuating` owns evaluation",
            "Do not propose or execute a repair",
            "Do not count clean attempts",
            "A pass grants no mutation",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, CONTRACT)

    def test_current_ledger_adapter_materializes_the_artifact(self) -> None:
        self.assertIn("ledger --source actuation", SKILL)
        self.assertIn("--goal <goal-id>", SKILL)
        self.assertIn("append --input <counterexample-set.json>", SKILL)

    def test_recurrent_class_preserves_set_lineage(self) -> None:
        self.assertIn("new Set's `predecessor_refs`", SKILL)
        self.assertIn("prior Set that most recently", SKILL)

    def test_non_review_falsifier_does_not_require_a_campaign(self) -> None:
        self.assertIn("non-review falsifier requires no review campaign", CONTRACT)
        self.assertIn("Never fabricate a campaign", CONTRACT)
        self.assertIn("make `review_contract_digest` optional", CONTRACT)

    def test_example_uses_current_exact_shape(self) -> None:
        artifact = EXAMPLE["artifact"]
        self.assertEqual("counterexample-set/v1", artifact["schema"])
        self.assertIsNone(artifact["artifact_id"])
        self.assertEqual("review-fold", artifact["semantic_author"])
        self.assertEqual(
            {
                "subject",
                "classes",
            },
            set(artifact["payload"]),
        )
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

    def test_retired_review_artifacts_are_absent(self) -> None:
        for token in [
            "RF-v2",
            "review-resolution/v1",
            "resolution-input",
            "correctness_refinement",
            "owner-boundary-synthesis/v1",
            "auxiliary-remediation",
        ]:
            with self.subTest(token=token):
                self.assertNotIn(token, CONTRACT)


if __name__ == "__main__":
    unittest.main()
