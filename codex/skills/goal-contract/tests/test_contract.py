from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.skill_flat = " ".join(cls.skill.split())
        cls.kernel = (ROOT / "references" / "artifact-kernel-v1.md").read_text(
            encoding="utf-8"
        )
        cls.legacy = (ROOT / "references" / "legacy-gc-v2.md").read_text(
            encoding="utf-8"
        )

    def test_artifact_kernel_selects_goal_contract_v3(self) -> None:
        for text in (
            "artifact-kernel-v1",
            "goal-contract/v3",
            "canonical JSON",
            "content-addressed `artifact_id`",
            "unknown fields",
            "predecessor_refs",
            "storage_mutated: false | true",
        ):
            with self.subTest(text=text):
                self.assertIn(text, self.skill + self.kernel)

    def test_v3_contains_only_the_authority_payload_sections(self) -> None:
        for text in (
            "objective:",
            "authority:",
            "scope:",
            "compatibility:",
            "laws:",
            "acceptance:",
            "required_outcomes:",
            "execution_authority_digest:",
            "required_observation:",
            "required_proof_kinds:",
        ):
            with self.subTest(text=text):
                self.assertIn(text, self.kernel)

    def test_semantic_authority_does_not_become_execution_authority(self) -> None:
        for text in (
            "only per-goal semantic-authority document",
            "Set `semantic_author` to `goal-contract`",
            "never grants mutation",
            "Ledger validation establishes only",
            "`$plan` may supply execution policy but never mutation authority",
            "records accepted permission",
        ):
            with self.subTest(text=text):
                self.assertIn(text, self.skill + self.kernel)

    def test_construction_and_mutable_state_are_excluded(self) -> None:
        for text in (
            "candidate constructions",
            "implementation architecture",
            "review request state",
            "attempt history",
            "mutable progress",
            "closure state",
        ):
            with self.subTest(text=text):
                self.assertIn(text, self.skill_flat)

    def test_gc_v2_is_frozen_and_protocol_is_not_mixed(self) -> None:
        self.assertIn("version: GC-v2", self.legacy)
        self.assertIn("legacy-actuating-v1", self.legacy)
        self.assertIn("Never write a GC-v2", self.skill)
        self.assertIn("do not add it as an unknown Goal Contract field", self.skill_flat)

    def test_protocol_is_evidence_owned_and_phase_three_is_fail_closed(self) -> None:
        for text in (
            "canonical Evidence Ledger",
            "goal_contract_registered",
            "goal_protocol_registered",
            "Production Phase 3 blocks every new artifact-kernel goal",
            "Legacy `open` validates its selected store",
            "invalid history or a conflicting protocol blocks",
        ):
            with self.subTest(text=text):
                self.assertIn(text, self.skill_flat)
        self.assertIn("Evidence Ledger admits the existing goal", self.skill_flat)

    def test_native_ledger_use_declares_bootstrap(self) -> None:
        self.assertIn("$ledger ensure", self.skill)


if __name__ == "__main__":
    unittest.main()
