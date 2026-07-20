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
        kernel_flat = " ".join(self.kernel.split())
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
            "duplicate-free",
            "`.git` root",
            "`.ledger/actuation/artifact-kernel` control root",
            "reserved under ASCII case-folding",
            "prefix-like siblings remain valid",
            "including `.`, cannot re-admit either root",
        ):
            with self.subTest(text=text):
                self.assertIn(text, kernel_flat)

    def test_high_critical_example_risk_is_explicit_and_class_law_scoped(self) -> None:
        corpus = self.skill_flat + " " + " ".join(self.kernel.split())
        for text in (
            "high-critical-example-proof-risk-authority/v1",
            "counterexample_class_ref:",
            "law_family:",
            "law_ref:",
            "no other family is eligible",
            "Generic source identity",
            "Construction prose never implies the grant",
            "remains unused only while the current Construction carries a direct strong",
            "pending risk-authority debt that blocks edits and closure",
        ):
            with self.subTest(text=text):
                self.assertIn(text, corpus)

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

    def test_semantic_successor_has_fresh_goal_lineage(self) -> None:
        corpus = self.skill_flat + " " + " ".join(self.kernel.split())
        for text in (
            "fresh Goal ID",
            "exactly one predecessor",
            "fresh initial Construction",
            "Actuating `open`",
            "never edit or reopen",
        ):
            with self.subTest(text=text):
                self.assertIn(text, corpus)

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
        self.assertIn("not an artifact, Goal field, durable marker", self.skill_flat)

    def test_protocol_is_evidence_owned_and_phase_four_is_explicit(self) -> None:
        for text in (
            "canonical Evidence Ledger",
            "goal_contract_registered",
            "goal_protocol_registered",
            "For an existing Goal ID",
            "For a new Goal ID with no canonical Evidence",
            "accepted execution route",
            "selector is transient control input",
            "first durable artifact-kernel protocol fact",
            "explicit `--goal GOAL_ID ... open` route selects `artifact-kernel-v1`",
            "inventory gates retirement of legacy writers",
            "Legacy `open` validates its selected store",
            "Any conflicting Evidence or invalid history blocks",
            "Never hand-write a marker or create a pre-registration peer artifact",
        ):
            with self.subTest(text=text):
                self.assertIn(text, self.skill_flat)
        self.assertIn("Evidence Ledger admits an existing goal", self.skill_flat)

    def test_native_ledger_use_declares_bootstrap(self) -> None:
        self.assertIn("$ledger ensure", self.skill)
        self.assertIn("ledger materialize goal-contract-v3 --input DRAFT", self.skill)
        self.assertIn("artifact_id` to JSON `null`", self.skill)


if __name__ == "__main__":
    unittest.main()
