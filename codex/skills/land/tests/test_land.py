import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
PROTOCOL = (SKILL_DIR / "references" / "landing-protocol.md").read_text(encoding="utf-8")
RECORD = (SKILL_DIR / "references" / "land-record.md").read_text(encoding="utf-8")
AGENT = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
SCRIPT = SKILL_DIR / "scripts" / "evaluate_preflight.py"
CASES = json.loads(
    (Path(__file__).resolve().parent / "fixtures" / "preflight-cases.json").read_text(
        encoding="utf-8"
    )
)

spec = importlib.util.spec_from_file_location("land_preflight", SCRIPT)
assert spec is not None and spec.loader is not None
land_preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(land_preflight)


def report(name: str) -> dict:
    return land_preflight.evaluate(CASES[name])["land_preflight"]


class LandContractTests(unittest.TestCase):
    def test_trigger_is_explicit_and_excludes_broad_nearby_tasks(self) -> None:
        self.assertIn("allow_implicit_invocation: false", AGENT)
        for phrase in (
            "watch CI",
            "close an unmerged PR",
            "delete a branch",
            "sync local state",
            "open/update a PR",
        ):
            self.assertIn(phrase, SKILL.split("---", 2)[1])

    def test_exact_head_guard_is_required(self) -> None:
        self.assertIn("--match-head-commit", PROTOCOL)
        self.assertIn("headRefOid", SKILL)
        self.assertIn("expected head OID", SKILL)
        for line in PROTOCOL.splitlines():
            if line.strip().startswith("gh pr merge"):
                self.assertNotIn("--delete-branch", line)

    def test_queue_auto_and_cleanup_only_are_distinct_modes(self) -> None:
        for mode in (
            "merge-now",
            "queue-and-wait",
            "auto-merge-and-wait",
            "cleanup-only",
            "blocked",
        ):
            self.assertIn(mode, SKILL)
            self.assertIn(mode, RECORD)

    def test_terminal_readback_precedes_cleanup(self) -> None:
        self.assertLess(
            SKILL.index("## Landing postcondition"),
            SKILL.index("## Cleanup transaction"),
        )
        self.assertIn("state == MERGED", SKILL)
        self.assertIn("mergedAt", SKILL)
        self.assertIn("mergeCommit OID", SKILL)

    def test_cancelled_checks_are_explicitly_blocked(self) -> None:
        self.assertRegex(SKILL, r"`fail`, `pending`, or `cancel` blocks")
        self.assertIn("Never interpret command exit zero alone as green", SKILL)

    def test_worktree_cleanup_is_branch_exact_and_fail_closed(self) -> None:
        for phrase in (
            "git worktree list --porcelain -z",
            "refs/heads/<head_ref>",
            "detached worktree at the same commit is not associated",
            "git worktree remove -- <path>",
            "never use `git worktree remove --force`",
            "never delete the directory with `rm -rf`",
            "primary worktree",
            "locked worktrees",
            "clean tracked and untracked status",
        ):
            self.assertIn(phrase, SKILL)
        self.assertIn("no inventory record contains", PROTOCOL)

    def test_worktree_cleanup_precedes_local_branch_deletion(self) -> None:
        order = SKILL.split("Order:", 1)[1].split("### Associated worktrees", 1)[0]
        self.assertLess(order.index("associated worktrees"), order.index("local head branch"))
        self.assertIn("no worktree is associated with it", SKILL)

    def test_land_record_keeps_merge_and_cleanup_independent(self) -> None:
        for field in (
            "record_version: LAND-v1",
            "postcondition:",
            "associated_worktrees:",
            "remote_branch:",
            "local_branch:",
            "overall: complete | degraded",
        ):
            self.assertIn(field, RECORD)
        self.assertIn("cleanup blocker does not", RECORD)

    def test_pure_evaluator_and_contract_are_packaged(self) -> None:
        self.assertIn("evaluate_preflight.py", SKILL)
        self.assertIn("The evaluator is pure", PROTOCOL)
        self.assertTrue(SCRIPT.exists())
        self.assertTrue((SKILL_DIR / "references" / "decision-contract.yaml").exists())

    def test_skill_remains_below_package_line_budget(self) -> None:
        self.assertLessEqual(len(SKILL.splitlines()), 500)


class EvaluatePreflightTests(unittest.TestCase):
    def test_immediate_route(self) -> None:
        value = report("merge-now")
        self.assertEqual("pass", value["verdict"])
        self.assertEqual("merge-now", value["mode"])
        self.assertEqual([], value["blockers"])

    def test_queue_and_auto_are_nonterminal_routes(self) -> None:
        self.assertEqual("queue-and-wait", report("queue")["mode"])
        self.assertEqual("auto-merge-and-wait", report("auto")["mode"])

    def test_cancelled_required_check_blocks(self) -> None:
        value = report("cancelled")
        self.assertEqual("block", value["verdict"])
        self.assertIn(
            "REQUIRED_CHECK_CANCELLED",
            {item["code"] for item in value["blockers"]},
        )

    def test_head_drift_blocks(self) -> None:
        value = report("head-mismatch")
        self.assertEqual("block", value["verdict"])
        self.assertIn(
            "TARGET_HEAD_MISMATCH",
            {item["code"] for item in value["blockers"]},
        )
        self.assertEqual("fail", value["gates"]["exact_head"])

    def test_already_merged_routes_to_cleanup_only(self) -> None:
        value = report("already-merged")
        self.assertEqual("pass", value["verdict"])
        self.assertEqual("cleanup-only", value["mode"])

    def test_required_skipping_needs_explicit_policy(self) -> None:
        snapshot = json.loads(json.dumps(CASES["merge-now"]))
        snapshot["checks"]["items"][0]["bucket"] = "skipping"
        self.assertEqual(
            "block",
            land_preflight.evaluate(snapshot)["land_preflight"]["verdict"],
        )
        snapshot["policy"]["allow_required_skipping"] = True
        self.assertEqual(
            "pass",
            land_preflight.evaluate(snapshot)["land_preflight"]["verdict"],
        )

    def test_cli_exit_code_matches_verdict(self) -> None:
        passed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(CASES["merge-now"]),
            check=False,
            capture_output=True,
            text=True,
        )
        blocked = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(CASES["cancelled"]),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, passed.returncode)
        self.assertEqual(2, blocked.returncode)


if __name__ == "__main__":
    unittest.main()
