"""Deterministic working-set traces; no model or native-runtime qualification."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "campaign_state.py"
SPEC = importlib.util.spec_from_file_location("elenctic_campaign_state", SCRIPT)
campaign = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(campaign)


def epoch():
    return {
        "host": "github.com", "viewer_id": "user-1", "pr_node_id": "pr-node-1",
        "repo": "example/project", "pr": 7, "base_tip": "base-tip",
        "base": "merge-base", "candidate": "head",
    }


def observation():
    return {**epoch(), "state": "OPEN"}


def assignment(assignment_id, state="queued", *, active=False, runnable=True):
    return {"assignment_id": assignment_id, "path": f"{assignment_id}.py",
            "state": state, "active": active, "runnable": runnable}


def schedule_input(rows, queue, **extra):
    return {
        "bound_epoch": epoch(), "observed_epoch": observation(),
        "selected_paths": [row["path"] for row in rows],
        "assignments": rows, "queue": queue, "concurrency": 1, **extra,
    }


def report_input(assignment_id="a", coverage="complete", verdict="BLOCKED"):
    expected = {
        "schema": "elenctic-review-identity/v1", "mode": "single-file",
        "repo": "example/project", "pr": 7, "campaign_id": "campaign-1",
        "assignment_id": assignment_id, "campaign_context_id": "context-1",
        "campaign_seed_thread_id": "seed-1", "target": f"{assignment_id}.py",
        "base": "merge-base", "candidate": "head", "view": "pr-head",
    }
    active = {"worker_id": f"worker-{assignment_id}", "turn_id": "turn-2"}
    return {
        "bound_epoch": epoch(), "observed_epoch": observation(),
        "expected_identity": expected, "active_attempt": active,
        "report": {**active, "identity": {**expected, "coverage": coverage, "verdict": verdict},
                   "decision": verdict},
    }


def admitted(assignment_id="a", verdict="BLOCKED"):
    claim = report_input(assignment_id, verdict=verdict)
    return {
        **assignment(assignment_id, "accepted", runnable=False),
        "expected_identity": claim["expected_identity"],
        "active_attempt": claim["active_attempt"], "accepted_report": claim["report"],
    }


def coverage_input(rows):
    return {
        "bound_epoch": epoch(), "observed_epoch": observation(),
        "campaign_id": "campaign-1", "campaign_context_id": "context-1",
        "campaign_seed_thread_id": "seed-1",
        "selected_paths": [row["path"] for row in rows], "assignments": rows,
    }


class CampaignStateTests(unittest.TestCase):
    def test_repeated_continuations_do_not_overtake_untouched_work(self):
        data = schedule_input(
            [assignment("a", "incomplete"), assignment("b"), assignment("c")],
            ["b", "c"], requeue="a",
        )
        original = copy.deepcopy(data)
        first = campaign.schedule(data)
        self.assertEqual(first["queue"], ["b", "c", "a"])
        self.assertEqual(first["dispatchable"], ["b"])
        self.assertEqual(data, original)  # The caller owns its existing working set.

        # B also returns incomplete: it joins behind C and A, rather than taking
        # its newly free slot again. This is scheduling opportunity, not convergence.
        first["assignments"][1]["state"] = "incomplete"
        second = campaign.schedule(schedule_input(first["assignments"], ["c", "a"], requeue="b"))
        self.assertEqual(second["queue"], ["c", "a", "b"])
        self.assertEqual(second["dispatchable"], ["c"])

    def test_continuation_is_immediately_eligible_when_slot_is_free(self):
        result = campaign.schedule(schedule_input([assignment("a", "incomplete")], [], requeue="a"))
        self.assertEqual(result["dispatchable"], ["a"])

    def test_provider_delay_retains_age_without_idling_other_work(self):
        data = schedule_input([assignment("a", runnable=False), assignment("b")], ["a", "b"])
        result = campaign.schedule(data)
        self.assertEqual(result["queue"], ["a", "b"])
        self.assertEqual(result["dispatchable"], ["b"])
        data["assignments"][0]["runnable"] = True
        self.assertEqual(campaign.schedule(data)["dispatchable"], ["a"])

    def test_requeue_is_idempotent_and_preserves_existing_position(self):
        data = schedule_input([assignment("a"), assignment("b")], ["a", "b"], requeue="a")
        self.assertEqual(campaign.schedule(data)["queue"], ["a", "b"])

    def test_live_or_ambiguous_attempt_reserves_its_slot(self):
        data = schedule_input(
            [assignment("a", "launched", active=True, runnable=False), assignment("b")], ["b"]
        )
        self.assertEqual(campaign.schedule(data)["dispatchable"], [])
        data["requeue"] = "a"
        with self.assertRaises(ValueError):
            campaign.schedule(data)

    def test_no_retry_for_approval_or_stale_work(self):
        for state in ("accepted", "stale"):
            with self.subTest(state=state), self.assertRaises(ValueError):
                campaign.schedule(schedule_input(
                    [assignment("a", state, runnable=False)], [], requeue="a"
                ))

    def test_missing_or_duplicate_order_and_expanded_selection_fail(self):
        for queue in ([], ["a", "a"], ["unknown"]):
            with self.subTest(queue=queue), self.assertRaises(ValueError):
                campaign.schedule(schedule_input([assignment("a")], queue))
        data = schedule_input([assignment("a")], ["a"])
        data["selected_paths"] = ["a.py", "excluded.py"]
        with self.assertRaises(ValueError):
            campaign.schedule(data)

    def test_paths_remain_exact_data(self):
        for path in (" ", "nested/a\nfile", "$(command)/'file'"):
            row = assignment("a")
            row["path"] = path
            result = campaign.schedule(schedule_input([row], ["a"]))
            self.assertEqual(result["assignments"][0]["path"], path)

    def test_superseded_attempt_and_wrong_worker_cannot_supply_completion(self):
        for field, value in (("turn_id", "turn-1"), ("worker_id", "old-worker")):
            data = report_input()
            data["report"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                campaign.check_report(data)

    def test_report_bindings_cannot_be_borrowed_from_another_assignment(self):
        for field in ("campaign_id", "assignment_id", "campaign_context_id",
                      "campaign_seed_thread_id", "target", "base", "candidate", "view"):
            data = report_input()
            data["report"]["identity"][field] = "another"
            with self.subTest(field=field), self.assertRaises(ValueError):
                campaign.check_report(data)

    def test_worker_policy_is_optional_only_for_matching_legacy_bindings(self):
        self.assertTrue(campaign.check_report(report_input())["completion_claim_consistent"])
        for policy in ("pragmatic", "pedantic"):
            data = report_input()
            data["expected_identity"]["merge_policy"] = policy
            data["report"]["identity"]["merge_policy"] = policy
            with self.subTest(policy=policy):
                self.assertTrue(campaign.check_report(data)["completion_claim_consistent"])
            for missing in ("expected_identity", "report"):
                changed = copy.deepcopy(data)
                identity = changed[missing] if missing == "expected_identity" else changed[missing]["identity"]
                del identity["merge_policy"]
                with self.subTest(policy=policy, missing=missing), self.assertRaises(ValueError):
                    campaign.check_report(changed)
        data["expected_identity"]["merge_policy"] = "pragmatic"
        with self.assertRaises(ValueError):
            campaign.check_report(data)  # Report still claims pedantic.

    def test_policy_must_be_an_explicit_known_string(self):
        for value in (None, "", "default", "Pragmatic", True, [], {}):
            data = report_input()
            data["expected_identity"]["merge_policy"] = value
            data["report"]["identity"]["merge_policy"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                campaign.check_report(data)

    def test_coverage_cannot_mix_or_strip_assignment_policies(self):
        for policy in ("pragmatic", "pedantic"):
            rows = [admitted("a"), admitted("b", "APPROVE")]
            for row in rows:
                row["expected_identity"]["merge_policy"] = policy
                row["accepted_report"]["identity"]["merge_policy"] = policy
            data = {**coverage_input(rows), "merge_policy": policy}
            with self.subTest(policy=policy):
                self.assertEqual(campaign.coverage(data)["complete_files"], 2)
            missing = copy.deepcopy(data); del missing["merge_policy"]
            with self.assertRaises(ValueError):
                campaign.coverage(missing)
            for replacement in (None, "pragmatic" if policy == "pedantic" else "pedantic"):
                changed = copy.deepcopy(data)
                for source in (changed["assignments"][1]["expected_identity"],
                               changed["assignments"][1]["accepted_report"]["identity"]):
                    if replacement is None:
                        del source["merge_policy"]
                    else:
                        source["merge_policy"] = replacement
                with self.subTest(policy=policy, replacement=replacement), self.assertRaises(ValueError):
                    campaign.coverage(changed)
        invalid = {**coverage_input([]), "merge_policy": None}
        with self.assertRaises(ValueError):
            campaign.coverage(invalid)

    def test_stale_epoch_blocks_admission_and_dispatch(self):
        for field in campaign.EPOCH_FIELDS:
            data = report_input()
            data["observed_epoch"][field] = 8 if field == "pr" else "changed"
            with self.subTest(field=field), self.assertRaises(ValueError):
                campaign.check_report(data)
        data = schedule_input([assignment("a")], ["a"])
        data["observed_epoch"]["state"] = "CLOSED"
        with self.assertRaises(ValueError):
            campaign.schedule(data)

    def test_coverage_and_verdict_remain_independent(self):
        for coverage, verdict, complete in (
            ("complete", "BLOCKED", True), ("complete", "APPROVE", True),
            ("incomplete", "BLOCKED", False), ("incomplete", "INCOMPLETE", False),
        ):
            with self.subTest(coverage=coverage, verdict=verdict):
                result = campaign.check_report(report_input(coverage=coverage, verdict=verdict))
                self.assertEqual(result["completion_claim_consistent"], complete)
        for coverage, verdict in (("complete", "INCOMPLETE"), ("incomplete", "APPROVE")):
            with self.subTest(coverage=coverage, verdict=verdict), self.assertRaises(ValueError):
                campaign.check_report(report_input(coverage=coverage, verdict=verdict))
        data = report_input()
        data["report"]["decision"] = "APPROVE"
        with self.assertRaises(ValueError):
            campaign.check_report(data)

    def test_selected_coverage_counts_admitted_files_once(self):
        rows = [admitted("a"), assignment("b", "incomplete"), assignment("c")]
        result = campaign.coverage(coverage_input(rows))
        self.assertEqual(result["selected_files"], 3)
        self.assertEqual(result["complete_files"], 1)
        self.assertEqual(result["complete_verdict_counts"], {"BLOCKED": 1, "APPROVE": 0})
        self.assertFalse(result["all_selected_files_have_accepted_reports"])
        self.assertNotIn("verdict", result)

    def test_accepted_flag_cannot_hide_incomplete_or_superseded_report(self):
        for change in ("incomplete", "old-turn", "other-campaign"):
            row = admitted()
            if change == "incomplete":
                row["accepted_report"]["identity"]["coverage"] = "incomplete"
            elif change == "old-turn":
                row["accepted_report"]["turn_id"] = "turn-1"
            else:
                row["expected_identity"]["campaign_id"] = "campaign-2"
                row["accepted_report"]["identity"]["campaign_id"] = "campaign-2"
            with self.subTest(change=change), self.assertRaises(ValueError):
                campaign.coverage(coverage_input([row]))

    def test_empty_selection_is_counted_without_a_review_verdict(self):
        result = campaign.coverage(coverage_input([]))
        self.assertEqual(result["complete_files"], 0)
        self.assertFalse(result["has_selected_files"])
        self.assertNotIn("verdict", result)

    def test_cli_stream_roundtrip_and_duplicate_key_rejection(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "check-report"],
                             input=json.dumps(report_input()), text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(json.loads(run.stdout)["completion_claim_consistent"])
        bad = subprocess.run([sys.executable, str(SCRIPT), "schedule"],
                             input='{"queue":[],"queue":[]}', text=True, capture_output=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, "")
        self.assertIn("duplicate JSON key", bad.stderr)


if __name__ == "__main__":
    unittest.main()
