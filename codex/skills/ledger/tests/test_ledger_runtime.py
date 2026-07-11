import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = SKILL_ROOT / "scripts" / "ledger-runtime"


def write_executable(path: Path, body: str) -> None:
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def fake_ledger(version: str = "0.5.0") -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
if [[ "${{1:-}}" == "--version" ]]; then
  echo "{version}"
elif [[ "${{1:-}}" == "--help" ]]; then
  echo "Durable source-memory, actuation, and plan ledger."
  echo "--source SOURCE"
elif [[ "${{1:-}}" == "fail" ]]; then
  echo "native failure" >&2
  exit 17
else
  printf 'native:'
  printf ' %s' "$@"
  printf '\n'
fi
"""


class LedgerRuntimeTests(unittest.TestCase):
    def run_runtime(self, bin_dir: Path, *args: str, extra_env=None):
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [str(RUNTIME), *args],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_ensure_emits_ready_receipt_for_compatible_native_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            write_executable(bin_dir / "ledger", fake_ledger("0.5.1"))

            result = self.run_runtime(bin_dir, "ensure", "--min-version", "0.5.0")

            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual("ledger-runtime-ready/v1", receipt["schema"])
            self.assertEqual("0.5.1", receipt["version"])
            self.assertEqual("none", receipt["action"])

    def test_run_preserves_native_arguments_and_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            write_executable(bin_dir / "ledger", fake_ledger())

            result = self.run_runtime(
                bin_dir,
                "run",
                "--min-version",
                "0.5.0",
                "--",
                "doctor",
                "--source",
                "learnings",
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("native: doctor --source learnings\n", result.stdout)

    def test_run_preserves_native_stderr_and_exit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            write_executable(bin_dir / "ledger", fake_ledger())

            result = self.run_runtime(bin_dir, "run", "--", "fail")

            self.assertEqual(17, result.returncode)
            self.assertEqual("", result.stdout)
            self.assertEqual("native failure\n", result.stderr)

    def test_missing_runtime_fails_closed_without_install_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_runtime(Path(tmp), "ensure")

            self.assertEqual(3, result.returncode)
            error = json.loads(result.stderr)
            self.assertEqual("missing", error["reason"])

    def test_wrong_binary_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            write_executable(
                bin_dir / "ledger",
                "#!/usr/bin/env bash\necho 'Ledger 3.3.0, the accounting tool'\n",
            )

            result = self.run_runtime(bin_dir, "ensure")

            self.assertEqual(3, result.returncode)
            error = json.loads(result.stderr)
            self.assertEqual("unexpected-ledger-binary", error["reason"])

    def test_install_authority_uses_formula_then_rechecks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            ledger_body = root / "ledger-body"
            ledger_body.write_text(fake_ledger("0.5.0"))
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

            result = self.run_runtime(
                bin_dir,
                "ensure",
                "--install",
                extra_env={
                    "LEDGER_RUNTIME_OS": "Darwin",
                    "FAKE_BREW_LOG": str(brew_log),
                    "FAKE_LEDGER_BODY": str(ledger_body),
                    "FAKE_BIN_DIR": str(bin_dir),
                },
            )

            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual("installed", receipt["action"])
            self.assertIn("install tkersey/tap/ledger", brew_log.read_text())


if __name__ == "__main__":
    unittest.main()
