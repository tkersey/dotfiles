from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
OWNERS = (SKILLS / "actuating" / "references" / "artifact-kernel.md").read_text(encoding="utf-8")
FLAT_SKILL = " ".join(SKILL.split())
ACTUATION = SKILL.split("## Actuating Artifact Kernel boundary", 1)[1].split(
    "## Source-memory lifecycle checkpoint", 1
)[0]
FLAT_ACTUATION = " ".join(ACTUATION.split())


class ArtifactKernelContractTests(unittest.TestCase):
    def test_generated_table_projects_actuating_owned_law(self) -> None:
        for phrase in (
            "generated implementation table",
            "command routing, accepted artifact and event shapes",
            "does not own or duplicate Actuating's lifecycle, review, or closure laws",
            "canonical Review Contract is an Actuating-owned input",
            "must not select or reconstruct the contract from hardcoded policy",
        ):
            self.assertIn(phrase, FLAT_ACTUATION)
        self.assertNotIn("sole Ledger-side inventory", FLAT_SKILL)

    def test_ledger_operations_are_structural_and_requested(self) -> None:
        for phrase in (
            "materialize canonical content-addressed documents",
            "validate document, event, and supporting-receipt structure",
            "append immutable observations",
            "replay recorded observations",
            "project requested structural facts",
            "`state` and `project` emit disposable structural aids",
        ):
            self.assertIn(phrase, FLAT_ACTUATION)

    def test_actuation_store_is_per_goal_evidence(self) -> None:
        self.assertIn(".ledger/actuation/<safe-goal-id>/evidence.jsonl", SKILL)
        self.assertNotIn(".ledger/actuation/events.jsonl", SKILL)

    def test_ledger_takes_no_execution_review_ship_or_closure_authority(self) -> None:
        for phrase in (
            "executes or edits repository work",
            "dispatches reviews or reads CAS verdict semantics",
            "classifies CAS owner facts as a semantic verdict or computes review credit",
            "interprets Ship receipts as publication truth",
            "classifies Counterexamples or selects a repair",
            "selects a Construction or proof strategy",
            "chooses Actuating's next action",
            "grants mutation authority",
            "emits `continue`, `ready-to-ship`, `complete`, or `blocked`",
            "authors an `actuating-closure-receipt/v1`",
        ):
            self.assertIn(phrase, FLAT_ACTUATION)

    def test_semantic_owners_remain_outside_ledger(self) -> None:
        for phrase in (
            "Actuating owns correct-by-construction implementation",
            "`$review-fold` owns Counterexample classification",
            "CAS owns its attempts and structured receipts",
            "`$ship` alone owns public effects",
        ):
            self.assertIn(phrase, FLAT_SKILL)
        self.assertIn("four authoritative per-goal artifact families", OWNERS)

    def test_structural_validation_grants_no_semantic_credit(self) -> None:
        self.assertIn("not semantic truth, mutation authority, review credit", FLAT_SKILL)
        self.assertIn("supporting evidence until Actuating evaluates it", FLAT_SKILL)

    def test_structural_aids_do_not_claim_actuating_outputs(self) -> None:
        for phrase in (
            "semantic workflow state",
            "review credit",
            "a next action",
            "a closure verdict",
        ):
            self.assertIn(phrase, FLAT_ACTUATION)
        self.assertNotIn("Ledger computes review credit", FLAT_ACTUATION)
        self.assertNotIn("Ledger authors the closure receipt", FLAT_ACTUATION)

    def test_unrelated_ledger_planes_remain_present(self) -> None:
        for heading in (
            "## Source-memory lifecycle checkpoint",
            "## Universalist Plan Workflow",
        ):
            self.assertIn(heading, SKILL)

    def test_retired_actuating_validators_are_absent(self) -> None:
        for retired in (
            "GC-v2",
            "RF-v2",
            "actuation-review-policy",
            "actuating-legacy-cutover",
            "closure-decision/v1",
        ):
            self.assertNotIn(retired, SKILL)


if __name__ == "__main__":
    unittest.main()
