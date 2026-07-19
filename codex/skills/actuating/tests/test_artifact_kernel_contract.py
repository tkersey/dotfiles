#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


SKILL = read(ROOT / "SKILL.md")
OWNERS = read(ROOT / "references" / "artifact-kernel.md")
CONSTRUCTION = read(ROOT / "references" / "construction-contract.md")
REVIEW = read(ROOT / "references" / "review-contract.md")
CLOSURE = read(ROOT / "references" / "closure.md")
COMMANDS = read(ROOT / "references" / "kernel-commands.md")
LEGACY = read(ROOT / "references" / "legacy-actuating-v1.md")
REVIEW_FOLD = read(SKILLS / "review-fold" / "SKILL.md")
LEDGER = read(SKILLS / "ledger" / "SKILL.md")
SHIP = read(SKILLS / "ship" / "SKILL.md")
SHIP_RECORD = read(SKILLS / "ship" / "references" / "ship-record.md")
FLAT_SKILL = " ".join(SKILL.split())
FLAT_OWNERS = " ".join(OWNERS.split())
FLAT_COMMANDS = " ".join(COMMANDS.split())


class ArtifactKernelSkillContractTests(unittest.TestCase):
    def test_five_public_modes_and_safe_triage(self) -> None:
        for mode in (
            "Bare `$actuating` or `/goal $actuating`",
            "`$actuating implement`",
            "`$actuating triage`",
            "`$actuating remediation-plan`",
            "`$actuating review-closeout`",
        ):
            self.assertIn(mode, SKILL)
        self.assertIn(
            "An unqualified request to review, inspect, audit, or classify selects `triage`",
            FLAT_SKILL,
        )
        self.assertLessEqual(len(SKILL.splitlines()), 180)

    def test_exactly_four_authoritative_families_have_named_owners(self) -> None:
        expected = {
            "goal-contract/v3": "$goal-contract",
            "counterexample-set/v1": "$review-fold",
            "construction-contract/v1": "$actuating",
            "actuating-evidence-event/v1": "domain owner",
        }
        for family, owner in expected.items():
            self.assertIn(family, SKILL)
            self.assertIn(family, OWNERS)
            self.assertIn(owner, OWNERS)
        self.assertIn("exactly four authoritative per-goal artifact families", SKILL)
        self.assertIn("Evidence Ledger is the sole mutable per-goal truth", FLAT_OWNERS)

    def test_protocol_is_immutable_and_legacy_is_frozen(self) -> None:
        for phrase in (
            "Bind each goal immutably",
            "canonical Evidence Ledger",
            "Production remains at migration Phase 3",
            "new artifact-kernel goal admission build-disabled",
            "Phase 4 remains blocked",
            "Never mix protocols, writers, artifacts, review credit, or closure rules",
            "frozen [legacy-actuating-v1 owner workflow]",
        ):
            self.assertIn(phrase, FLAT_SKILL)
        self.assertIn("already marked with that protocol", LEGACY)
        self.assertIn("never an input, authority source", LEGACY)
        for phrase in (
            "goal_contract_registered",
            "goal_protocol_registered",
            "construction_ref: null",
            "current repository subject digest",
            '{"protocol":"legacy-actuating-v1","schema":"goal-protocol-registration/v1"}',
            "Invalid legacy history blocks",
            "ignored residue, never authority",
        ):
            self.assertIn(phrase, FLAT_OWNERS)
        self.assertFalse((ROOT / "references" / "live-semantics.yaml").exists())

    def test_owner_boundaries_are_exact(self) -> None:
        self.assertIn("sole per-goal semantic-authority artifact", OWNERS)
        self.assertIn("sole classified-bug artifact", OWNERS)
        self.assertIn("sole architecture-selection artifact", OWNERS)
        self.assertIn("Ledger's Construction-bound handlers", SKILL)
        self.assertIn("`$goal-actuating`", LEGACY)
        self.assertIn("`$goal-grind`", LEGACY)
        self.assertIn("sole public-effect owner", SHIP)
        self.assertIn("does not take the semantic owner's authority", FLAT_OWNERS)

    def test_counterexample_identity_is_law_and_boundary_owned(self) -> None:
        self.assertIn(
            "class identity = governing law + semantic boundary + discrepancy + applicability",
            REVIEW_FOLD,
        )
        for transient in ("filenames", "attempt IDs", "publication epochs", "proposed patch"):
            self.assertIn(transient, REVIEW_FOLD)
        self.assertIn("successor Construction Contract before mutation", REVIEW_FOLD)

    def test_construction_review_and_closure_link_to_their_owners(self) -> None:
        self.assertIn("sole architecture-selection artifact", CONSTRUCTION)
        self.assertIn("representation\n> total-transition", CONSTRUCTION)
        self.assertIn("Launch standard plus four auxiliaries concurrently", REVIEW)
        self.assertIn("five", REVIEW)
        self.assertIn("Closure is a deterministic projection", CLOSURE)
        for link in ("construction-contract.md", "review-contract.md", "closure.md"):
            self.assertIn(link, OWNERS)

    def test_ship_v1_projection_is_exact_and_ship_owned(self) -> None:
        equations = (
            "actuation_binding.actuation_run_id = closure_receipt.receipt_id",
            "actuation_binding.state_fingerprint = closure_receipt.subject_digest",
        )
        for equation in equations:
            self.assertIn(equation, SKILL)
            self.assertIn(equation, SHIP)
        self.assertIn("exact two-field", SHIP_RECORD)
        self.assertIn("copies it, and never synthesizes or relabels it", " ".join(SHIP_RECORD.split()))

    def test_ledger_commands_are_one_internal_projection(self) -> None:
        self.assertIn("routing table is the single command inventory", COMMANDS)
        self.assertIn("artifact-kernel `--path` is rejected", FLAT_COMMANDS)
        for command in (
            "open", "register-construction", "register-counterexamples", "append",
            "prepare", "record", "execute", "observe", "abort", "state", "decide",
        ):
            self.assertIn(command, COMMANDS)
        self.assertNotIn("\nclose\n", COMMANDS)
        self.assertNotIn("`recover --step", COMMANDS)
        self.assertNotIn("goal-1 doctor", COMMANDS)
        self.assertNotIn("| `path` |", COMMANDS)
        self.assertIn("operation_observation_reserved", OWNERS)
        self.assertIn("After observation reservation, recovery is not legal", FLAT_COMMANDS)

    def test_ledger_validator_surface_is_owned_once(self) -> None:
        for command in (
            "goal-contract-v3", "counterexample-set", "construction-contract",
            "actuating-review-contract", "actuating-evidence-event",
            "actuating-closure-receipt", "ship-v1",
        ):
            self.assertEqual(1, LEDGER.count(f"ledger validate {command} --input FILE|-"))
        self.assertFalse((SKILLS / "ledger" / "references" / "artifact-kernel.md").exists())

    def test_decision_contract_is_seq_valid_skdc_v1(self) -> None:
        contract = ROOT / "references" / "decision-contract.yaml"
        result = subprocess.run(
            ["seq", "skill-contract", "validate", "--file", str(contract), "--format", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)["skill_contract"]
        self.assertTrue(payload["valid"])
        self.assertEqual("actuating", payload["skill"])
        self.assertEqual([], payload["validation_codes"])


if __name__ == "__main__":
    unittest.main()
