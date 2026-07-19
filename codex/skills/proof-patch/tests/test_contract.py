from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_proof_follows_current_deterministic_closure(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("after live closure has been derived", skill)
        self.assertIn("actuating-closure-receipt/v1", skill)
        self.assertIn("closure-decision/v1", skill)
        self.assertIn("verdict: complete", skill)
        self.assertIn("rederive the closure projection", skill)
        self.assertIn("Do not emit final proof before current complete closure", skill)

    def test_artifact_kernel_binding_is_complete(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for text in (
            "goal_contract_ref:",
            "construction_ref:",
            "subject_digest:",
            "evidence_head:",
            "review_contract_digest:",
            "missing_obligations: 0",
            "missing_retirements: 0",
            "auxiliaries_current: true",
            "clean_streak: 5",
            "full_wave_complete: true",
            "current: true | false",
            "counterexample_sets: []",
            "ship_receipt: {} | null",
        ):
            with self.subTest(text=text):
                self.assertIn(text, skill)

    def test_output_contains_counterexamples_review_and_retirements(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for text in (
            "## Counterexamples and construction",
            "Invalid states eliminated",
            "## Review convergence",
            "Standard clean streak",
            "## Retirement and semantic balance",
            "Dominated constructs remaining",
        ):
            self.assertIn(text, skill)

    def test_legacy_detail_still_requires_bound_source_objects(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        normalized = " ".join(skill.split())
        for text in (
            "run_digest:",
            "resolution_digest:",
            "actuation_kernel_state: {}",
            "review_resolution: {} | null",
            "evidence_folds: []",
            "cas_evidence: {} | null",
            "ship_record: {} | null",
            "basis IDs alone are not enough",
        ):
            with self.subTest(text=text):
                self.assertIn(text, normalized)

    def test_publication_and_authority_remain_external(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        agent = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("Do not publish", skill)
        self.assertIn("does not decide completion", skill)
        self.assertIn("without changing closure or publication state", agent)


if __name__ == "__main__":
    unittest.main()
