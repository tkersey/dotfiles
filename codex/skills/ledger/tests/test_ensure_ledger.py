"""Bootstrap regressions; no real Ledger, Homebrew, network, or store access.

Run: uv run codex/skills/ledger/tests/test_ensure_ledger.py
The isolated PATH contains only Bash, cat, and test doubles. These tests establish
bootstrap behavior, not native artifact validation or model effectiveness.
"""
from __future__ import annotations

import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ensure-ledger"
BASH = shutil.which("bash")
CHMOD = shutil.which("chmod")
CAT = shutil.which("cat")
FORMULA = "tkersey/tap/ledger"


def ledger_stub(version="1.0.3", abi="ledger-artifact-abi/v1", version_exit=0,
                capabilities_exit=0):
    return f"""#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$MOCK_LEDGER_LOG"
case "$*" in
  version)
    printf '%s\\n' {shlex.quote(version)}
    exit {version_exit} ;;
  'capabilities --format text')
    printf '%s\\n' {shlex.quote('ABI: ' + abi)}
    exit {capabilities_exit} ;;
  *) exit 64 ;;
esac
"""


BREW_STUB = """#!/usr/bin/env bash
set -eu
printf '%s\\n' "$*" >> "$MOCK_BREW_LOG"
case "$1" in
  list) [[ -f "$MOCK_INSTALLED" ]] ;;
  install|upgrade)
    printf '%s\\n' 'mock Homebrew diagnostic' >&2
    if [[ "${MOCK_BREW_EXIT:-0}" != 0 ]]; then
      exit "$MOCK_BREW_EXIT"
    fi
    printf '%s\\n' "$MOCK_LEDGER_AFTER" > "$MOCK_BIN/ledger"
    "$MOCK_CHMOD" +x "$MOCK_BIN/ledger"
    : > "$MOCK_INSTALLED" ;;
  *) exit 64 ;;
esac
"""


