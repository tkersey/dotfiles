import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch


def load_module():
    module_path = Path(__file__).with_name("saddle_up.py")
    spec = importlib.util.spec_from_file_location("saddle_up", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AGENTS_TEXT = textwrap.dedent(
    """
    # Harness

    Retry immediately with only required fields; if that fails again, switch to the smallest read/search step or ask one blocking question.
    Use workdir instead of cd ... && ...
    If progress is blocked by an external hard stop such as model quota, auth failure, provider outage, missing required credentials, or network denial, report that blocker immediately with the exact failing command or provider/model and any known retry or reset signal.
    If a command, test, or proof step was not executed in this turn, say `not run`; do not imply success.
    """
).lstrip()


def init_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tests"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (repo / "AGENTS.md").write_text(AGENTS_TEXT, encoding="utf-8")
    subprocess.run(["git", "add", "AGENTS.md"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


class SaddleUpGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def parse_run_args(self, repo: Path):
        parser = self.mod.build_parser()
        return parser.parse_args(
            [
                "run",
                "--repo",
                str(repo),
                "--harness-path",
                "AGENTS.md",
                "--model",
                "google/gemini-2.5-pro",
                "--no-commit",
                "--max-cycles",
                "1",
                "--opencode-timeout-seconds",
                "600",
            ]
        )

    def latest_run(self, repo: Path) -> dict:
        runs_path = repo / ".saddle-up" / "runs.jsonl"
        return json.loads(runs_path.read_text(encoding="utf-8").splitlines()[-1])

    def test_post_improver_gate_reverts_bad_diff_and_skips_mixed_eval(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            init_repo(repo)
            original_text = (repo / "AGENTS.md").read_text(encoding="utf-8")
            args = self.parse_run_args(repo)

            eval_calls = []

            def fake_run_opencode(_repo, _model, message, *, timeout_seconds=None):
                _ = timeout_seconds
                if message.startswith("Improve `AGENTS.md`"):
                    agents = repo / "AGENTS.md"
                    agents.write_text(
                        original_text
                        + "\nRetry immediately with only required fields so the loop sounds smoother.\n",
                        encoding="utf-8",
                    )
                return {
                    "cmd": [],
                    "returncode": 0,
                    "events": [],
                    "output_text": "ok",
                    "stdout": "",
                    "stderr": "",
                    "timed_out": False,
                    "external_blocker": None,
                }

            def fake_evaluate_iteration(_repo, _model, selected_cases, _scoring, **_kwargs):
                eval_calls.append([case["id"] for case in selected_cases])
                if len(eval_calls) == 1:
                    return (
                        [
                            {
                                "id": "curated-gemini-retry-path",
                                "passed": False,
                                "external_blocker": None,
                            }
                        ],
                        0.0,
                    )
                if len(eval_calls) == 2:
                    return (
                        [
                            {
                                "id": "curated-gemini-retry-path",
                                "passed": True,
                                "external_blocker": None,
                            }
                        ],
                        1.0,
                    )
                raise AssertionError("mixed eval should be skipped after a rejected improver diff")

            with (
                patch.object(self.mod, "require_command", return_value=None),
                patch.object(self.mod, "run_opencode", side_effect=fake_run_opencode),
                patch.object(self.mod, "evaluate_iteration", side_effect=fake_evaluate_iteration),
            ):
                rc = self.mod.run_loop(args)

            self.assertEqual(rc, 0)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), original_text)
            self.assertEqual(len(eval_calls), 2)
            latest = self.latest_run(repo)
            self.assertTrue(latest["post_improver_curated_gate_ran"])
            self.assertFalse(latest["post_improver_curated_gate_passed"])
            self.assertTrue(latest["post_improver_reverted"])
            self.assertEqual(latest["post_improver_reverted_paths"], ["AGENTS.md"])
            self.assertIn("retry-path", latest["post_improver_reverted_rule_ids"])
            self.assertEqual(latest["failed_case_ids"][0], "post-improver-curated-gate")
            self.assertEqual(latest["eval_total"], 0)

    def test_post_improver_gate_pass_allows_mixed_eval(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            init_repo(repo)
            args = self.parse_run_args(repo)

            eval_calls = []

            def fake_run_opencode(_repo, _model, message, *, timeout_seconds=None):
                _ = timeout_seconds
                if message.startswith("Improve `AGENTS.md`"):
                    agents = repo / "AGENTS.md"
                    current = agents.read_text(encoding="utf-8")
                    agents.write_text(current + "\n## Extra Notes\nKeep edits precise.\n", encoding="utf-8")
                return {
                    "cmd": [],
                    "returncode": 0,
                    "events": [],
                    "output_text": "ok",
                    "stdout": "",
                    "stderr": "",
                    "timed_out": False,
                    "external_blocker": None,
                }

            def fake_evaluate_iteration(_repo, _model, selected_cases, _scoring, **_kwargs):
                eval_calls.append([case["id"] for case in selected_cases])
                return (
                    [
                        {
                            "id": str(selected_cases[0]["id"]),
                            "passed": True,
                            "external_blocker": None,
                        }
                    ],
                    1.0,
                )

            with (
                patch.object(self.mod, "require_command", return_value=None),
                patch.object(self.mod, "run_opencode", side_effect=fake_run_opencode),
                patch.object(self.mod, "evaluate_iteration", side_effect=fake_evaluate_iteration),
            ):
                rc = self.mod.run_loop(args)

            self.assertEqual(rc, 0)
            self.assertEqual(len(eval_calls), 2)
            latest = self.latest_run(repo)
            self.assertTrue(latest["post_improver_curated_gate_ran"])
            self.assertTrue(latest["post_improver_curated_gate_passed"])
            self.assertFalse(latest["post_improver_reverted"])
            self.assertGreater(latest["eval_total"], 0)
            self.assertTrue(latest["gate_passed"])


if __name__ == "__main__":
    unittest.main()
