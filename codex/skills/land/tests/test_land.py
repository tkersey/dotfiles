import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text()
PROTOCOL = (ROOT / "references" / "landing-protocol.md").read_text()
RECORD = (ROOT / "references" / "land-record.md").read_text()
CONTRACT = json.loads((ROOT / "references" / "decision-contract.json").read_text())
AGENT = (ROOT / "agents" / "openai.yaml").read_text()
SCRIPT = ROOT / "scripts" / "evaluate_preflight.py"
SPEC = importlib.util.spec_from_file_location("land_preflight", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
H0 = "0" * 40
H1 = "1" * 40


def snapshot(head=H0, delivery="immediate"):
    return {
        "expected": {"repository": "o/r", "pr_number": 42, "base_ref": "main", "head_repository": "o/r", "head_ref": "feature", "head_oid": head},
        "observed": {"repository": "o/r", "pr_number": 42, "state": "OPEN", "is_draft": False, "base_ref": "main", "head_repository": "o/r", "head_ref": "feature", "head_oid": head},
        "reviews": {"inventory_complete": True, "unresolved_thread_ids": [], "review_decision": "APPROVED", "requested_changes_active": False, "explicit_blockers": 0, "reconciliation": {"initial_unresolved_thread_ids": [], "records": []}},
        "checks": {"required_expected": True, "items": [{"name": "tests", "required": True, "bucket": "pass"}]},
        "merge": {"delivery_mode": delivery, "conflict_free": True, "branch_up_to_date": True, "strict_freshness_required": True, "policy_satisfied": True, "method_allowed": True, "admin_override": False},
        "policy": {"approvals_required": True, "allow_required_skipping": False},
    }


def resolution(*, observed=H0, resolved=H1, authority="entailed", applicability="already-excluded", disposition="fixed-and-evidenced", tid="T1"):
    return {"thread_id": tid, "concern_ref": "https://github.com/o/r/pull/42#discussion_r1", "observed_head_oid": observed, "resolved_head_oid": resolved, "law_authority": authority, "current_applicability": applicability, "disposition": disposition, "evidence_refs": ["proof:current-head"], "resolution_readback": True}


def report(value):
    return MODULE.evaluate(value)["land_preflight"]


def codes(value, field="blockers"):
    return {item["code"] for item in value[field]}


class ContractTests(unittest.TestCase):
    def test_review_closure_is_explicit_owned_work(self):
        for phrase in ("allow_implicit_invocation: false", "reconcile every unresolved review thread"):
            self.assertIn(phrase, AGENT)
        for phrase in ("Every unresolved review thread", "must drive every unresolved thread"):
            self.assertIn(phrase, SKILL)

    def test_state_machine_and_order(self):
        modes = ("reconcile-reviews", "rebind-successor-head", "merge-now", "queue-and-wait", "auto-merge-and-wait", "cleanup-only", "obstructed")
        for mode in modes:
            self.assertIn(mode, SKILL)
            self.assertIn(mode, RECORD)
        self.assertLess(SKILL.index("## Review reconciliation"), SKILL.index("## Merge admission"))

    def test_resolution_cannot_erase_evidence(self):
        self.assertNotIn("resolve-only-with-user-authorization", SKILL + PROTOCOL)
        for phrase in ("Thread resolution records proof; it never creates proof", "bare thread IDs", "generic continuation instruction", "fixed-and-evidenced", "reviewer-withdrawn"):
            self.assertIn(phrase, SKILL + PROTOCOL)

    def test_successor_epoch_restarts_preflight(self):
        for phrase in ("successor landing epoch", "patch -> validate -> publish successor head", "discard every admission observation", "complete fresh preflight"):
            self.assertIn(phrase, SKILL + PROTOCOL)

    def test_existing_safety_invariants_remain(self):
        for phrase in ("--match-head-commit", "state == MERGED", "mergedAt", "mergeCommit OID", "git worktree list --porcelain -z", "git worktree remove --force", "rm -rf"):
            self.assertIn(phrase, SKILL + PROTOCOL)
        self.assertIn("Never use `--admin`", PROTOCOL)
        for field in ("record_version: LAND-v2", "review_reconciliation:", "epochs:", "obstructions:", "postcondition:", "associated_worktrees:"):
            self.assertIn(field, RECORD)

    def test_decision_contract_references_exist(self):
        contract = CONTRACT["skill_decision_contract"]
        triggers = {x["trigger_id"] for x in contract["triggers"]}
        routes = {x["route_id"] for x in contract["routes"]}
        self.assertTrue({"LAND-RECONCILE-REVIEWS", "LAND-REBIND-SUCCESSOR", "LAND-OBSTRUCT"} <= routes)
        for clause in contract["clauses"]:
            self.assertTrue(set(clause["trigger_refs"]) <= triggers, clause["clause_id"])
            self.assertTrue(set(clause["expected_routes"]) <= routes, clause["clause_id"])
            self.assertTrue(set(clause["prohibited_routes"]) <= routes, clause["clause_id"])
        self.assertLessEqual(len(SKILL.splitlines()), 500)


class EvaluatorTests(unittest.TestCase):
    def assert_block(self, value, code):
        result = report(value)
        self.assertEqual("block", result["verdict"])
        self.assertIn(code, codes(result))

    def test_immediate_ready(self):
        value = report(snapshot())
        self.assertEqual(("pass", "ready", "merge-now"), (value["verdict"], value["merge_admission"], value["mode"]))

    def test_unresolved_thread_continues(self):
        value = snapshot()
        value["reviews"]["unresolved_thread_ids"] = ["T1"]
        value["reviews"]["reconciliation"]["initial_unresolved_thread_ids"] = ["T1"]
        result = report(value)
        self.assertEqual(("continue", "not-ready", "reconcile-reviews"), (result["verdict"], result["merge_admission"], result["mode"]))
        self.assertIn("REVIEW_THREADS_UNRESOLVED", codes(result, "reasons"))

    def test_requested_changes_continue(self):
        value = snapshot()
        value["reviews"].update(requested_changes_active=True, review_decision="CHANGES_REQUESTED")
        self.assertEqual("continue", report(value)["verdict"])

    def test_successor_head_fix_reflights(self):
        value = snapshot(H1)
        value["reviews"]["reconciliation"] = {"initial_unresolved_thread_ids": ["T1"], "records": [resolution()]}
        self.assertEqual("pass", report(value)["verdict"])

    def test_unchanged_head_fix_is_rejected(self):
        value = snapshot()
        value["reviews"]["reconciliation"] = {"initial_unresolved_thread_ids": ["T1"], "records": [resolution(resolved=H0)]}
        self.assert_block(value, "FIXED_THREAD_HEAD_UNCHANGED")

    def test_disappeared_thread_requires_resolution_evidence(self):
        value = snapshot()
        value["reviews"]["reconciliation"]["initial_unresolved_thread_ids"] = ["T1"]
        result = report(value)
        self.assertEqual("continue", result["verdict"])
        self.assertIn("REVIEW_RECONCILIATION_INCOMPLETE", codes(result, "reasons"))

    def test_nonblocking_preference_can_resolve_without_head_change(self):
        value = snapshot()
        rec = resolution(resolved=H0, authority="preference", applicability="still-present", disposition="nonblocking-by-authority")
        value["reviews"]["reconciliation"] = {"initial_unresolved_thread_ids": ["T1"], "records": [rec]}
        self.assertEqual("pass", report(value)["verdict"])

    def test_reconciliation_provenance_failures(self):
        cases = []
        unbound = snapshot(); unbound["reviews"]["unresolved_thread_ids"] = ["T1"]
        cases.append((unbound, "REVIEW_RECONCILIATION_SCOPE_MISMATCH"))
        overlap = snapshot(); overlap["reviews"]["unresolved_thread_ids"] = ["T1"]
        overlap["reviews"]["reconciliation"] = {"initial_unresolved_thread_ids": ["T1"], "records": [resolution(resolved=H0, authority="preference", applicability="still-present", disposition="nonblocking-by-authority")]}
        cases.append((overlap, "REVIEW_RESOLUTION_STATE_CONTRADICTION"))
        entailed = snapshot(); entailed["reviews"]["reconciliation"] = {"initial_unresolved_thread_ids": ["T1"], "records": [resolution(resolved=H0, applicability="still-present", disposition="nonblocking-by-authority")]}
        cases.append((entailed, "REVIEW_RESOLUTION_AUTHORITY_CONTRADICTION"))
        for value, code in cases:
            with self.subTest(code=code): self.assert_block(value, code)

    def test_thread_id_shape_is_fail_closed(self):
        invalid = snapshot(); invalid["reviews"]["unresolved_thread_ids"] = False
        self.assert_block(invalid, "FIELD_LIST_INVALID")
        duplicate = snapshot(); duplicate["reviews"]["unresolved_thread_ids"] = ["T1", "T1"]
        duplicate["reviews"]["reconciliation"]["initial_unresolved_thread_ids"] = ["T1", "T1"]
        self.assert_block(duplicate, "FIELD_LIST_DUPLICATE")

    def test_checks_and_freshness_are_route_correct(self):
        canceled = snapshot(); canceled["checks"]["items"][0]["bucket"] = "cancel"
        self.assert_block(canceled, "REQUIRED_CHECK_CANCELLED")
        queued = snapshot(delivery="queue"); queued["merge"]["branch_up_to_date"] = False
        self.assertEqual(("pass", "not-applicable"), (report(queued)["verdict"], report(queued)["gates"]["branch_freshness"]))
        strict = snapshot(); strict["merge"]["branch_up_to_date"] = False
        self.assert_block(strict, "BRANCH_NOT_CURRENT")
        loose = snapshot(); loose["merge"].update(branch_up_to_date=False, strict_freshness_required=False)
        self.assertEqual("pass", report(loose)["verdict"])

    def test_admin_and_head_drift_block(self):
        admin = snapshot(); admin["merge"]["admin_override"] = True
        self.assert_block(admin, "ADMIN_OVERRIDE_PROHIBITED")
        drift = snapshot(); drift["observed"]["head_oid"] = H1
        self.assert_block(drift, "TARGET_HEAD_MISMATCH")

    def test_cleanup_only_needs_only_merged_identity(self):
        value = snapshot()
        value["observed"].update(state="MERGED", merged_at="2026-08-20T20:00:00Z", merge_commit_oid="a" * 40)
        for field in ("reviews", "checks", "merge", "policy"): value.pop(field)
        result = report(value)
        self.assertEqual(("pass", "cleanup-only", "not-applicable"), (result["verdict"], result["mode"], result["merge_admission"]))

    def test_skipping_requires_policy(self):
        value = snapshot(); value["checks"]["items"][0]["bucket"] = "skipping"
        self.assertEqual("block", report(value)["verdict"])
        value["policy"]["allow_required_skipping"] = True
        self.assertEqual("pass", report(value)["verdict"])

    def test_cli_exit_codes(self):
        continuing = snapshot(); continuing["reviews"]["unresolved_thread_ids"] = ["T1"]
        continuing["reviews"]["reconciliation"]["initial_unresolved_thread_ids"] = ["T1"]
        obstructed = snapshot(); obstructed["checks"]["items"][0]["bucket"] = "cancel"
        def run(value):
            return subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(value), text=True, capture_output=True).returncode
        self.assertEqual((0, 3, 2), (run(snapshot()), run(continuing), run(obstructed)))


if __name__ == "__main__":
    unittest.main()