@unittest.skipUnless(BASH and CHMOD and CAT, "Bash, chmod, and cat are required")
class BootstrapTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="ledger-bootstrap-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        (self.bin / "bash").symlink_to(BASH)
        (self.bin / "cat").symlink_to(CAT)
        self.brew_log = self.root / "brew.log"
        self.ledger_log = self.root / "ledger.log"
        self.installed = self.root / "installed"
        self.env = {
            "PATH": str(self.bin), "HOME": str(self.root), "LC_ALL": "C",
            "TMPDIR": str(self.root), "LEDGER_BOOTSTRAP_OS": "Linux",
            "MOCK_BIN": str(self.bin), "MOCK_CHMOD": CHMOD,
            "MOCK_INSTALLED": str(self.installed),
            "MOCK_BREW_LOG": str(self.brew_log),
            "MOCK_LEDGER_LOG": str(self.ledger_log),
            "MOCK_LEDGER_AFTER": ledger_stub(),
        }
        self.write_executable("brew", BREW_STUB)

    def write_executable(self, name, content):
        path = self.bin / name
        path.write_text(content)
        path.chmod(0o755)

    def run_bootstrap(self, *args):
        return subprocess.run([str(SCRIPT), *args], env=self.env, text=True,
                              capture_output=True, timeout=5, check=False)

    def calls(self, path):
        return path.read_text().splitlines() if path.exists() else []

    def assert_ready(self, result, action="none", version="1.0.3"):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "schema": "ledger-bootstrap-ready/v1", "status": "ready",
            "path": str(self.bin / "ledger"), "version": version,
            "abi": "ledger-artifact-abi/v1", "action": action,
        })

    def assert_blocked(self, result, reason, code=3):
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        error = json.loads(result.stderr.splitlines()[-1])
        self.assertEqual(error["schema"], "ledger-bootstrap-error/v1")
        self.assertEqual(error["status"], "blocked")
        self.assertEqual(error["reason"], reason)
        self.assertTrue(error["remediation"])

    def test_supported_versions_do_not_provision(self):
        for version in ("1.0.3", "1.0.4", "1.1.1"):
            with self.subTest(version=version):
                self.write_executable("ledger", ledger_stub(version=version))
                self.assert_ready(self.run_bootstrap(), version=version)
        self.assertEqual(self.calls(self.brew_log), [])

    def test_bad_versions_and_missing_abi_are_blocked(self):
        for version, abi in (("1.0.2", "ledger-artifact-abi/v1"),
                             ("0.9.9", "ledger-artifact-abi/v1"),
                             ("2.0.0", "ledger-artifact-abi/v1"),
                             ("1.0.3-rc.1", "ledger-artifact-abi/v1"),
                             ("not-a-version", "ledger-artifact-abi/v1"),
                             ("1.0.3", "ledger-artifact-abi/v2"),
                             ("1.0.3", "")):
            with self.subTest(version=version, abi=abi):
                self.write_executable("ledger", ledger_stub(version, abi))
                self.assert_blocked(self.run_bootstrap(), "version-or-abi-mismatch")
        self.assertEqual(self.calls(self.brew_log), [])

    def test_valid_text_from_failed_probes_is_not_readiness(self):
        for version_exit, capabilities_exit in ((7, 0), (0, 9), (7, 9)):
            with self.subTest(version_exit=version_exit,
                              capabilities_exit=capabilities_exit):
                self.write_executable("ledger", ledger_stub(
                    version_exit=version_exit, capabilities_exit=capabilities_exit))
                self.assert_blocked(self.run_bootstrap(), "version-or-abi-mismatch")
        self.assertEqual(self.calls(self.brew_log), [])

    def test_missing_binary_does_not_install_without_authority(self):
        self.assert_blocked(self.run_bootstrap(), "missing")
        self.assertEqual(self.calls(self.brew_log), [])

    def test_incompatible_binary_does_not_upgrade_without_authority(self):
        self.write_executable("ledger", ledger_stub(version="1.0.2"))
        self.installed.touch()
        self.assert_blocked(self.run_bootstrap(), "version-or-abi-mismatch")
        self.assertEqual(self.calls(self.brew_log), [])

    def test_install_ignores_formula_override(self):
        self.env["LEDGER_BOOTSTRAP_FORMULA"] = "other/tap/not-ledger"
        self.assert_ready(self.run_bootstrap("--install"), action="installed")
        self.assertEqual(self.calls(self.brew_log),
                         [f"list --versions {FORMULA}", f"install {FORMULA}"])

    def test_upgrade_ignores_formula_override(self):
        self.env["LEDGER_BOOTSTRAP_FORMULA"] = "other/tap/not-ledger"
        self.write_executable("ledger", ledger_stub(version="1.0.2"))
        self.installed.touch()
        self.assert_ready(self.run_bootstrap("--install"), action="upgraded")
        self.assertEqual(self.calls(self.brew_log),
                         [f"list --versions {FORMULA}", f"upgrade {FORMULA}"])

    def test_failed_probes_after_upgrade_are_not_readiness(self):
        for version_exit, capabilities_exit in ((7, 0), (0, 9)):
            with self.subTest(version_exit=version_exit,
                              capabilities_exit=capabilities_exit):
                self.write_executable("ledger", ledger_stub(version="1.0.2"))
                self.installed.touch()
                self.env["MOCK_LEDGER_AFTER"] = ledger_stub(
                    version_exit=version_exit, capabilities_exit=capabilities_exit)
                self.assert_blocked(self.run_bootstrap("--install"),
                                    "post-upgrade-version-or-abi-mismatch", code=2)

    def test_failed_install_does_not_emit_readiness(self):
        self.env["MOCK_BREW_EXIT"] = "17"
        self.assert_blocked(self.run_bootstrap("--install"),
                            "homebrew-install-failed", code=17)

    def test_failed_upgrade_does_not_emit_readiness(self):
        self.write_executable("ledger", ledger_stub(version="1.0.2"))
        self.installed.touch()
        self.env["MOCK_BREW_EXIT"] = "17"
        self.assert_blocked(self.run_bootstrap("--install"),
                            "homebrew-upgrade-failed", code=2)

    def test_nonformula_binary_is_not_upgraded(self):
        self.write_executable("ledger", ledger_stub(version="1.0.2"))
        self.assert_blocked(self.run_bootstrap("--install"),
                            "version-or-abi-mismatch-nonformula", code=2)
        self.assertEqual(self.calls(self.brew_log), [f"list --versions {FORMULA}"])

    def test_help_and_unknown_arguments_do_not_probe_or_proxy(self):
        result = self.run_bootstrap("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("ensure-ledger [--install]", result.stdout)
        self.assert_blocked(self.run_bootstrap("validate"), "unknown-option", code=2)
        self.assertEqual(self.calls(self.ledger_log), [])
        self.assertEqual(self.calls(self.brew_log), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
