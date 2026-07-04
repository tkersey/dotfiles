#!/usr/bin/env -S uv run python
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "actuation_terminal_gate.py"
ASSETS = ROOT / "assets"
SPEC = importlib.util.spec_from_file_location("actuation_terminal_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ActuationTerminalGateTests(unittest.TestCase):
    def context(self, name: str = "terminal-context.proof-only.example.json"):
        return json.loads((ASSETS / name).read_text())["actuation_terminal_context"]

    def decision(self, name: str):
        return json.loads((ASSETS / name).read_text())

    def fixture(self, name: str):
        return json.loads((ASSETS / name).read_text())

    def assert_blocks_with(self, context, reason: str, next_owner: str) -> None:
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["can_mark_goal_complete"], "no")
        self.assertEqual(body["next_owner"], next_owner)
        self.assertIn(reason, body["blocked_reasons"])

    def test_proof_only_context_can_complete(self) -> None:
        decision = MODULE.make_decision(self.context())
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertEqual(body["can_mark_goal_complete"], "yes")
        self.assertEqual(body["next_owner"], "none")

    def test_current_proof_patch_allows_tracked_dirty_binding(self) -> None:
        context = deepcopy(self.context())
        context["artifact_scope"]["dirty_state"] = "tracked-dirty"
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertEqual(body["current_artifact_binding"]["dirty_state"], "tracked-dirty")

    def test_original_regression_is_blocked(self) -> None:
        decision = MODULE.make_decision(self.context("terminal-context.regression.example.json"))
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["can_mark_goal_complete"], "no")
        self.assertEqual(body["next_owner"], "$cas")
        self.assertIn("cas-review-blocked", body["blocked_reasons"])
        self.assertIn("cas.clean_runs:0-of-3", body["blocked_reasons"])
        self.assertIn("final_report.normalized_cas_clean_runs:not-satisfied", body["blocked_reasons"])

    def test_advisory_would_block_matches_seq_fixture_expectation(self) -> None:
        fixture = self.fixture("terminal-context.advisory-would-block.example.json")
        advisory = MODULE.make_advisory(fixture["actuation_terminal_context"])
        self.assertEqual(advisory["verdict"], "advisory")
        self.assertEqual(advisory["would_block"], fixture["advisory_expectation"]["would_block"])
        self.assertEqual(
            advisory["would_block_reasons"],
            fixture["advisory_expectation"]["would_block_reasons"],
        )
        self.assertEqual(
            advisory["can_mark_goal_complete"],
            fixture["advisory_expectation"]["can_mark_goal_complete"],
        )
        self.assertEqual(advisory["next_owner"], fixture["advisory_expectation"]["next_owner"])

    def test_advisory_cli_would_block_is_non_blocking(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "validate",
                "--context",
                str(ASSETS / "terminal-context.advisory-would-block.example.json"),
                "--mode",
                "advisory",
                "--format",
                "json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        body = json.loads(result.stdout)
        self.assertEqual(body["verdict"], "advisory")
        self.assertTrue(body["would_block"])
        self.assertFalse(body["can_mark_goal_complete"])

    def test_hard_decision_blocks_advisory_fixture(self) -> None:
        fixture = self.fixture("terminal-context.advisory-would-block.example.json")
        decision = MODULE.make_decision(fixture["actuation_terminal_context"])
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["can_mark_goal_complete"], "no")
        self.assertEqual(body["next_owner"], fixture["advisory_expectation"]["next_owner"])
        for reason in fixture["advisory_expectation"]["would_block_reasons"]:
            self.assertIn(reason, body["blocked_reasons"])

    def test_review_closeout_governance_accepts_cas_review_fold_and_resolution(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "review_closeout": {
                "required": "yes",
                "cas_reviewed": "yes",
                "review_folded": "yes",
                "review_closeout_obeyed": "yes",
            }
        }
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertEqual(body["can_mark_goal_complete"], "yes")

    def test_review_closeout_governance_blocks_without_cas_review_fold_or_resolution(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "review_closeout": {
                "required": "yes",
                "cas_reviewed": "no",
                "review_folded": "yes",
                "review_closeout_obeyed": "yes",
            }
        }
        self.assert_blocks_with(context, "cas-review-blocked", "$cas")

    def test_legacy_resolve_governance_is_still_accepted(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "resolve": {
                "required": "yes",
                "cas_reviewed": "yes",
                "review_folded": "yes",
                "resolve_obeyed": "yes",
            }
        }
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertEqual(body["can_mark_goal_complete"], "yes")

    def test_legacy_review_fix_governance_still_blocks_without_resolution(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "review_fix": {
                "required": "yes",
                "cas_reviewed": "yes",
                "review_folded": "yes",
                "resolve_passed": "no",
            }
        }
        self.assert_blocks_with(context, "cas-review-blocked", "$cas")

    def test_advisory_direct_action_fused_exempts_loop_receipts(self) -> None:
        fixture = self.fixture("terminal-context.advisory-fused.example.json")
        advisory = MODULE.make_advisory(fixture["actuation_terminal_context"])
        self.assertEqual(advisory, {
            "verdict": "advisory",
            "would_block": False,
            "would_block_reasons": [],
            "can_mark_goal_complete": True,
            "next_owner": "none",
        })

    def test_hard_direct_action_fused_can_complete(self) -> None:
        fixture = self.fixture("terminal-context.advisory-fused.example.json")
        decision = MODULE.make_decision(fixture["actuation_terminal_context"])
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertEqual(body["can_mark_goal_complete"], "yes")
        self.assertEqual(body["next_owner"], "none")

    def test_advisory_st_governed_exempts_loop_receipts(self) -> None:
        fixture = self.fixture("terminal-context.advisory-st-governed.example.json")
        advisory = MODULE.make_advisory(fixture["actuation_terminal_context"])
        self.assertEqual(advisory, {
            "verdict": "advisory",
            "would_block": False,
            "would_block_reasons": [],
            "can_mark_goal_complete": True,
            "next_owner": "none",
        })

    def test_hard_st_governed_current_receipt_can_complete(self) -> None:
        fixture = self.fixture("terminal-context.advisory-st-governed.example.json")
        decision = MODULE.make_decision(fixture["actuation_terminal_context"])
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertEqual(body["can_mark_goal_complete"], "yes")
        self.assertEqual(body["next_owner"], "none")

    def test_hard_st_governed_requires_current_receipt(self) -> None:
        context = deepcopy(self.context("terminal-context.advisory-st-governed.example.json"))
        context["loop_governance"]["st_control"]["current"] = "no"
        self.assert_blocks_with(context, "st-authority-blocked", "$st")

    def test_hard_stale_loop_contract_blocks_completion(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "material": "yes",
            "alsr": {"required": "yes", "present": "yes", "current": "no"},
            "hyl": {"required": "yes", "present": "yes", "current": "yes"},
            "hsr": {
                "terminal_present": "yes",
                "latest_fold_current_artifact_bound": "yes",
                "material_mutations": [{"has_hsr": "yes"}],
            },
        }
        self.assert_blocks_with(context, "blocked-loop-contract-stale", "$goal-actuating")

    def test_hard_missing_frontier_blocks_completion(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "material": "yes",
            "alsr": {"required": "yes", "present": "yes", "current": "yes"},
            "hyl": {"required": "yes", "present": "yes", "current": "yes"},
            "hsr": {
                "terminal_present": "yes",
                "latest_fold_current_artifact_bound": "yes",
                "material_mutations": [{"has_unfold": "no", "has_action": "yes", "has_fold": "yes"}],
            },
        }
        self.assert_blocks_with(context, "blocked-hylo-frontier-missing", "$goal-actuating")

    def test_hard_missing_fold_blocks_completion(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "material": "yes",
            "alsr": {"required": "yes", "present": "yes", "current": "yes"},
            "hyl": {"required": "yes", "present": "yes", "current": "yes"},
            "hsr": {
                "terminal_present": "yes",
                "latest_fold_current_artifact_bound": "yes",
                "material_mutations": [{"has_unfold": "yes", "has_action": "yes", "has_fold": "no"}],
            },
        }
        self.assert_blocks_with(context, "blocked-hylo-fold-missing", "$goal-actuating")

    def test_hard_missing_terminal_hsr_blocks_completion(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "material": "yes",
            "alsr": {"required": "yes", "present": "yes", "current": "yes"},
            "hyl": {"required": "yes", "present": "yes", "current": "yes"},
            "hsr": {
                "terminal_present": "no",
                "latest_fold_current_artifact_bound": "yes",
                "material_mutations": [{"has_hsr": "yes"}],
            },
        }
        self.assert_blocks_with(context, "blocked-hylo-terminal-missing", "$goal-actuating")

    def test_hard_proof_stale_blocks_completion(self) -> None:
        context = deepcopy(self.context())
        context["proof"] = {"required": "yes", "matches_verifier": "no"}
        self.assert_blocks_with(context, "proof-stale", "$goal-grind")

    def test_hard_side_effect_boundary_blocks_completion(self) -> None:
        context = deepcopy(self.context())
        context["side_effect_boundary"] = {"respected": "no"}
        self.assert_blocks_with(context, "side-effect-boundary-violated", "$ship")

    def test_proof_patch_closure_requires_proof_patch_receipt(self) -> None:
        context = deepcopy(self.context())
        context["proof_patch"] = {}
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "continue")
        self.assertEqual(body["next_owner"], "$proof-patch")
        self.assertIn("proof_patch.required:missing-for-proof-patch-closure", body["continue_reasons"])

    def test_ship_complete_requires_delivery_evidence(self) -> None:
        context = deepcopy(self.context())
        context["closure_candidate"] = "ship-complete"
        context["delivery"] = {}
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["next_owner"], "$ship")
        self.assertIn("delivery.pr_intent:missing-for-ship-complete", body["blocked_reasons"])

    def test_ship_complete_accepts_wrapped_add_v1_handoff(self) -> None:
        context = deepcopy(self.context())
        context["closure_candidate"] = "ship-complete"
        context["delivery"] = {
            "pr_intent": "yes",
            "publication_required": "yes",
            "add_v1_decision": json.loads((ASSETS / "add-v1.handoff.example.json").read_text()),
            "ship_result": {
                "present": "yes",
                "current": "yes",
                "pr_url": "https://github.com/tkersey/example/pull/1",
                "ref": "ship:example",
            },
        }
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertIn("add_v1_delivery_decision", body["required_receipts"])
        self.assertIn("ship_result", body["required_receipts"])

    def test_ship_complete_rejects_stale_wrapped_add_v1_handoff(self) -> None:
        add_v1 = json.loads((ASSETS / "add-v1.handoff.example.json").read_text())
        add_v1["actuation_delivery_decision"]["target_head"] = "stale-head"
        add_v1["actuation_delivery_decision"]["ship_handoff"]["ship_input"]["head_sha"] = "stale-head"
        context = deepcopy(self.context())
        context["closure_candidate"] = "ship-complete"
        context["delivery"] = {
            "pr_intent": "yes",
            "publication_required": "yes",
            "add_v1_decision": add_v1,
            "ship_result": {
                "present": "yes",
                "current": "yes",
                "pr_url": "https://github.com/tkersey/example/pull/1",
                "ref": "ship:example",
            },
        }
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("delivery.add_v1_decision.target_head:artifact-mismatch", body["blocked_reasons"])
        self.assertIn("delivery.add_v1_decision.ship_input.head_sha:artifact-mismatch", body["blocked_reasons"])

    def test_ship_complete_rejects_add_shaped_stub_without_add_v1_version(self) -> None:
        context = deepcopy(self.context())
        context["closure_candidate"] = "ship-complete"
        context["delivery"] = {
            "pr_intent": "yes",
            "publication_required": "yes",
            "add_v1_decision": {
                "verdict": "handoff_to_ship",
                "target_head": "abc123",
                "ship_handoff": {
                    "ship_input": {
                        "head_sha": "abc123",
                    }
                },
            },
            "ship_result": {
                "present": "yes",
                "current": "yes",
                "pr_url": "https://github.com/tkersey/example/pull/1",
                "ref": "ship:example",
            },
        }
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("delivery.add_v1_decision.decision_version:invalid", body["blocked_reasons"])

    def test_ship_complete_rejects_partial_add_v1_handoff_with_version(self) -> None:
        context = deepcopy(self.context())
        context["closure_candidate"] = "ship-complete"
        context["delivery"] = {
            "pr_intent": "yes",
            "publication_required": "yes",
            "add_v1_decision": {
                "decision_version": "ADD-v1",
                "verdict": "handoff_to_ship",
                "target_branch": "feature/example",
                "target_head": "abc123",
                "ship_handoff": {
                    "next_owner": "$ship",
                    "ship_input": {
                        "branch": "feature/example",
                        "head_sha": "abc123",
                    }
                },
            },
            "ship_result": {
                "present": "yes",
                "current": "yes",
                "pr_url": "https://github.com/tkersey/example/pull/1",
                "ref": "ship:example",
            },
        }
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("delivery.add_v1_decision.run_id:missing", body["blocked_reasons"])
        self.assertIn("delivery.add_v1_decision.integrated_change_set_receipts:empty", body["blocked_reasons"])

    def test_cached_cas_receipt_does_not_count_as_fresh_clean_run(self) -> None:
        context = self.context("terminal-context.proof-only.example.json")
        context["cas_review"] = {
            "required": "yes",
            "clean_runs_required": 3,
            "clean_runs_count": 3,
            "independent_fresh_runs": "no",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "head123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["normalized_cas_clean_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("cas.clean_runs:not-independent", body["blocked_reasons"])

    def test_cas_tuple_must_match_current_artifact(self) -> None:
        context = self.context("terminal-context.proof-only.example.json")
        context["cas_review"] = {
            "required": "yes",
            "clean_runs_required": 3,
            "clean_runs_count": 3,
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "stale-head",
                "target_fingerprint": "stale-diff",
            },
        }
        context["final_report_fields"]["normalized_cas_clean_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("cas.tuple.head_sha:artifact-mismatch", body["blocked_reasons"])
        self.assertIn("cas.tuple.target_fingerprint:artifact-mismatch", body["blocked_reasons"])

    def test_cas_required_rejects_nonpositive_or_bool_required_clean_runs(self) -> None:
        for value in (0, False):
            with self.subTest(value=value):
                context = deepcopy(self.context("terminal-context.proof-only.example.json"))
                context["cas_review"] = {
                    "required": "yes",
                    "clean_runs_required": value,
                    "clean_runs_count": 0,
                    "independent_fresh_runs": "yes",
                    "tuple_bound": "yes",
                    "tuple": {
                        "base_sha": "base123",
                        "head_sha": "abc123",
                        "target_fingerprint": "diff:clean",
                    },
                }
                context["final_report_fields"]["normalized_cas_clean_runs"] = 1
                decision = MODULE.make_decision(context)
                body = decision["actuation_terminal_decision"]
                self.assertEqual(body["verdict"], "blocked")
                self.assertIn("cas.clean_runs_required:invalid", body["blocked_reasons"])

    def test_cas_required_rejects_insufficient_final_report_clean_runs(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "yes",
            "clean_runs_required": 3,
            "clean_runs_count": 3,
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "abc123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["normalized_cas_clean_runs"] = 2
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("final_report.normalized_cas_clean_runs:not-satisfied", body["blocked_reasons"])

    def test_cas_required_accepts_matching_final_report_clean_runs(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "yes",
            "clean_runs_required": 3,
            "clean_runs_count": 3,
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "abc123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["normalized_cas_clean_runs"] = "3"
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")

    def test_standard_clean_run_aliases_are_first_class(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "yes",
            "standard_clean_runs_required": 3,
            "standard_clean_runs_count": 3,
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "abc123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")

    def test_standard_clean_run_aliases_block_when_insufficient(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "yes",
            "standard_clean_runs_required": 3,
            "standard_clean_runs_count": 2,
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "abc123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["standard_clean_cas_runs"] = 2
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("cas.standard_clean_runs:2-of-3", body["blocked_reasons"])
        self.assertIn(
            "final_report.standard_clean_cas_runs:not-satisfied",
            body["blocked_reasons"],
        )

    def test_required_auxiliary_lane_missing_blocks_completion(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "yes",
            "standard_clean_runs_required": 3,
            "standard_clean_runs_count": 3,
            "required_auxiliary_lanes": ["footgun-finder"],
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "abc123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["next_owner"], "$cas")
        self.assertIn("cas-review-blocked", body["blocked_reasons"])
        self.assertIn("cas.auxiliary_lanes.footgun-finder:missing", body["blocked_reasons"])

    def test_required_auxiliary_lane_blocker_or_rerun_blocks_completion(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "yes",
            "standard_clean_runs_required": 3,
            "standard_clean_runs_count": 3,
            "required_auxiliary_lanes": ["invariant-ace", "complexity-mitigator"],
            "auxiliary_lanes": {
                "invariant-ace": {
                    "folded": "yes",
                    "unresolved_blockers": "yes",
                },
                "complexity-mitigator": {
                    "status": "rerun-required",
                    "folded": "yes",
                },
            },
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "abc123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("cas.auxiliary_lanes.invariant-ace:blocked", body["blocked_reasons"])
        self.assertIn(
            "cas.auxiliary_lanes.complexity-mitigator:rerun-required",
            body["blocked_reasons"],
        )

    def test_selected_auxiliary_lane_requires_standard_cas_even_when_not_marked_required(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "no",
            "required_auxiliary_lanes": ["footgun-finder"],
            "auxiliary_lanes": {
                "footgun-finder": {
                    "status": "clean",
                    "folded": "yes",
                    "head_sha": "abc123",
                    "target_fingerprint": "diff:clean",
                },
            },
        }
        context["final_report_fields"]["standard_clean_cas_runs"] = 0
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["next_owner"], "$cas")
        self.assertIn("cas.standard_clean_runs:0-of-3", body["blocked_reasons"])
        self.assertIn("cas.standard_clean_runs:not-independent", body["blocked_reasons"])
        self.assertIn("cas.tuple.head_sha:missing", body["blocked_reasons"])
        self.assertIn(
            "final_report.standard_clean_cas_runs:not-satisfied",
            body["blocked_reasons"],
        )

    def test_clean_auxiliary_lane_must_match_current_artifact(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "yes",
            "standard_clean_runs_required": 3,
            "standard_clean_runs_count": 3,
            "required_auxiliary_lanes": ["invariant-ace"],
            "auxiliary_lanes": {
                "invariant-ace": {
                    "status": "clean",
                    "folded": "yes",
                    "head_sha": "stale-head",
                    "target_fingerprint": "stale-diff",
                },
            },
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "abc123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn(
            "cas.auxiliary_lanes.invariant-ace.head_sha:artifact-mismatch",
            body["blocked_reasons"],
        )
        self.assertIn(
            "cas.auxiliary_lanes.invariant-ace.target_fingerprint:artifact-mismatch",
            body["blocked_reasons"],
        )

    def test_current_clean_auxiliary_lane_allows_completion_with_standard_cas(self) -> None:
        context = deepcopy(self.context("terminal-context.proof-only.example.json"))
        context["cas_review"] = {
            "required": "yes",
            "standard_clean_runs_required": 3,
            "standard_clean_runs_count": 3,
            "required_auxiliary_lanes": ["complexity-mitigator"],
            "auxiliary_lanes": {
                "complexity-mitigator": {
                    "status": "clean",
                    "folded": "yes",
                    "head_sha": "abc123",
                    "target_fingerprint": "diff:clean",
                },
            },
            "independent_fresh_runs": "yes",
            "tuple_bound": "yes",
            "tuple": {
                "base_sha": "base123",
                "head_sha": "abc123",
                "target_fingerprint": "diff:clean",
            },
        }
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")

    def test_publication_required_requires_pr_intent_and_ship_evidence(self) -> None:
        context = deepcopy(self.context())
        context["delivery"]["publication_required"] = "yes"
        context["delivery"]["pr_intent"] = "no"
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("delivery.pr_intent:missing-with-publication-required", body["blocked_reasons"])

    def test_ship_handoff_without_ship_result_continues(self) -> None:
        decision = MODULE.make_decision(self.context("terminal-context.ship-continue.example.json"))
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "continue")
        self.assertEqual(body["next_owner"], "$ship")
        self.assertIn("ship_result:missing", body["continue_reasons"])

    def test_missing_artifact_binding_blocks(self) -> None:
        context = deepcopy(self.context())
        context["artifact_scope"]["head_sha"] = ""
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("artifact_scope.head_sha:missing", body["blocked_reasons"])

    def test_artifact_blocker_owner_precedes_cas_blocker(self) -> None:
        context = deepcopy(self.context("terminal-context.regression.example.json"))
        context["artifact_scope"]["head_sha"] = ""
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["next_owner"], "$goal-grind")
        self.assertIn("artifact_scope.head_sha:missing", body["blocked_reasons"])
        self.assertIn("cas.clean_runs:0-of-3", body["blocked_reasons"])

    def test_blocked_artifact_owner_not_overridden_by_pending_proof_patch(self) -> None:
        context = deepcopy(self.context())
        context["artifact_scope"]["head_sha"] = ""
        context["proof_patch"] = {}
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["next_owner"], "$goal-grind")
        self.assertIn("artifact_scope.head_sha:missing", body["blocked_reasons"])

    def test_incomplete_local_proof_routes_to_goal_grind(self) -> None:
        context = deepcopy(self.context())
        context["local_proof"]["evidence_fold_verdict"] = "continue"
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "continue")
        self.assertEqual(body["next_owner"], "$goal-grind")
        self.assertIn("local_proof.evidence_fold_verdict:continue", body["continue_reasons"])

    def test_refactor_kernel_local_proof_routes_to_goal_grind(self) -> None:
        context = deepcopy(self.context())
        context["local_proof"]["evidence_fold_verdict"] = "refactor-kernel"
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "continue")
        self.assertEqual(body["next_owner"], "$goal-grind")
        self.assertIn("local_proof.evidence_fold_verdict:refactor-kernel", body["continue_reasons"])

    def test_blocked_local_proof_is_terminal_blocker(self) -> None:
        context = deepcopy(self.context())
        context["local_proof"]["evidence_fold_verdict"] = "blocked"
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["next_owner"], "$goal-grind")
        self.assertIn("local_proof.evidence_fold_verdict:blocked", body["blocked_reasons"])

    def test_ask_human_local_proof_routes_to_human(self) -> None:
        context = deepcopy(self.context())
        context["local_proof"]["evidence_fold_verdict"] = "ask-human"
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "continue")
        self.assertEqual(body["next_owner"], "human")

    def test_check_valid_complete_decision(self) -> None:
        result = MODULE.validate_decision(self.decision("atcg-v1.complete.example.json"))
        self.assertEqual(result["actuation_terminal_gate"]["verdict"], "pass")
        self.assertEqual(result["actuation_terminal_gate"]["can_mark_goal_complete"], "yes")

    def test_completion_allowance_accepts_only_complete_yes(self) -> None:
        allowance = MODULE.make_completion_allowance(self.decision("atcg-v1.complete.example.json"))
        body = allowance["actuation_completion_allowance"]
        self.assertEqual(body["verdict"], "allowed")
        self.assertEqual(body["can_call_update_goal_complete"], "yes")
        self.assertEqual(body["decision_verdict"], "complete")
        self.assertEqual(body["can_mark_goal_complete"], "yes")

    def test_completion_allowance_denies_continue_with_next_owner(self) -> None:
        context = deepcopy(self.context())
        context["proof_patch"] = {}
        allowance = MODULE.make_completion_allowance(MODULE.make_decision(context))
        body = allowance["actuation_completion_allowance"]
        self.assertEqual(body["verdict"], "denied")
        self.assertEqual(body["can_call_update_goal_complete"], "no")
        self.assertEqual(body["decision_verdict"], "continue")
        self.assertEqual(body["next_owner"], "$proof-patch")
        self.assertIn("proof_patch.required:missing-for-proof-patch-closure", body["continue_reasons"])

    def test_completion_allowance_denies_missing_loop_contract(self) -> None:
        context = deepcopy(self.context())
        context["loop_governance"] = {
            "material": "yes",
            "alsr": {"required": "yes", "present": "no", "current": "no"},
            "hyl": {"required": "yes", "present": "no", "current": "no"},
            "hsr": {
                "terminal_present": "yes",
                "latest_fold_current_artifact_bound": "yes",
                "material_mutations": [{"has_hsr": "yes"}],
            },
        }
        allowance = MODULE.make_completion_allowance(MODULE.make_decision(context))
        body = allowance["actuation_completion_allowance"]
        self.assertEqual(body["verdict"], "denied")
        self.assertEqual(body["can_call_update_goal_complete"], "no")
        self.assertEqual(body["decision_verdict"], "blocked")
        self.assertEqual(body["next_owner"], "$goal-actuating")
        self.assertIn("blocked-loop-contract-missing", body["blocked_reasons"])

    def test_completion_allowance_denies_stale_proof(self) -> None:
        context = deepcopy(self.context())
        context["proof"] = {"required": "yes", "matches_verifier": "no"}
        allowance = MODULE.make_completion_allowance(MODULE.make_decision(context))
        body = allowance["actuation_completion_allowance"]
        self.assertEqual(body["verdict"], "denied")
        self.assertEqual(body["can_call_update_goal_complete"], "no")
        self.assertEqual(body["next_owner"], "$goal-grind")
        self.assertIn("proof-stale", body["blocked_reasons"])

    def test_completion_allowance_denies_side_effect_boundary_violation(self) -> None:
        context = deepcopy(self.context())
        context["side_effect_boundary"] = {"respected": "no"}
        allowance = MODULE.make_completion_allowance(MODULE.make_decision(context))
        body = allowance["actuation_completion_allowance"]
        self.assertEqual(body["verdict"], "denied")
        self.assertEqual(body["can_call_update_goal_complete"], "no")
        self.assertEqual(body["next_owner"], "$ship")
        self.assertIn("side-effect-boundary-violated", body["blocked_reasons"])

    def test_check_rejects_complete_without_artifact_binding(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["current_artifact_binding"]["head_sha"] = ""
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete.current_artifact_binding.head_sha"):
            MODULE.validate_decision(decision)

    def test_check_rejects_dirty_complete_without_proof_patch_receipt(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["current_artifact_binding"]["dirty_state"] = "tracked-dirty"
        decision["actuation_terminal_decision"]["required_receipts"] = []
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete.current_artifact_binding.dirty_state"):
            MODULE.validate_decision(decision)

    def test_check_rejects_proof_patch_complete_without_required_receipt(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["required_receipts"] = []
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete.required_receipts.proof_patch"):
            MODULE.validate_decision(decision)

    def test_check_rejects_ship_complete_without_ship_receipt(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["closure_candidate"] = "ship-complete"
        decision["actuation_terminal_decision"]["required_receipts"] = ["add_v1_delivery_decision"]
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete.required_receipts.ship_result"):
            MODULE.validate_decision(decision)

    def test_check_rejects_ship_complete_without_add_v1_receipt(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["closure_candidate"] = "ship-complete"
        decision["actuation_terminal_decision"]["required_receipts"] = ["ship_result"]
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete.required_receipts.add_v1_delivery_decision"):
            MODULE.validate_decision(decision)

    def test_check_rejects_invalid_terminal_enums(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["source"] = "unknown-source"
        decision["actuation_terminal_decision"]["closure_candidate"] = "unknown-closure"
        with self.assertRaisesRegex(MODULE.TerminalGateError, "closure_candidate:invalid"):
            MODULE.validate_decision(decision)

    def test_check_rejects_complete_for_nonterminal_closure_candidate(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["closure_candidate"] = "ship-handoff"
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete.closure_candidate:not-terminal"):
            MODULE.validate_decision(decision)

    def test_check_rejects_complete_with_blockers(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["blocked_reasons"] = ["cas.clean_runs:0-of-3"]
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete:reasons-present"):
            MODULE.validate_decision(decision)

    def test_check_rejects_continue_without_next_owner(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        body = decision["actuation_terminal_decision"]
        body["verdict"] = "continue"
        body["can_mark_goal_complete"] = "no"
        body["next_owner"] = "none"
        body["continue_reasons"] = ["proof_patch:missing"]
        with self.assertRaisesRegex(MODULE.TerminalGateError, "continue:next_owner-none"):
            MODULE.validate_decision(decision)

    def test_check_rejects_blocked_without_next_owner(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        body = decision["actuation_terminal_decision"]
        body["verdict"] = "blocked"
        body["can_mark_goal_complete"] = "no"
        body["next_owner"] = "none"
        body["blocked_reasons"] = ["artifact_scope.head_sha:missing"]
        with self.assertRaisesRegex(MODULE.TerminalGateError, "blocked:next_owner-none"):
            MODULE.validate_decision(decision)

    def test_cli_decide_writes_terminal_decision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "terminal.json"
            code = MODULE.main([
                "decide",
                "--context",
                str(ASSETS / "terminal-context.proof-only.example.json"),
                "--out",
                str(out),
            ])
            self.assertEqual(code, 0)
            body = json.loads(out.read_text())["actuation_terminal_decision"]
            self.assertEqual(body["verdict"], "complete")

    def test_cli_allow_complete_accepts_valid_complete_decision(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "allow-complete",
                "--decision",
                str(ASSETS / "atcg-v1.complete.example.json"),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        body = json.loads(result.stdout)["actuation_completion_allowance"]
        self.assertEqual(body["can_call_update_goal_complete"], "yes")

    def test_cli_allow_complete_denies_valid_noncomplete_decision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            decision_path = Path(td) / "blocked.json"
            decision_path.write_text(
                json.dumps(MODULE.make_decision(self.context("terminal-context.advisory-would-block.example.json"))),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "allow-complete",
                    "--decision",
                    str(decision_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        body = json.loads(result.stdout)["actuation_completion_allowance"]
        self.assertEqual(body["can_call_update_goal_complete"], "no")
        self.assertEqual(body["decision_verdict"], "blocked")


if __name__ == "__main__":
    unittest.main()
