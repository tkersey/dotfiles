#!/usr/bin/env python3
"""Behavioral checks in isolated Fish sessions; never read/write the live Fish config.

Run from the repository root: uv run --no-project scripts/test_native_fish_prompt.py
Requires Fish 4.x, Git, and the existing git-wrapper dependency hub.
No third-party Python packages are needed.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import venv

ROOT = Path(__file__).resolve().parents[1]
FISH = shutil.which("fish")
ANSI = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\([A-Z])")


def quote(value: str | Path) -> str:
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def plain(value: str) -> str:
    return ANSI.sub("", value)


class NativePromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sandbox = tempfile.TemporaryDirectory(prefix="native-fish-")
        self.addCleanup(self.sandbox.cleanup)
        self.base = Path(self.sandbox.name).resolve()
        self.home = self.base / "home"
        self.bin = self.base / "bin"
        self.home.mkdir()
        self.bin.mkdir()
        # Use real Git through a private path, avoiding macOS command-line-tools
        # bootstrap detection in the shipped prompt during these behavior tests.
        git = shutil.which("git")
        if not git:
            self.fail("Git is required for the prompt tests.")
        (self.bin / "git").symlink_to(git)
        self.env = {
            "HOME": str(self.home),
            "PATH": str(self.bin) + os.pathsep + os.environ.get("PATH", "/usr/bin:/bin"),
            "TERM": "xterm-256color",
            "LC_ALL": "C.UTF-8" if os.uname().sysname == "Linux" else "en_US.UTF-8",
            "XDG_CONFIG_HOME": str(self.base / "config"),
            "XDG_DATA_HOME": str(self.base / "data"),
            "XDG_CACHE_HOME": str(self.base / "cache"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "Prompt Test",
            "GIT_AUTHOR_EMAIL": "prompt@example.invalid",
            "GIT_COMMITTER_NAME": "Prompt Test",
            "GIT_COMMITTER_EMAIL": "prompt@example.invalid",
        }
        self.stub("date", "09:30:00 AM")
        self.init = (
            f"set --prepend fish_function_path {quote(ROOT / 'fish/functions')}; "
            f"source {quote(ROOT / 'fish/conf.d/native-prompt.fish')}; "
            "set -g native_prompt_context_items; "
            "set -g fish_term24bit 1; "
            "function fish_is_root_user; return 1; end; "
        )

    def stub(self, name: str, output: str) -> None:
        target = self.bin / name
        # All fixture output is a literal, including whitespace/control characters.
        target.write_text("#!/bin/sh\nprintf '%s\\n' '" + output.replace("'", "'\\''") + "'\n")
        target.chmod(0o755)

    def run_fish(self, code: str, cwd: Path | None = None) -> str:
        result = subprocess.run(
            [FISH, "--no-config", "--interactive", "--command", self.init + code],
            cwd=cwd or self.home, env=self.env, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        # A non-TTY interactive session may warn once; runtime errors must not pass.
        errors = "\n".join(
            line for line in result.stderr.splitlines()
            if not line.startswith(("warning:", "warning "))
        ).strip()
        self.assertFalse(errors, errors)
        return result.stdout

    def git(self, directory: Path, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(directory), *arguments], env=self.env,
            check=True, capture_output=True, text=True, timeout=30,
        )
        return result.stdout

    def repository(self) -> Path:
        repo = self.home / "project"
        repo.mkdir()
        self.git(repo, "init", "--initial-branch=main")
        (repo / "tracked").write_text("original\n")
        self.git(repo, "add", "tracked")
        self.git(repo, "commit", "-m", "fixture")
        return repo

    def test_native_files_parse(self) -> None:
        files = [ROOT / "fish/conf.d/native-prompt.fish"]
        files += [ROOT / f"fish/functions/{name}.fish" for name in (
            "fish_prompt", "fish_right_prompt", "fish_mode_prompt",
            "__native_prompt_pwd", "__native_prompt_context", "__native_prompt_segment",
        )]
        for file in files:
            with self.subTest(file=file.name):
                result = subprocess.run(
                    [FISH, "--no-config", "--no-execute", str(file)], env=self.env,
                    capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_status_changes_color_not_the_fixed_chevron(self) -> None:
        success = self.run_fish("true; fish_prompt")
        failure = self.run_fish("false; fish_prompt")
        self.assertEqual(plain(success), plain(failure))
        self.assertTrue(plain(success).endswith(" ❯ "))
        self.assertIn("\x1b[38;2;95;215;0m", success)
        self.assertIn("\x1b[38;2;255;0;0m", failure)
        for mode in ("insert", "default", "replace_one", "visual"):
            output = self.run_fish(f"set -g fish_bind_mode {mode}; true; fish_prompt")
            self.assertEqual(plain(output), plain(success))

    def test_right_prompt_retains_pipeline_failure(self) -> None:
        self.assertIn("✔ 1|0", plain(self.run_fish("false | true; fish_right_prompt")))
        self.assertIn("✘ 0|1", plain(self.run_fish("true | false; fish_right_prompt")))
        output = plain(self.run_fish(f"command {quote(FISH)} --no-config -c 'exit 2'; fish_right_prompt"))
        self.assertIn("✘ 2", output)
        self.assertEqual(plain(self.run_fish("false; fish_right_prompt")), " 09:30:00 AM")

    def test_duration_threshold_and_hour_format(self) -> None:
        for duration, expected in ((3000, ""), (3001, "3s"), (65000, "1m 5s"), (3605000, "1h 0m 5s")):
            with self.subTest(duration=duration):
                output = plain(self.run_fish(f"set -g CMD_DURATION {duration}; true; fish_right_prompt"))
                if expected:
                    self.assertIn(" " + expected, output)
                else:
                    self.assertNotIn("", output)

    def test_git_state_and_switching_linked_worktrees(self) -> None:
        repo = self.repository()
        worktree = self.home / "feature-worktree"
        self.git(repo, "worktree", "add", "-b", "feature", str(worktree))
        (worktree / "tracked").write_text("changed\n")
        (worktree / "staged").write_text("staged\n")
        self.git(worktree, "add", "staged")
        (worktree / "untracked").write_text("untracked\n")
        output = plain(self.run_fish(
            f"cd {quote(repo)}; fish_prompt; printf '\\n'; "
            f"cd {quote(worktree)}; fish_prompt", cwd=repo,
        ))
        first, second = output.splitlines()
        self.assertIn("main", first)
        self.assertNotIn("feature", first)
        self.assertIn("feature", second)
        for indicator in (" +1", " !1", " ?1"):
            self.assertIn(indicator, second)

    def test_node_activation_in_ancestor_and_not_unrelated_directory(self) -> None:
        self.stub("node", "v22.5.1")
        project = self.home / "node-project"
        child = project / "src"
        child.mkdir(parents=True)
        (project / "package.json").write_text("{}\n")
        code = "set -g native_prompt_context_items node; true; fish_right_prompt"
        self.assertIn("22.5.1", plain(self.run_fish(code, child)))
        self.assertNotIn("22.5.1", plain(self.run_fish(code, self.home)))

    def test_virtualenv_activation_does_not_wrap_the_left_prompt(self) -> None:
        environment = self.home / "python-project" / ".venv"
        venv.EnvBuilder(with_pip=False).create(environment)
        output = plain(self.run_fish(
            f"source {quote(environment / 'bin/activate.fish')}; "
            "set -g native_prompt_context_items python; true; fish_prompt; "
            "printf '\\n'; true; fish_right_prompt"
        ))
        left, right = output.splitlines()
        self.assertNotIn("(.venv)", left)
        self.assertIn("(python-project)", right)
        self.assertTrue(left.endswith(" ❯ "))

    def test_kubernetes_namespace_and_control_characters(self) -> None:
        code = "set -g native_prompt_context_items kubectl; true; fish_right_prompt"
        self.stub("kubectl", "cluster/default")
        self.assertNotIn("/default", plain(self.run_fish(code)))
        self.stub("kubectl", "cluster/team")
        self.assertIn("cluster/team", plain(self.run_fish(code)))
        self.stub("kubectl", "cluster/\x1b[31mteam")
        self.assertIn("cluster/?[31mteam", plain(self.run_fish(code)))

    def test_path_shortening_preserves_project_anchor_and_current_directory(self) -> None:
        project = self.home / "long-parent-directory" / "recognizable-project"
        child = project / "long-intermediate-directory" / "src" / "current"
        child.mkdir(parents=True)
        (project / "build.zig").touch()
        output = plain(self.run_fish("__native_prompt_pwd 8", child))
        self.assertIn("recognizable-project", output)
        self.assertIn("/src/current", output)
        self.assertNotIn("long-parent-directory", output)

    def test_control_characters_in_directory_names_are_not_emitted(self) -> None:
        directory = self.home / "bad\x1b[31m\nname"
        directory.mkdir()
        raw = self.run_fish("__native_prompt_pwd 1000", directory)
        # prompt_pwd may already sanitize the name before our final escaping.
        # Check the safety contract, not a particular replacement character.
        self.assertNotIn("\x1b[31m", raw)
        output = plain(raw)
        self.assertIn("bad", output)
        self.assertIn("name", output)
        self.assertNotRegex(output, r"[\x00-\x1f\x7f-\x9f]")

    def test_noninteractive_configuration_is_silent(self) -> None:
        result = subprocess.run(
            [FISH, "--no-config", "-c", f"source {quote(ROOT / 'fish/conf.d/native-prompt.fish')}; "
             "set --query native_prompt_context_items; and exit 1; exit 0"],
            env=self.env, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))


if __name__ == "__main__":
    if not FISH:
        raise SystemExit("Fish is required: install Fish, then rerun this check.")
    unittest.main(verbosity=2)
