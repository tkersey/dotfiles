from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_proof_follows_closure(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("after live closure has been derived", skill)
        self.assertIn("closure-decision/v1", skill)
        self.assertIn("verdict: complete", skill)
        self.assertNotIn("ready-to-ship", skill)
        self.assertIn("Do not emit final proof before closure", skill)

    def test_output_contains_review_and_semantic_balance(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for text in (
            "Resolution digest",
            "Selected lenses",
            "Standard CAS record IDs",
            "Added constructs and replacements",
            "Dominated constructs remaining",
        ):
            self.assertIn(text, skill)

    def test_detail_output_requires_bound_source_objects(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for text in (
            "run_digest:",
            "resolution_digest:",
            "actuation_run: {}",
            "review_resolution: {} | null",
            "evidence_folds: []",
            "cas_evidence: {} | null",
            "ship_record: {} | null",
            "basis IDs alone are not enough",
        ):
            with self.subTest(text=text):
                self.assertIn(text, skill)

    def test_publication_remains_ship_owned(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        agent = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("Do not publish", skill)
        self.assertIn("without changing closure or publication state", agent)


if __name__ == "__main__":
    unittest.main()
