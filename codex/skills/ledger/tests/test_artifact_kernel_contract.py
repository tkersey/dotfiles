from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
OWNERS = (SKILLS / "actuating" / "references" / "artifact-kernel.md").read_text(
    encoding="utf-8"
)
FLAT_OWNERS = " ".join(OWNERS.split())
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")


class ArtifactKernelContractTests(unittest.TestCase):
    def test_exposes_each_kernel_validator_once(self) -> None:
        for contract in (
            "goal-contract-v3",
            "counterexample-set",
            "construction-contract",
            "actuating-review-contract",
            "actuating-evidence-event",
            "actuating-closure-receipt",
            "ship-v1",
        ):
            command = f"ledger validate {contract} --input FILE|-"
            self.assertEqual(1, SKILL.count(command), command)

    def test_exposes_discardable_projections(self) -> None:
        for command in ("--help", "state", "decide"):
            self.assertIn(f"ledger --source actuation --goal GOAL_ID {command}", SKILL)
        self.assertNotIn("ledger --source actuation --goal GOAL_ID doctor", SKILL)
        self.assertIn("serialized receipt is a cache", SKILL)

    def test_ledger_does_not_take_semantic_or_effect_authority(self) -> None:
        normalized = " ".join(SKILL.split())
        for phrase in (
            "does not author Goal semantics",
            "classify Counterexamples",
            "select a Construction",
            "grant mutation",
            "perform public effects",
        ):
            self.assertIn(phrase, normalized)
        for phrase in (
            "sole per-goal semantic-authority artifact",
            "sole classified-bug artifact",
            "sole architecture-selection artifact",
            "sole mutable per-goal truth",
        ):
            self.assertIn(phrase, FLAT_OWNERS)

    def test_protocol_admission_is_owned_by_canonical_map(self) -> None:
        for phrase in (
            "goal_contract_registered",
            "goal_protocol_registered",
            "goal-protocol-registration/v1",
            "Same-protocol admission is idempotent",
            "artifact Evidence path is fixed",
            "ignored residue, never authority",
            "Invalid legacy history blocks",
        ):
            self.assertIn(phrase, FLAT_OWNERS)
        self.assertIn("../actuating/references/artifact-kernel.md", SKILL)
        self.assertFalse((ROOT / "references" / "artifact-kernel.md").exists())

    def test_legacy_and_post_closure_guards_remain(self) -> None:
        self.assertIn("Legacy read compatibility only", SKILL)
        self.assertIn("must not write either legacy artifact", SKILL)
        self.assertIn("defer this checkpoint", " ".join(SKILL.split()))
        self.assertIn("without taking semantic authority", AGENT)


if __name__ == "__main__":
    unittest.main()
