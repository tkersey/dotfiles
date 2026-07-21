import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
CONSTRUCTION = (ROOT / "references" / "construction-contract.md").read_text(
    encoding="utf-8"
)
DECISION = (ROOT / "references" / "decision-contract.yaml").read_text(
    encoding="utf-8"
)
UNIVERSALIST = (SKILLS / "universalist" / "SKILL.md").read_text(encoding="utf-8")
UNI_DECISION = (SKILLS / "universalist" / "references" / "decision-contract.yaml").read_text(encoding="utf-8")
REDUCE = (SKILLS / "reduce" / "SKILL.md").read_text(encoding="utf-8")
RC = (SKILLS / "reduce" / "references" / "reduction-certificate.md").read_text(encoding="utf-8")


class ReduceRoleContractTests(unittest.TestCase):
    def test_composed_roles_are_ordered_and_non_authoritative(self) -> None:
        for phrase in (
            "`nominate -> challenge once ->\nadjudicate`",
            "Actuating alone performs the adjudication",
            "Invoke `$reduce` exactly once for that candidate version",
        ):
            self.assertIn(phrase, SKILL)
        for phrase in (
            "`nominate -> challenge once -> adjudicate\n-> one Construction`",
            "an independently useful Reduction\nCertificate may appear only in `supporting_refs`",
            "never starts recursive Universalist/Reduce competition",
        ):
            self.assertIn(phrase, CONSTRUCTION)
        self.assertIn("Universalist nominates and Reduce challenges once", DECISION)

    def test_composed_analysis_needs_no_duplicate_artifact(self) -> None:
        self.assertIn("the Construction is the decision carrier", UNIVERSALIST)
        self.assertIn("decision_receipt: optional", UNI_DECISION)
        self.assertIn("return exactly one compact challenge", REDUCE)
        self.assertIn("the compact Reduction Challenge is sufficient", RC)


if __name__ == "__main__":
    unittest.main()
