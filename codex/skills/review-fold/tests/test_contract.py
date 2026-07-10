from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_skill_is_classification_only(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("RF-v2", skill)
        self.assertIn("review-resolution/v1", skill)
        self.assertIn("never choose the patch", skill)
        self.assertNotIn("selected_work_node:", skill)
        self.assertNotIn("clean_run_accounting", skill)

    def test_agent_is_not_implicit_authority(self) -> None:
        agent = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("classify", agent)
        self.assertIn("without selecting repairs", agent)


if __name__ == "__main__":
    unittest.main()
