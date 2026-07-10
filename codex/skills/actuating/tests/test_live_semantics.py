from __future__ import annotations

import subprocess
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
DECISION_CONTRACT = ROOT / "references" / "decision-contract.yaml"
GOAL_ACTUATING = REPO / "codex/skills/goal-actuating/SKILL.md"
SEMANTICS = yaml.safe_load(
    (ROOT / "references/live-semantics.yaml").read_text(encoding="utf-8")
)["live_semantics"]


class LiveSemanticsTests(unittest.TestCase):
    def test_package_surface_is_exact_allowlist(self) -> None:
        expected = {
            "SKILL.md",
            "agents/openai.yaml",
            "references/live-semantics.yaml",
            "references/review-resolution.md",
            "references/closure.md",
            "references/decision-contract.yaml",
            "tools/actuating_gate.py",
            "tests/test_live_semantics.py",
            "tests/test_actuating_gate.py",
        }
        actual = {
            str(path.relative_to(ROOT))
            for path in ROOT.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(actual, expected)

    def test_runtime_vocabulary_contains_only_executable_step_effects(self) -> None:
        self.assertEqual(SEMANTICS["step_effects"], ["inspect", "edit", "verify"])
        self.assertNotIn("isomorphism", SEMANTICS)

    def test_mode_table_and_invocation_defaults(self) -> None:
        self.assertEqual(
            set(SEMANTICS["modes"]),
            {"implement", "triage", "remediation-plan", "review-closeout"},
        )
        self.assertEqual(SEMANTICS["safe_review_default"], "triage")
        self.assertEqual(
            SEMANTICS["invocation_defaults"],
            {
                "bare": [
                    "implement",
                    "ship",
                    "review-closeout",
                    "final-closure",
                ],
                "explicit-implement": ["implement"],
            },
        )
        material = {mode for mode, row in SEMANTICS["modes"].items() if row["material"]}
        self.assertEqual(material, {"implement", "review-closeout"})

    def test_authority_and_owner_table(self) -> None:
        objects = SEMANTICS["canonical_objects"]
        self.assertEqual(
            set(objects),
            {
                "actuation-run/v1",
                "review-resolution/v1",
                "closure-decision/v1",
            },
        )
        self.assertEqual(SEMANTICS["owners"]["public_effects"], "ship")
        self.assertEqual(SEMANTICS["owners"]["review_classifier"], "review-fold")
        self.assertEqual(SEMANTICS["owners"]["resolution"], "actuating")

    def test_cas_review_contract_is_standard_only(self) -> None:
        self.assertEqual(
            SEMANTICS["lens_contracts"],
            {"standard": "standard-review-v1"},
        )
        self.assertTrue(
            all(not value for value in SEMANTICS["change_surfaces"].values())
        )

    def test_closure_flow_ends_in_terminal_proof(self) -> None:
        flow = SEMANTICS["closure_flow"]
        self.assertEqual(
            flow["bare_lifecycle"],
            ["implement", "ship", "review-closeout", "final-closure"],
        )
        self.assertEqual(
            flow["ship_handoff"],
            {
                "when": "implementation-ready-to-ship",
                "action": "ship",
                "terminal": False,
                "records": "implementation-checkpoint/v1",
                "then": "same-run-review-closeout",
            },
        )
        self.assertEqual(
            flow["review_closeout"],
            {
                "requires_when": "publication-requested",
                "receipt": "pre-review-SHIP-v1",
                "before_repair_admission": [
                    "refresh-live-review-sources",
                    "review-fold",
                    "review-resolution",
                ],
                "after_edit": {
                    "unresolved": [
                        "evidence-fold",
                        "refresh-live-review-sources",
                        "review-fold",
                        "review-resolution",
                        "gate-derived-continuation",
                    ],
                    "resolved": [
                        "evidence-fold",
                        "current-resolved-refold",
                        "ship",
                        "reset-cas-credit",
                        "review-closeout",
                    ],
                },
                "then": "final-closure",
            },
        )
        self.assertEqual(flow["final_closure"], "closure-decision/v1")
        self.assertEqual(flow["terminal_view"], "final-proof-patch")

    def test_bare_lifecycle_is_bound_across_coordinator_contracts(self) -> None:
        contract = yaml.safe_load(DECISION_CONTRACT.read_text(encoding="utf-8"))[
            "skill_decision_contract"
        ]
        ship_route = next(
            row for row in contract["routes"] if row["route_id"] == "ACT-SHIP-HANDOFF"
        )
        authority = next(
            row for row in contract["clauses"] if row["clause_id"] == "ACT-AUTHORITY-001"
        )
        self.assertEqual(ship_route["terminal"], "no")
        self.assertIn("ACT-CLOSURE", authority["expected_routes"])
        goal_text = GOAL_ACTUATING.read_text(encoding="utf-8")
        self.assertIn(
            "implement ->\n$ship -> review-closeout -> final closure",
            goal_text,
        )
        self.assertIn("$actuating implement` runs only", goal_text)

    def test_documented_validate_run_uses_provisioned_wrapper(self) -> None:
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(
            "uv run --with pyyaml python \\\n"
            "     codex/skills/actuating/tools/actuating_gate.py validate-run",
            skill_text,
        )
        self.assertIn("--run RUN.yaml", skill_text)
        self.assertIn("--repo .", skill_text)
        self.assertNotIn(
            "Validate the run with `tools/actuating_gate.py validate-run`",
            skill_text,
        )

    def test_standard_only_reference_shapes_are_literal(self) -> None:
        closure = (ROOT / "references" / "closure.md").read_text(encoding="utf-8")
        resolution = (ROOT / "references" / "review-resolution.md").read_text(
            encoding="utf-8"
        )
        ship = (REPO / "codex/skills/ship/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("selectedLenses: [standard]", closure)
        self.assertIn("reviewLane: standard", closure)
        self.assertIn("lensContract: standard-review-v1", closure)
        self.assertIn("selected_lenses: [standard]", resolution)
        self.assertNotIn("complexity lens", resolution)
        self.assertIn("review-admission/v1", closure)
        self.assertIn("review_admission", closure)
        self.assertIn("review-admission:<admission_digest>", closure)
        self.assertIn("review.ship_receipt", closure)
        self.assertIn("same-publication-continuation/v1", closure)
        self.assertIn("evidence_fold_digest", closure)
        self.assertIn("resets CAS credit to zero", closure)
        self.assertNotIn("unpublished_repair_chain", closure)
        self.assertIn("blocked-index-observer-flags", closure)
        self.assertIn("actuation_binding:", ship)
        self.assertNotIn("review_contract_fingerprint", ship)
        self.assertIn("Never add or relabel", ship)
        self.assertIn("review.ship_receipt", ship)

    def test_review_repair_continuation_is_derived_and_refresh_bound(self) -> None:
        invariants = {
            row["id"]: row["statement"] for row in SEMANTICS["invariants"]
        }
        self.assertIn("live-review-source-before-admission", invariants)
        self.assertIn("same-publication-continuation-derived", invariants)
        self.assertIn("review-history-survives-reship", invariants)
        self.assertIn("terminal-resolution-exact", invariants)
        self.assertIn("repair-reship-resets-cas", invariants)
        self.assertIn("pr-publication-watermark-before-cas", invariants)
        self.assertIn(
            "gate-derived continuation receipt",
            invariants["same-publication-continuation-derived"],
        )
        self.assertIn(
            "three fresh ordered standard attempts",
            invariants["repair-reship-resets-cas"],
        )
        self.assertIn(
            "records at or before the greatest observation are superseded",
            invariants["pr-publication-watermark-before-cas"],
        )
        self.assertIn(
            "a regressing observation blocks closure",
            invariants["pr-publication-watermark-before-cas"],
        )
        self.assertIn(
            "strictly extending the finding set",
            invariants["review-history-survives-reship"],
        )

    def test_retired_protocol_is_absent_from_live_surfaces(self) -> None:
        paths = [
            REPO / "codex/AGENTS.md",
            ROOT / "SKILL.md",
            ROOT / "agents",
            ROOT / "references",
            ROOT / "tools",
            REPO / "codex/skills/goal-contract",
            REPO / "codex/skills/goal-actuating",
            REPO / "codex/skills/goal-grind",
            REPO / "codex/skills/goal-workgraph",
            REPO / "codex/skills/agent-loop-schemes",
            REPO / "codex/skills/review-fold",
            REPO / "codex/skills/complexity-mitigator",
            REPO / "codex/skills/proof-patch",
            REPO / "codex/skills/plan",
            REPO / "codex/skills/spec-pipeline",
        ]
        retired = (
            "FUSION-v1|ALSR-v1|HYL-v1|HSR-v1|ATCG-v1|APMA-v1|ASL-v1|"
            "direct.action fused exemption|actuation.slice|actuation_checkpoint"
        )
        result = subprocess.run(
            ["rg", "-n", "-i", retired, *map(str, paths)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_legacy_actuation_agents_are_deleted(self) -> None:
        self.assertEqual(
            list((REPO / "codex/agents").glob("actuation-*.toml")),
            [],
        )

    def test_mutation_contract_is_single_step(self) -> None:
        paths = [
            REPO / "codex/AGENTS.md",
            ROOT / "SKILL.md",
            ROOT / "references/live-semantics.yaml",
            REPO / "codex/skills/goal-actuating/SKILL.md",
            REPO / "codex/skills/goal-grind/SKILL.md",
        ]
        result = subprocess.run(
            [
                "rg",
                "-n",
                "-i",
                "safe frontier|file-disjoint selected|patch fanout|lead-selected frontier",
                *map(str, paths),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 1, result.stdout)


if __name__ == "__main__":
    unittest.main()
