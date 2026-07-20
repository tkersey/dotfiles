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

    def test_protocol_is_immutable_and_phase_four_is_opt_in(self) -> None:
        for phrase in (
            "Bind each goal immutably",
            "canonical Evidence Ledger",
            "Production is Phase 4 opt-in",
            "an explicit `--goal` admits a new artifact-kernel goal",
            "required before retiring legacy writers or changing the default route",
            "Never mix protocols, writers, artifacts, review credit, or closure rules",
            "frozen [legacy-actuating-v1 owner workflow]",
        ):
            if phrase == "Bind each goal immutably":
                self.assertIn("After registration, bind each goal immutably", FLAT_SKILL)
            elif phrase == "Production is Phase 4 opt-in":
                self.assertIn("production Phase 4", FLAT_SKILL)
            elif phrase == "an explicit `--goal` admits a new artifact-kernel goal":
                self.assertIn("explicit `--goal` selects artifact-kernel", FLAT_SKILL)
            else:
                self.assertIn(phrase, FLAT_SKILL)
        for phrase in (
            "A new goal selects its protocol before Goal compilation only from the accepted execution route",
            "pre-registration selector is transient and non-authorizing",
            "An unregistered Goal ID has no marker",
            "first durable `artifact-kernel-v1` fact",
            "validates the complete envelope, Goal, K0, subject, and authority before the first `goal_contract_registered` append",
        ):
            self.assertIn(phrase, " ".join((SKILL + OWNERS + COMMANDS).split()))
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

    def test_construction_exception_is_narrow_versioned_and_non_authorizing(self) -> None:
        flat = " ".join(CONSTRUCTION.split())
        for phrase in (
            "Omit `extensions` for every ordinary Construction",
            "high-critical-example-proof-exception/v1",
            "high-critical-example-proof-risk-authority/v1",
            "counterexample_class_ref",
            "example_obligation_ref",
            "compensating_obligation_ref",
            "stronger_proof_infeasibility_reason",
            "whose law appears in `architecture.governing_law_refs`",
            "The Construction cannot supply or copy authority",
            "exact matching `counterexample_class_ref`, eligible `law_family`, and example-obligation `law_ref`",
            "remain byte-identical in every successor",
            "actual architecture delta",
            "`replacement_ref` names that direct strong proof",
            "not a fifth artifact family, event, command, state machine, or mutation authority",
            "Both named obligations must still be discharged before closure",
            "architecture.canonical_owner` and `execution.owner_boundary` must be identical",
            "both `falsified_predecessor_claims` and `preserved_predecessor_claims` are empty",
            "`realization-repair` and `ablation-repair` also name at least one preserved predecessor claim",
            "ledger materialize construction-contract --input DRAFT",
            "re-author a current Counterexample Set from the still-applicable witness evidence",
            "pending risk-authority debt",
            "blocks edits and closure",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, flat)

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
        self.assertIn("capability-less `abort --step step-1` custody-recovery route", FLAT_COMMANDS)

    def test_review_binding_and_state_are_ledger_authored_projections(self) -> None:
        for phrase in (
            "actuating-review-instruction/v1",
            "ACTUATING-REVIEW-DISPATCH/v1",
            "append-only release registry",
            "registry-pinned lens-contract bytes",
            "pinned lens contract below governs this review",
            "top-level `instruction_path`",
            "body contains only `schema`, `campaign_id`, `initial_wave`, `lens`, `lens_contract_digest`, and `request_id`",
            "must not supply `instruction_digest`, `request_fingerprint`, or `target_fingerprint_digest`",
            "digest-only custody of the whole packet",
            "actuating-review-request/v1",
            "cas review_session target-identity",
            "CAS-TARGET-IDENTITY-v1",
            "Ledger-authored request fingerprint",
            "live, stored, and receipt target digests",
            "Historical replay verifies the durable joins without recomputing a live target",
            "actuating-kernel-state/v1",
            "`credit_current` exactly compares the admitted and live subject digests",
            "stale recovery bindings are suppressed without rewriting Evidence",
            "discharged and outstanding proof/retirement IDs",
            "one `next_transition` command/reason pair",
            "never exposes raw capability material or a capability digest",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, FLAT_COMMANDS)

    def test_review_findings_and_target_drift_are_evidence_owned(self) -> None:
        for phrase in (
            "omit `body.finding_refs`",
            "actuating-review-finding/v1",
            "Caller-authored, reordered, or substituted refs are rejected",
            "review-attempt-completed/v2",
            "review-transport-failed/v2",
            "persist the corresponding v3 terminal body",
            "no semantic or request-local recovery credit",
            "After every launched sibling terminalizes",
            "review-campaign-started/v3",
            "using the same campaign ID",
            "fresh concurrent 1+4 binding",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, FLAT_COMMANDS)
        flat_review = " ".join(REVIEW.split())
        self.assertIn("No prior auxiliary result or standard clean survives the restart", flat_review)
        self.assertIn("no review credit across a material subject change", flat_review)

    def test_frozen_goal_supersession_is_read_only_and_blocks_predecessor(self) -> None:
        for phrase in (
            "`goal_superseded` is read-only frozen Evidence",
            "goal-superseded/v1",
            "single predecessor ref and source digest",
            "paired pending step/capability invalidation",
            "projects the predecessor goal blocked",
            "No current writer emits this event",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, FLAT_COMMANDS)

    def test_ship_receipt_admission_is_complete_and_exact(self) -> None:
        self.assertIn("complete exact owner-issued `SHIP-v1` envelope", FLAT_COMMANDS)
        self.assertIn("partial fragment", FLAT_COMMANDS)
        self.assertIn("mismatched result/readiness pair", FLAT_COMMANDS)
        self.assertIn("digest-shaped `actuation_run_id`", FLAT_COMMANDS)
        self.assertIn("nonblank opaque historical run ID", FLAT_COMMANDS)
        self.assertIn("Read compatibility never makes that historical identity admissible", FLAT_COMMANDS)

    def test_ledger_validator_surface_is_owned_once(self) -> None:
        for command in (
            "goal-contract-v3", "counterexample-set", "construction-contract",
            "actuating-review-contract", "actuating-evidence-event",
            "actuating-closure-receipt", "ship-v1",
        ):
            self.assertEqual(1, LEDGER.count(f"ledger validate {command} --input FILE|-"))
        self.assertFalse((SKILLS / "ledger" / "references" / "artifact-kernel.md").exists())

    def test_ledger_materializer_is_pure_and_capability_probed(self) -> None:
        for command in (
            "ledger materialize goal-contract-v3 --input DRAFT",
            "ledger materialize counterexample-set --input DRAFT",
            "ledger materialize construction-contract --input DRAFT",
        ):
            self.assertEqual(1, LEDGER.count(command), command)
        flat = " ".join((SKILL + COMMANDS + LEDGER).split())
        self.assertIn("older partial CLI", flat)
        self.assertIn("reads or writes no `.ledger` store and grants no authority", flat)
        self.assertIn("example-proof-risk-authority-pending", flat)

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
