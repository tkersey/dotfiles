from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.contract = (ROOT / "references" / "artifact-kernel-v1.md").read_text(encoding="utf-8")
        cls.skill_flat = " ".join(cls.skill.split())
        cls.contract_flat = " ".join(cls.contract.split())

    def test_v3_is_the_only_goal_contract(self) -> None:
        for phrase in (
            "goal-contract/v3",
            "semantic_author: goal-contract",
            "content-addressed `artifact_id`",
            "Treat every materialized Goal as immutable",
        ):
            self.assertIn(phrase, self.skill + self.contract)
        self.assertFalse((ROOT / "references" / "legacy-gc-v2.md").exists())

    def test_goal_identity_is_stable_and_cli_safe(self) -> None:
        for phrase in (
            "[A-Za-z0-9][A-Za-z0-9._-]{0,127}",
            "stable opaque identity",
            "Never derive it from mutable Goal content",
            "same `goal_id`",
        ):
            self.assertIn(phrase, self.skill + self.contract)

    def test_goal_is_materialized_before_actuating_handoff(self) -> None:
        for phrase in (
            "append --input <goal-contract-draft.json>",
            "Require `actuating-append-result/v1`",
            "equal to `artifact.artifact_id`",
            "registration `event_digest`",
            "returned immutable artifact and exact identity",
        ):
            self.assertIn(phrase, self.skill_flat)
        self.assertLess(
            self.skill_flat.index("append --input <goal-contract-draft.json>"),
            self.skill_flat.index("returned immutable artifact and exact identity"),
        )

    def test_authority_scope_laws_and_acceptance_are_complete(self) -> None:
        for phrase in (
            "objective:",
            "authority:",
            "scope:",
            "compatibility:",
            "laws:",
            "acceptance:",
            "execution_authority_digest:",
            "required_observation:",
            "required_proof_kinds:",
        ):
            self.assertIn(phrase, self.contract)

    def test_goal_records_but_does_not_grant_or_select(self) -> None:
        for phrase in (
            "never grants mutation",
            "selects a Construction",
            "chooses an operation",
            "records mutable progress",
        ):
            self.assertIn(phrase, self.skill_flat)
        self.assertIn("it does not author semantics or grant authority", self.skill_flat)

    def test_source_authority_and_successor_lineage_are_explicit(self) -> None:
        self.assertIn("Separate semantic source authority from execution authority", self.skill_flat)
        self.assertIn("exactly one predecessor `artifact_id`", self.skill_flat)
        self.assertIn("same `goal_id`", self.skill_flat)
        self.assertIn("new content-addressed `artifact_id`", self.skill_flat)
        self.assertIn("Never edit the predecessor in place", self.skill_flat)
        self.assertNotIn("fresh Goal ID", self.skill + self.contract)

    def test_architecture_counterexamples_and_state_are_excluded(self) -> None:
        for phrase in (
            "candidate constructions",
            "selected architecture",
            "Counterexample classification",
            "review bindings or attempts",
            "mutable progress",
            "closure state",
        ):
            self.assertIn(phrase, self.skill_flat)

    def test_paths_reserve_git_and_control_storage(self) -> None:
        for phrase in (
            "duplicate-free canonical literal",
            "reserved under ASCII case-folding",
            "Root scope cannot re-admit them",
        ):
            self.assertIn(phrase, self.contract_flat)

    def test_no_retired_goal_contract_surface_remains(self) -> None:
        doctrine = self.skill + self.contract
        for retired in ("GC-v2", "legacy-actuating-v1", "review-resolution/v1"):
            self.assertNotIn(retired, doctrine)


if __name__ == "__main__":
    unittest.main()
