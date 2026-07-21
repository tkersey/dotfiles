import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
CONSTRUCTION = (ROOT / "references" / "construction-contract.md").read_text(
    encoding="utf-8"
)
DECISION = (ROOT / "references" / "decision-contract.yaml").read_text(
    encoding="utf-8"
)


class ReduceRoleContractTests(unittest.TestCase):
    def test_reduce_is_bounded_supporting_evidence(self) -> None:
        for phrase in (
            "`$reduce` may supply non-authoritative minimization",
            "Reduction Certificate is supporting evidence only",
            "Neither review prose nor\n`$reduce` selects a Construction",
            "invoke `$reduce` for exactly one\nproof-preserving reduction pass",
        ):
            self.assertIn(phrase, SKILL)
        for phrase in (
            "`$reduce` may supply the evidence for `Why not smaller?`",
            "Reduction Certificate belongs only in `supporting_refs`",
            "`$reduce` for exactly one proof-preserving reduction pass",
        ):
            self.assertIn(phrase, CONSTRUCTION)
        self.assertIn("Reduce remains non-authoritative supporting evidence", DECISION)
        self.assertIn("$reduce grants mutation or bypasses Actuating selection", DECISION)


if __name__ == "__main__":
    unittest.main()
