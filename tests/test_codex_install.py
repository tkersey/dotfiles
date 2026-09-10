"""Exercise the real installer without changing live config or HOME."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


class CodexInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="codex install ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        for relative in ("install", "etc/codex/config.toml", "home/.codex/config.toml"):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / relative, target)
        self.stage = self.root / "stage"
        self.system = self.stage / "etc/codex/config.toml"
        self.home = self.stage / Path(os.environ["HOME"]).relative_to("/") / ".codex/config.toml"
        self.env = dict(os.environ, DESTDIR=str(self.stage))
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.stub("sudo", "exit 91")
        self.env["PATH"] = str(self.bin) + os.pathsep + self.env["PATH"]

    def stub(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/bash\n" + body + "\n")
        path.chmod(0o755)

    def run_install(self, *args, success=True):
        result = subprocess.run(
            [str(self.repo / "install"), *(args or ("--codex-config",))],
            cwd=self.repo, env=self.env, capture_output=True, text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def assert_installed(self):
        for destination, source, mode in (
            (self.system, "etc/codex/config.toml", 0o644),
            (self.home, "home/.codex/config.toml", 0o600),
        ):
            self.assertFalse(destination.is_symlink())
            self.assertEqual(destination.read_bytes(), (self.repo / source).read_bytes())
            self.assertEqual(destination.stat().st_mode & 0o777, mode)

    def test_fresh_install_and_unchanged_rerun(self):
        self.run_install()
        self.assert_installed()
        before = [p.stat().st_mtime_ns for p in (self.system, self.home)]
        self.run_install()
        self.assertEqual(before, [p.stat().st_mtime_ns for p in (self.system, self.home)])
        self.assertEqual(list(self.stage.rglob("*.backup.*")), [])

    def test_regular_configs_are_backed_up_before_update(self):
        self.run_install()
        self.system.write_text('model = "previous-system"\n')
        self.home.write_text('model = "previous-user"\n')
        self.run_install()
        self.assert_installed()
        for destination, previous in ((self.system, 'model = "previous-system"\n'),
                                      (self.home, 'model = "previous-user"\n')):
            backups = list(destination.parent.glob("config.toml.backup.*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), previous)

    def test_symlinks_become_regular_files_without_writing_targets(self):
        for destination in (self.system, self.home):
            destination.parent.mkdir(parents=True, exist_ok=True)
            target = destination.parent / "original.toml"
            target.write_text('model = "live-old-value"\n')
            destination.symlink_to(target)
        self.run_install()
        self.assert_installed()
        for destination in (self.system, self.home):
            self.assertEqual((destination.parent / "original.toml").read_text(),
                             'model = "live-old-value"\n')
            backup, = destination.parent.glob("config.toml.backup.*")
            self.assertFalse(backup.is_symlink())
            self.assertEqual(backup.read_text(), 'model = "live-old-value"\n')

    def test_dangling_links_are_replaced(self):
        for destination in (self.system, self.home):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(destination.parent / "removed-by-checkout.toml")
        self.run_install()
        self.assert_installed()

    def test_failed_copy_preserves_destination_and_cleans_temporary_file(self):
        self.system.parent.mkdir(parents=True)
        self.system.write_text('model = "keep-me"\n')
        self.stub("install", "exit 75")
        self.run_install(success=False)
        self.assertEqual(self.system.read_text(), 'model = "keep-me"\n')
        self.assertEqual(list(self.stage.rglob("*.install.*")), [])
        self.assertFalse(self.home.exists())

    def test_invalid_user_destination_fails_before_system_write(self):
        self.home.mkdir(parents=True)
        self.run_install(success=False)
        self.assertFalse(self.system.exists())

    def test_missing_user_source_fails_before_system_write(self):
        (self.repo / "home/.codex/config.toml").unlink()
        self.run_install(success=False)
        self.assertFalse(self.system.exists())

    def test_staging_rejects_other_operations(self):
        self.run_install("--codex-config", "--symlink", success=False)
        self.assertFalse(self.stage.exists())


if __name__ == "__main__":
    unittest.main()
