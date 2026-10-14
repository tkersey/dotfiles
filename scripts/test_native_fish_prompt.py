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
            # Direct render tests inspect a completed snapshot at a wide width.
            # Reader-driven async repaint is exercised separately under a PTY.
            "set -g native_prompt_async 0; "
            "set -g COLUMNS 240; "
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
            "fish_prompt", "fish_right_prompt", "fish_mode_prompt", "fish_user_key_bindings",
        )]
        files += sorted((ROOT / "fish/functions").glob("__native_prompt*.fish"))
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

    def test_prompt_retains_pipeline_failure(self) -> None:
        self.assertIn("✔ 1|0", plain(self.run_fish("false | true; fish_prompt; fish_right_prompt")))
        self.assertIn("✘ 0|1", plain(self.run_fish("true | false; fish_prompt; fish_right_prompt")))
        output = plain(self.run_fish(
            f"command {quote(FISH)} --no-config -c 'exit 2'; fish_prompt; fish_right_prompt"
        ))
        self.assertIn("✘ 2", output)
        self.assertTrue(plain(self.run_fish("false; fish_prompt; fish_right_prompt")).endswith(" 09:30:00 AM"))

    def test_normal_prompt_order_preserves_pipeline_failure(self) -> None:
        output = plain(self.run_fish("false | true; fish_prompt; fish_right_prompt"))
        self.assertIn("✔ 1|0", output)
        output = plain(self.run_fish("true | false; fish_prompt; fish_right_prompt"))
        self.assertIn("✘ 0|1", output)

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

    def test_detached_head_has_distinct_amber_color(self) -> None:
        repo = self.repository()
        branch = self.run_fish("true; fish_prompt", cwd=repo)
        self.assertIn("\x1b[38;2;95;215;0mmain", branch)
        self.assertNotIn("\x1b[38;2;215;175;0m", branch)
        self.git(repo, "checkout", "--detach", "HEAD")
        detached = self.run_fish("true; fish_prompt", cwd=repo)
        self.assertIn("\x1b[38;2;215;175;0m", detached)
        self.assertNotIn("main", plain(detached))
        # The status-colored chevron remains green; only Git identity changes.
        self.assertIn("\x1b[38;2;95;215;0m ❯ ", detached)

    def test_transient_render_keeps_context_and_failure_without_collection(self) -> None:
        repo = self.repository()
        self.stub("node", "v22.5.1")
        (repo / "package.json").write_text("{}\n")
        output = plain(self.run_fish(
            "set -g native_prompt_context_items node; "
            "set -g CMD_DURATION 65000; false | true; fish_prompt >/dev/null; "
            # Neither final prompt function may invoke a fresh collector.
            "function __native_prompt_refresh; printf 'UNEXPECTED-COLLECTION'; end; "
            "fish_prompt --final-rendering; printf '\\n'; "
            "fish_right_prompt --final-rendering",
            cwd=repo,
        ))
        self.assertEqual(output.count("\n"), 1)
        left, right = output.split("\n")
        for expected in ("project", "main", "✔ 1|0", " ❯ "):
            self.assertIn(expected, left)
        for absent in ("UNEXPECTED-COLLECTION", "22.5.1", "09:30:00 AM", "", "", ""):
            self.assertNotIn(absent, output)
        self.assertEqual(right, "")

    def test_narrow_prompt_preserves_identity_and_failure_on_left(self) -> None:
        for identity in ("ssh", "root"):
            with self.subTest(identity=identity):
                setup = "set -g SSH_CONNECTION fixture; " if identity == "ssh" else (
                    "function fish_is_root_user; return 0; end; "
                )
                output = plain(self.run_fish(
                    "set -g COLUMNS 45; set -g USER operator; "
                    + setup + "true | false; fish_prompt; printf '\\n'; fish_right_prompt"
                ))
                left, right = output.split("\n")
                self.assertIn("operator@" + os.uname().nodename.split(".")[0], left)
                self.assertIn("✘ 0|1", left)
                self.assertEqual(right, "")

    def test_narrow_prompt_drops_details_before_cloud_jobs_and_duration(self) -> None:
        self.stub("node", "v22.5.1")
        self.stub("kubectl", "cluster/team")
        (self.home / "package.json").write_text("{}\n")
        setup = (
            # Put the runtime first to verify priority is independent of config order.
            "set -g native_prompt_context_items node kubectl; "
            "function jobs; "
            "if contains -- --query $argv; return 0; "
            "else if contains -- --pid $argv; printf '4242\\n'; end; end; "
            "set -g CMD_DURATION 65000; true; fish_prompt >/dev/null; "
        )
        wide = plain(self.run_fish(setup + "fish_right_prompt"))
        for expected in ("cluster/team", "", " 1m 5s", "22.5.1", "09:30:00 AM"):
            self.assertIn(expected, wide)
        narrow = plain(self.run_fish(setup + "set -g COLUMNS 72; fish_right_prompt"))
        for expected in ("cluster/team", "", " 1m 5s"):
            self.assertIn(expected, narrow)
        self.assertNotIn("22.5.1", narrow)
        self.assertNotIn("09:30:00 AM", narrow)

    def test_details_binding_and_toggle_preserve_saved_command_result(self) -> None:
        self.stub("node", "v22.5.1")
        self.stub("kubectl", "cluster/team")
        (self.home / "package.json").write_text("{}\n")
        output = self.run_fish(
            "function fzf_key_bindings; end; fish_user_key_bindings; "
            "for mode in insert default visual; bind --mode $mode ctrl-alt-p; end; "
            "set -g native_prompt_context_items node kubectl; set -g CMD_DURATION 65000; "
            "false | true; fish_prompt >/dev/null; "
            # Stand in only for the reader's repaint request, unavailable without
            # a TTY; keep the actual toggle and rendering behavior under test.
            "function commandline; set -g requested_repaint $argv; end; "
            "__native_prompt_toggle_details; "
            "printf 'OFF:%s;STATUS:%s;PIPE:%s;DURATION:%s;REPAINT:%s\\n' "
            "$native_prompt_show_details $__native_prompt_last_status "
            "(string join '|' $__native_prompt_last_pipestatus) "
            "$__native_prompt_last_duration (string join ' ' -- $requested_repaint); "
            "fish_right_prompt; printf '\\n'; "
            "__native_prompt_toggle_details; printf 'ON:%s\\n' $native_prompt_show_details; "
            "fish_right_prompt"
        )
        self.assertEqual(output.count("ctrl-alt-p __native_prompt_toggle_details"), 3)
        self.assertIn("OFF:0;STATUS:0;PIPE:1|0;DURATION:65000;REPAINT:--function repaint", output)
        lines = plain(output).splitlines()
        off_index = next(index for index, line in enumerate(lines) if line.startswith("OFF:"))
        compact = lines[off_index + 1]
        self.assertIn("cluster/team", compact)
        self.assertIn(" 1m 5s", compact)
        self.assertNotIn("22.5.1", compact)
        self.assertNotIn("09:30:00 AM", compact)
        self.assertEqual(lines[off_index + 2], "ON:1")
        self.assertIn("22.5.1", lines[off_index + 3])
        self.assertIn("09:30:00 AM", lines[off_index + 3])

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
        python = environment / "bin/python3"
        python.unlink(missing_ok=True)
        python.write_text("#!/bin/sh\nprintf 'Python 3.12.0\\n'\n")
        python.chmod(0o755)
        output = plain(self.run_fish(
            f"source {quote(environment / 'bin/activate.fish')}; "
            "set -g native_prompt_context_items python; true; fish_prompt; "
            "printf '\\n'; fish_right_prompt",
            cwd=environment.parent,
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
    from test_native_fish_prompt_async import AsyncPromptTests

    unittest.main(verbosity=2)
