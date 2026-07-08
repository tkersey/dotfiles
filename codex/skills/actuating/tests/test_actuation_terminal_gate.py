#!/usr/bin/env -S uv run python
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
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
        self.assertIn("proof_patch", body["required_receipts"])

    def test_hylo_context_can_complete_with_real_receipts(self) -> None:
        decision = MODULE.make_decision(self.context("terminal-context.hylo-complete.example.json"))
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertIn("alsr", body["required_receipts"])
        self.assertIn("hyl", body["required_receipts"])
        self.assertIn("terminal_hsr", body["required_receipts"])
        self.assertIn("goal_focus_frame_chain", body["required_receipts"])

    def test_material_run_without_hsr_chain_blocks(self) -> None:
        context = deepcopy(self.context("terminal-context.hylo-complete.example.json"))
        loop = context["loop_governance"]
        loop["hsr"] = {"required": "yes", "terminal_required": "yes", "terminal_present": "no", "latest_fold_current_artifact_bound": "no"}
        loop["material_mutations"] = []
        self.assert_blocks_with(context, "blocked-hylo-terminal-missing", "$goal-actuating")

    def test_material_mutation_requires_unfold_action_fold_and_receipt_ref(self) -> None:
        context = deepcopy(self.context("terminal-context.hylo-complete.example.json"))
        loop = context["loop_governance"]
        loop["hsr"]["chain"] = []
        loop["hsr"]["terminal_present"] = "yes"
        loop["material_mutations"] = [{"has_hsr": "yes", "has_unfold": "no", "has_action": "yes", "has_fold": "no"}]
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("blocked-hylo-frontier-missing", body["blocked_reasons"])
        self.assertIn("blocked-hylo-fold-missing", body["blocked_reasons"])
        self.assertIn("material_mutations[0].receipt_ref:missing", body["blocked_reasons"])

    def test_stale_alsr_blocks_completion(self) -> None:
        context = deepcopy(self.context("terminal-context.hylo-complete.example.json"))
        context["loop_governance"]["alsr"]["receipt"]["artifact_scope"]["head"] = "stale"
        self.assert_blocks_with(context, "blocked-loop-contract-stale", "$goal-actuating")

    def test_goal_focus_child_cannot_claim_parent_completion(self) -> None:
        context = deepcopy(self.context("terminal-context.hylo-complete.example.json"))
        context["loop_governance"]["goal_focus"]["child_claimed_parent_completion"] = "yes"
        self.assert_blocks_with(context, "blocked-hylo-terminal-missing", "$goal-actuating")

    def test_fused_context_can_complete_with_fusion_receipt(self) -> None:
        decision = MODULE.make_decision(self.context("terminal-context.advisory-fused.example.json"))
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertIn("fusion_receipt", body["required_receipts"])

    def test_fused_claim_without_receipt_blocks(self) -> None:
        context = self.context("terminal-context.fusion-missing.example.json")
        self.assert_blocks_with(context, "blocked-loop-contract-missing", "$goal-actuating")

    def test_original_regression_is_blocked(self) -> None:
        decision = MODULE.make_decision(self.context("terminal-context.regression.example.json"))
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertEqual(body["next_owner"], "$cas")
        self.assertIn("cas-review-blocked", body["blocked_reasons"])
        self.assertIn("cas.clean_runs:0-of-3", body["blocked_reasons"])

    def test_cached_cas_receipt_does_not_count_as_fresh_clean_run(self) -> None:
        context = deepcopy(self.context())
        context["cas_review"] = {
            "required": "yes",
            "clean_runs_required": 3,
            "clean_runs_count": 3,
            "independent_fresh_runs": "no",
            "tuple_bound": "yes",
            "tuple": {"base_sha": "base123", "head_sha": "abc123", "target_fingerprint": "diff:clean"},
        }
        context["review_profile"] = review_profile()
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("cas.clean_runs:not-independent", body["blocked_reasons"])

    def test_review_profile_requires_all_auxiliary_lane_decisions(self) -> None:
        context = deepcopy(self.context())
        context["cas_review"] = satisfied_standard_cas()
        context["review_profile"] = review_profile()
        del context["review_profile"]["auxiliary_review_lanes"]["invariant-ace"]
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        self.assert_blocks_with(context, "review_profile.auxiliary_review_lanes.invariant-ace:missing", "$goal-actuating")

    def test_selected_auxiliary_lane_requires_valid_lens_evidence(self) -> None:
        context = deepcopy(self.context())
        context["cas_review"] = satisfied_standard_cas()
        context["review_profile"] = review_profile(**{"complexity-mitigator": {"state": "clean", **lens_evidence("complexity-mitigator", lens_evidence_state="stale")}})
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("review_profile.auxiliary_review_lanes.complexity-mitigator.lens_evidence_state:stale", body["blocked_reasons"])

    def test_selected_pending_auxiliary_lane_blocks_completion(self) -> None:
        context = deepcopy(self.context())
        context["cas_review"] = satisfied_standard_cas()
        context["review_profile"] = review_profile(**{"footgun-finder": {"state": "selected-pending", "reason": "Public API surface changed."}})
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        self.assert_blocks_with(context, "review_profile.auxiliary_review_lanes.footgun-finder:selected-pending", "$goal-actuating")

    def test_invalid_clean_auxiliary_lane_does_not_clear_obligation(self) -> None:
        context = deepcopy(self.context())
        context["cas_review"] = satisfied_standard_cas()
        context["review_profile"] = review_profile(
            **{
                "footgun-finder": {
                    "state": "clean",
                    **lens_evidence("footgun-finder", source_validity="invalid-proof"),
                    "tuple": {"base_sha": "unknown", "head_sha": "abc123", "target_fingerprint": "diff:clean"},
                }
            }
        )
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("review_profile.auxiliary_review_lanes.footgun-finder.source_validity:invalid-proof", body["blocked_reasons"])

    def test_invalid_dirty_auxiliary_lane_remains_candidate_pressure(self) -> None:
        context = deepcopy(self.context())
        context["cas_review"] = satisfied_standard_cas()
        context["review_profile"] = review_profile(
            **{
                "footgun-finder": {
                    "state": "candidate-pressure",
                    "source_validity": "invalid-proof",
                    "reason": "Findings are quarantined until owner-boundary validation completes.",
                }
            }
        )
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        self.assert_blocks_with(context, "review_profile.auxiliary_review_lanes.footgun-finder:candidate-pressure", "$goal-actuating")

    def test_valid_folded_auxiliary_lane_can_complete(self) -> None:
        context = deepcopy(self.context())
        context["cas_review"] = satisfied_standard_cas()
        context["review_profile"] = review_profile(**{"footgun-finder": {"state": "findings-folded", **lens_evidence("footgun-finder")}})
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")

    def test_standard_review_profile_can_complete(self) -> None:
        context = deepcopy(self.context())
        context["cas_review"] = satisfied_standard_cas()
        context["review_profile"] = review_profile()
        context["final_report_fields"]["standard_clean_cas_runs"] = 3
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "complete")
        self.assertIn("cas_review", body["required_receipts"])

    def test_ship_handoff_without_ship_result_continues(self) -> None:
        decision = MODULE.make_decision(self.context("terminal-context.ship-continue.example.json"))
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "continue")
        self.assertEqual(body["next_owner"], "$ship")
        self.assertIn("ship_handoff:not-terminal", body["continue_reasons"])

    def test_missing_artifact_binding_blocks(self) -> None:
        context = deepcopy(self.context())
        context["artifact_scope"]["head_sha"] = ""
        self.assert_blocks_with(context, "artifact_scope.head_sha:missing", "$goal-grind")

    def test_incomplete_local_proof_routes_to_goal_grind(self) -> None:
        context = deepcopy(self.context())
        context["local_proof"]["evidence_fold_verdict"] = "continue"
        decision = MODULE.make_decision(context)
        body = decision["actuation_terminal_decision"]
        self.assertEqual(body["verdict"], "continue")
        self.assertEqual(body["next_owner"], "$goal-grind")

    def test_completion_allowance_accepts_only_complete_yes(self) -> None:
        allowance = MODULE.make_completion_allowance(MODULE.make_decision(self.context()))
        body = allowance["actuation_completion_allowance"]
        self.assertEqual(body["verdict"], "allowed")
        self.assertEqual(body["can_call_update_goal_complete"], "yes")

    def test_completion_allowance_denies_blocked_hylo(self) -> None:
        allowance = MODULE.make_completion_allowance(MODULE.make_decision(self.context("terminal-context.fusion-missing.example.json")))
        body = allowance["actuation_completion_allowance"]
        self.assertEqual(body["verdict"], "denied")
        self.assertEqual(body["next_owner"], "$goal-actuating")

    def test_check_rejects_complete_without_artifact_binding(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["current_artifact_binding"]["head_sha"] = ""
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete.current_artifact_binding.head_sha"):
            MODULE.validate_decision(decision)

    def test_check_rejects_complete_for_nonterminal_closure_candidate(self) -> None:
        decision = self.decision("atcg-v1.complete.example.json")
        decision["actuation_terminal_decision"]["closure_candidate"] = "ship-handoff"
        with self.assertRaisesRegex(MODULE.TerminalGateError, "complete.closure_candidate:not-terminal"):
            MODULE.validate_decision(decision)

    def test_advisory_cli_would_block_is_non_blocking(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "validate", "--context", str(ASSETS / "terminal-context.advisory-would-block.example.json"), "--mode", "advisory", "--format", "json"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        body = json.loads(result.stdout)
        self.assertEqual(body["verdict"], "advisory")
        self.assertTrue(body["would_block"])
        self.assertFalse(body["can_mark_goal_complete"])
        self.assertIn("blocked-loop-contract-missing", body["would_block_reasons"])


def lens_evidence(lane: str, **overrides):
    contracts = {"footgun-finder": "footgun-lens-v1", "invariant-ace": "invariant-gate-v1", "complexity-mitigator": "complexity-preflight-v1"}
    record = {"lens_contract": contracts[lane], "lens_evidence_state": "valid", "lens_evidence_ref": f"cas:{lane}:lens", "source_validity": "valid", "head_sha": "abc123", "target_fingerprint": "diff:clean"}
    record.update(overrides)
    return record


def review_profile(**lane_overrides):
    lanes = {
        "footgun-finder": {"state": "not-required", "reason": "Diff does not touch misuse-prone public surfaces."},
        "invariant-ace": {"state": "not-required", "reason": "Diff does not touch invariant-bearing state."},
        "complexity-mitigator": {"state": "not-required", "reason": "Reviewability is not blocked by complexity."},
    }
    lanes.update(lane_overrides)
    return {"standard": "required", "auxiliary_review_lanes": lanes}


def satisfied_standard_cas():
    return {"required": "yes", "standard_clean_runs_required": 3, "standard_clean_runs_count": 3, "independent_fresh_runs": "yes", "tuple_bound": "yes", "tuple": {"base_sha": "base123", "head_sha": "abc123", "target_fingerprint": "diff:clean"}}


if __name__ == "__main__":
    unittest.main()
