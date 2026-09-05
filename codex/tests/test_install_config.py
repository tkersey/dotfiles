# /// script
# requires-python = ">=3.11"
# dependencies = ["tomlkit==0.13.3"]
# ///
"""Isolated configuration migration tests; never write /etc or use real sudo."""

import contextlib
import copy
import importlib.util
import io
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

CODEX = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("install_config", CODEX / "install-config.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
BASELINE = installer.MARKER + b'''model = "shared-model"
[features]
memories = true
context_management.experimental_mode = true
[features.multi_agent_v2]
enabled = true
[tui]
status_line = ["codex-version", "git-branch"]
theme = "coldark-dark"
[mcp_servers.docs]
url = "https://example.invalid/mcp"
'''
LIVE = b'''model = "shared-model"
notify = ["/Users/local/notify", "turn-ended"] # keep this comment
[features]
memories = false # intentional override
context_management.experimental_mode = true
local_feature = true
[features.multi_agent_v2]
enabled = true
[tui]
status_line = ["codex-version", "git-branch"]
theme = "coldark-dark"
[tui.model_availability_nux]
"local-model" = 4
[projects."/tmp/local project"]
trust_level = "trusted"
[marketplaces.local]
source = "/Users/local/.cache/plugins"
[plugins."browser@local"]
enabled = true
[desktop]
appearanceLightCodeThemeId = "rose-pine"
[desktop.fonts]
[notice]
fast_default_opt_out = true
[mcp_servers.docs]
url = "https://example.invalid/mcp"
[mcp_servers.node_repl]
command = "/Applications/ChatGPT.app/node_repl"
[mcp_servers.node_repl.env]
CODEX_HOME = "/Users/local/.codex"
[shell_environment_policy.set]
LOCAL_HASH = "sensitive-test-value"
[unknown_future_section]
text = """a multiline value
that must survive unchanged"""
'''


def parsed(data):
    return tomllib.loads(data.decode())


def overlay(base, overrides):
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = overlay(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="codex test ")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "repo" / "config.toml"
        self.user = self.root / "home" / "config.toml"
        self.system = self.root / "etc" / "codex" / "config.toml"
        self.source.parent.mkdir()
        self.user.parent.mkdir()
        self.source.write_bytes(BASELINE)
        self.user.write_bytes(LIVE)
        # Exercise real install/mktemp/mv operations, but only under this temp root.
        self.commands = []
        self.privilege = patch.object(installer, "privileged", side_effect=self.run_unprivileged).start()
        self.addCleanup(patch.stopall)

    def run_unprivileged(self, *args):
        self.commands.append(args)
        return subprocess.run([str(arg) for arg in args], check=True, text=True,
                              stdout=subprocess.PIPE).stdout.strip()

    def run_install(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            installer.install_config(self.source, self.user, self.system, **kwargs)
        return output.getvalue()

    def test_preserves_effective_values_and_local_state(self):
        self.run_install()
        remainder = self.user.read_bytes()
        self.assertEqual(overlay(parsed(BASELINE), parsed(LIVE)),
                         overlay(parsed(self.system.read_bytes()), parsed(remainder)))
        self.assertNotIn("model", parsed(remainder))
        self.assertEqual(parsed(remainder)["features"], {"memories": False, "local_feature": True})
        self.assertNotIn("docs", parsed(remainder)["mcp_servers"])
        self.assertIn(b"# keep this comment", remainder)
        self.assertIn(b"# intentional override", remainder)
        for key in ("notify", "projects", "marketplaces", "plugins", "desktop", "notice",
                    "shell_environment_policy", "unknown_future_section"):
            self.assertEqual(parsed(LIVE)[key], parsed(remainder)[key])
        backups = list(self.user.parent.glob("config.toml.backup.*"))
        self.assertEqual([p.read_bytes() for p in backups], [LIVE])
        for path in [self.user, *backups]:
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.system.stat().st_mode), 0o644)
        self.assertEqual(self.source.read_bytes(), BASELINE)

    def test_repeated_install_is_byte_and_backup_idempotent(self):
        self.run_install()
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.commands.clear()
        self.run_install()
        after = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(self.commands, [])

    def test_future_baseline_update_is_not_shadowed_by_old_duplicates(self):
        self.run_install()
        updated = BASELINE.replace(b"shared-model", b"next-model")
        self.source.write_bytes(updated)
        self.run_install()
        self.assertEqual(self.system.read_bytes(), updated)
        self.assertNotIn("model", parsed(self.user.read_bytes()))
        backup, = self.system.parent.glob("config.toml.backup.*")
        self.assertEqual(backup.read_bytes(), BASELINE)
        self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)

    def test_detaches_live_link_from_another_worktree_without_writing_target(self):
        live_target = self.root / "old repo config.toml"
        live_target.write_bytes(LIVE + b'\nextra_local = "uncommitted"\n')
        expected = live_target.read_bytes()
        self.user.unlink()
        self.user.symlink_to(live_target)
        self.run_install()
        self.assertFalse(self.user.is_symlink())
        self.assertEqual(live_target.read_bytes(), expected)
        backup, = self.user.parent.glob("config.toml.backup.*")
        self.assertEqual(backup.read_bytes(), expected)

    def test_rejects_already_pulled_link_to_reduced_baseline(self):
        other_checkout = self.root / "another reduced checkout.toml"
        other_checkout.write_bytes(BASELINE)
        for target in (self.source, other_checkout):
            with self.subTest(target=target):
                self.user.unlink()
                self.user.symlink_to(target)
                with self.assertRaisesRegex(RuntimeError, "BEFORE pulling"):
                    self.run_install()
                self.assertTrue(self.user.is_symlink())
                self.assertFalse(self.system.exists())
                self.assertEqual(self.commands, [])

    def test_rejects_user_system_alias(self):
        with self.assertRaisesRegex(RuntimeError, "must be different"):
            installer.install_config(self.source, self.user, self.user)
        self.assertEqual(self.user.read_bytes(), LIVE)

    def test_rejects_dangling_user_link(self):
        self.user.unlink()
        self.user.symlink_to(self.root / "missing")
        with self.assertRaises(FileNotFoundError):
            self.run_install()
        self.assertTrue(self.user.is_symlink())
        self.assertEqual(self.commands, [])

    def test_fresh_install_never_seeds_another_machines_state(self):
        self.user.unlink()
        self.user.parent.rmdir()
        self.run_install()
        self.assertEqual(parsed(self.user.read_bytes()), {})
        self.assertEqual(self.system.read_bytes(), BASELINE)
        self.assertFalse(list(self.user.parent.glob("*.backup.*")))

    def test_dry_run_has_no_writes_or_privilege_and_does_not_print_secrets(self):
        before = set(self.root.rglob("*"))
        output = self.run_install(dry_run=True)
        self.assertEqual(set(self.root.rglob("*")), before)
        self.assertEqual(self.user.read_bytes(), LIVE)
        self.assertEqual(self.commands, [])
        self.assertNotIn("sensitive-test-value", output)
        self.user.unlink()
        self.user.parent.rmdir()
        self.run_install(dry_run=True)
        self.assertFalse(self.user.parent.exists())

    def test_invalid_toml_fails_before_any_writes(self):
        for path in (self.user, self.source):
            with self.subTest(path=path):
                original = path.read_bytes()
                path.write_bytes(installer.MARKER + b"invalid = [")
                with self.assertRaises(ValueError):
                    self.run_install()
                self.assertFalse(self.system.exists())
                self.assertEqual(self.commands, [])
                self.assertFalse(list(self.user.parent.glob("*.backup.*")))
                path.write_bytes(original)

    def test_unmanaged_system_config_is_not_overwritten(self):
        self.system.parent.mkdir(parents=True)
        self.system.write_bytes(b'model = "admin-owned"\n')
        with self.assertRaisesRegex(RuntimeError, "not managed"):
            self.run_install()
        self.assertEqual(self.system.read_bytes(), b'model = "admin-owned"\n')
        self.assertEqual(self.user.read_bytes(), LIVE)
        self.assertEqual(self.commands, [])

    def test_system_symlink_is_not_replaced(self):
        self.system.parent.mkdir(parents=True)
        self.system.symlink_to(self.source)
        with self.assertRaisesRegex(RuntimeError, "symlink"):
            self.run_install()
        self.assertTrue(self.system.is_symlink())
        self.assertEqual(self.commands, [])

    def test_failed_system_install_does_not_prune_the_user_file(self):
        self.privilege.side_effect = subprocess.CalledProcessError(1, ["sudo", "install"])
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_install()
        self.assertEqual(self.user.read_bytes(), LIVE)
        self.assertFalse(list(self.user.parent.glob(".config.toml.*")))
        backup, = self.user.parent.glob("config.toml.backup.*")
        self.assertEqual(backup.read_bytes(), LIVE)

    def test_concurrent_local_edit_is_not_clobbered(self):
        changed = LIVE + b'\nconcurrent = true\n'
        with patch.object(installer, "deploy_system", side_effect=lambda *args: self.user.write_bytes(changed)):
            with self.assertRaisesRegex(RuntimeError, "local config changed"):
                self.run_install()
        self.assertEqual(self.user.read_bytes(), changed)

    def test_concurrent_system_edit_is_not_clobbered(self):
        def change_after_staging(*args):
            result = self.run_unprivileged(*args)
            if args[:3] == ("install", "-m", "0644"):
                self.system.write_bytes(b'model = "concurrent-system"\n')
            return result
        self.privilege.side_effect = change_after_staging
        with self.assertRaisesRegex(RuntimeError, "System config changed"):
            self.run_install()
        self.assertEqual(self.system.read_bytes(), b'model = "concurrent-system"\n')
        self.assertEqual(self.user.read_bytes(), LIVE)
        self.assertFalse(list(self.system.parent.glob(".config.toml.*")))

    def test_inline_tables_arrays_and_type_distinctions(self):
        data = b'features = { memories = true, local = 7 }\narray = [true, 2]\ninteger = 1\nfloat = 1.0\n'
        defaults = {"features": {"memories": True}, "array": [1, 2], "integer": True, "float": 1}
        result = parsed(installer.local_remainder(data, defaults))
        self.assertEqual(result["features"], {"local": 7})
        self.assertIn("array", result)
        self.assertIn("integer", result)
        self.assertIn("float", result)

    def test_cli_respects_codex_home_and_rejects_sudo_invocation(self):
        with patch.dict(os.environ, {"CODEX_HOME": str(self.root / "custom home")}), \
             patch.object(sys, "argv", ["install-config.py", "--dry-run"]), \
             patch.object(installer, "install_config") as install:
            installer.main()
            self.assertEqual(install.call_args.args[1], self.root / "custom home" / "config.toml")
        with patch.object(os, "geteuid", return_value=0), \
             patch.object(sys, "argv", ["install-config.py"]), \
             contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            installer.main()

    def test_repository_baseline_is_portable_and_links_are_unchanged_except_config(self):
        baseline = (CODEX / "config.toml").read_bytes()
        self.assertTrue(baseline.startswith(installer.MARKER))
        config = parsed(baseline)
        for key in ("notify", "projects", "plugins", "marketplaces", "desktop", "shell_environment_policy", "notice"):
            self.assertNotIn(key, config)
        self.assertEqual(set(config["mcp_servers"]), {"openaiDeveloperDocs"})
        self.assertNotIn("model_availability_nux", config["tui"])
        self.assertNotIn(b"/Users/", baseline)
        self.assertNotIn(b"/Applications/", baseline)
        links = (CODEX.parent / "links.conf").read_text()
        self.assertNotIn("codex/config.toml:$HOME/.codex/config.toml", links)
        self.assertIn("codex/skills:$HOME/.agents/skills", links)
        self.assertIn("codex/agents:$HOME/.codex/agents", links)

    def test_installer_flag_routes_only_codex_and_propagates_failure(self):
        binary = self.root / "bin"
        binary.mkdir()
        uv = binary / "uv"
        uv.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\nexit "${UV_TEST_STATUS:-0}"\n')
        uv.chmod(0o755)
        env = {**os.environ, "PATH": str(binary) + os.pathsep + os.environ["PATH"]}
        command = ["bash", str(CODEX.parent / "install"), "--codex-config"]
        result = subprocess.run(command, cwd=CODEX.parent, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--script\n" + str(CODEX / "install-config.py"), result.stdout)
        self.assertNotIn("creating symlinks", result.stdout)
        env["UV_TEST_STATUS"] = "7"
        result = subprocess.run(command, cwd=CODEX.parent, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 7)
        self.assertNotIn("All installed!", result.stdout)

    def test_documented_pre_pull_preservation_keeps_live_bytes(self):
        docs = (CODEX / "CONFIGURATION.md").read_text()
        command = docs.split("```sh\n", 1)[1].split("```", 1)[0]
        self.user.unlink()
        live_target = self.root / "old repository config"
        live_target.write_bytes(LIVE)
        self.user.symlink_to(live_target)
        env = {**os.environ, "CODEX_HOME": str(self.user.parent)}
        for _ in range(2):
            subprocess.run(["bash", "-c", command], env=env, check=True, capture_output=True)
        self.assertFalse(self.user.is_symlink())
        self.assertEqual(self.user.read_bytes(), LIVE)
        self.assertEqual(live_target.read_bytes(), LIVE)
        backup, = self.user.parent.glob("*.pre-system-split.*")
        self.assertEqual(backup.read_bytes(), LIVE)
        self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)
        live_target.write_bytes(BASELINE)  # Simulate pulling the reduced tracked file.
        self.assertEqual(self.user.read_bytes(), LIVE)
        self.run_install()
        self.assertEqual(overlay(parsed(BASELINE), parsed(self.user.read_bytes())),
                         overlay(parsed(BASELINE), parsed(LIVE)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
