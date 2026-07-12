import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = SKILL_ROOT / "scripts" / "ensure-ledger"


def write_executable(path: Path, body: str) -> None:
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def fake_ledger() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${FAKE_LEDGER_LOG:-}" ]]; then
  printf 'invoked\n' >> "$FAKE_LEDGER_LOG"
fi
exit 97
"""


class EnsureLedgerTests(unittest.TestCase):
    def run_bootstrap(self, bin_dir: Path, *args: str, extra_env=None):
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [str(BOOTSTRAP), *args],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_emits_ready_receipt_without_invoking_native_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            invocation_log = bin_dir / "ledger.log"
            write_executable(bin_dir / "ledger", fake_ledger())

            result = self.run_bootstrap(
                bin_dir,
                extra_env={"FAKE_LEDGER_LOG": str(invocation_log)},
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse(invocation_log.exists())
            receipt = json.loads(result.stdout)
            self.assertEqual("ledger-bootstrap-ready/v1", receipt["schema"])
            self.assertEqual(str(bin_dir / "ledger"), receipt["path"])
            self.assertEqual("none", receipt["action"])

    def test_does_not_proxy_native_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            write_executable(bin_dir / "ledger", fake_ledger())

            result = self.run_bootstrap(bin_dir, "doctor")

            self.assertEqual(2, result.returncode)
            self.assertEqual("", result.stdout)
            self.assertEqual("unknown-option", json.loads(result.stderr)["reason"])

    def test_does_not_accept_a_version_constraint(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            write_executable(bin_dir / "ledger", fake_ledger())

            result = self.run_bootstrap(bin_dir, "--min-version", "0.5.0")

            self.assertEqual(2, result.returncode)
            self.assertEqual("unknown-option", json.loads(result.stderr)["reason"])

    def test_missing_cli_fails_closed_without_install_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_bootstrap(Path(tmp))

            self.assertEqual(3, result.returncode)
            receipt = json.loads(result.stderr)
            self.assertEqual("missing", receipt["reason"])
            self.assertIn("ensure-ledger --install", receipt["remediation"])

    def test_bootstrap_does_not_duplicate_cli_version_or_identity_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            write_executable(
                bin_dir / "ledger",
                "#!/usr/bin/env bash\necho 'unrelated ledger 0.0.1'\nexit 41\n",
            )

            result = self.run_bootstrap(bin_dir)

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("ledger-bootstrap-ready/v1", json.loads(result.stdout)["schema"])

    def test_install_authority_uses_formula_then_rechecks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            ledger_body = root / "ledger-body"
            ledger_body.write_text(fake_ledger())
            brew_log = root / "brew.log"
            write_executable(
                bin_dir / "brew",
                """#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$*" >> "$FAKE_BREW_LOG"
if [[ "${1:-}" == "list" ]]; then
  exit 1
fi
if [[ "${1:-}" == "install" ]]; then
  cp "$FAKE_LEDGER_BODY" "$FAKE_BIN_DIR/ledger"
  chmod +x "$FAKE_BIN_DIR/ledger"
fi
""",
            )

            result = self.run_bootstrap(
                bin_dir,
                "--install",
                extra_env={
                    "LEDGER_BOOTSTRAP_OS": "Darwin",
                    "FAKE_BREW_LOG": str(brew_log),
                    "FAKE_LEDGER_BODY": str(ledger_body),
                    "FAKE_BIN_DIR": str(bin_dir),
                },
            )

            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual("installed", receipt["action"])
            self.assertIn("install tkersey/tap/ledger", brew_log.read_text())

    def test_homebrew_install_failure_is_not_masked(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            write_executable(
                bin_dir / "brew",
                """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "list" ]]; then
  exit 1
fi
if [[ "${1:-}" == "install" ]]; then
  exit 42
fi
""",
            )

            result = self.run_bootstrap(
                bin_dir,
                "--install",
                extra_env={"LEDGER_BOOTSTRAP_OS": "Darwin"},
            )

            self.assertEqual(42, result.returncode)
            self.assertEqual("homebrew-install-failed", json.loads(result.stderr)["reason"])


if __name__ == "__main__":
    unittest.main()
