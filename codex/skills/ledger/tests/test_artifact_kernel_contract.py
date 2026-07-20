from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
REPO = ROOT.parents[2]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
OWNERS = (SKILLS / "actuating" / "references" / "artifact-kernel.md").read_text(
    encoding="utf-8"
)
FLAT_OWNERS = " ".join(OWNERS.split())
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
ROOT_AGENTS = (REPO / "AGENTS.md").read_text(encoding="utf-8")
CODEX_AGENTS = (REPO / "codex" / "AGENTS.md").read_text(encoding="utf-8")


class ArtifactKernelContractTests(unittest.TestCase):
    def test_exposes_pure_materializer_once_per_semantic_document(self) -> None:
        for contract in (
            "goal-contract-v3",
            "counterexample-set",
            "construction-contract",
        ):
            command = f"ledger materialize {contract} --input DRAFT"
            self.assertEqual(1, SKILL.count(command), command)
        normalized = " ".join(SKILL.split())
        self.assertIn("artifact_id` is JSON `null`", normalized)
        self.assertIn("reads or writes no `.ledger` store and grants no authority", normalized)
        self.assertIn("older partial CLI", normalized)

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
        self.assertIn("closure -> handoff/report -> source-memory evaluation", SKILL)
        normalized = " ".join(SKILL.split())
        self.assertIn("must not delay code closure, a commit, or a PR handoff", normalized)
        self.assertIn("cannot gate, delay, invalidate, or roll back delivery", normalized)
        self.assertIn("without taking semantic authority", AGENT)

    def test_source_memory_checkpoint_follows_handoff_and_never_gates_delivery(self) -> None:
        for doctrine in (ROOT_AGENTS, CODEX_AGENTS):
            normalized = " ".join(doctrine.split())
            self.assertIn(
                "After a terminal `complete` or `ready-to-ship` closure decision",
                normalized,
            )
            self.assertIn(
                "closure -> handoff/report -> source-memory evaluation",
                normalized,
            )
            self.assertIn(
                "not a prerequisite for and must not delay code closure, a Codex-made commit, or a PR handoff",
                normalized,
            )
            self.assertIn(
                "re-establish closure and complete the resulting handoff or report before reevaluating",
                normalized,
            )
            self.assertIn(
                "source-memory status cannot gate, delay, invalidate, or roll back delivery",
                normalized,
            )
            self.assertIn(
                "Negative Ledger pre-route gate may block a selected route before execution",
                normalized,
            )

    def test_actuation_store_protocols_and_reserved_verifier_are_explicit(self) -> None:
        normalized = " ".join(SKILL.split())
        self.assertIn(
            "`.ledger/actuation/events.jsonl` is the default frozen `legacy-actuating-v1` persistent adapter",
            normalized,
        )
        self.assertIn(
            "`.ledger/actuation/artifact-kernel/evidence.jsonl` is the fixed `artifact-kernel-v1` Evidence Ledger adapter",
            normalized,
        )
        self.assertIn("`subject_digest`, and `verifier`", FLAT_OWNERS)

    def test_current_ship_validation_is_stricter_than_frozen_read_compatibility(self) -> None:
        normalized = " ".join(SKILL.split())
        self.assertIn("`ledger validate ship-v1` is the current-write validator", normalized)
        self.assertIn("digest-shaped Actuating identity", normalized)
        self.assertIn("relaxes only the historical run identity", normalized)
        self.assertIn("grants no current write authority", normalized)


if __name__ == "__main__":
    unittest.main()
