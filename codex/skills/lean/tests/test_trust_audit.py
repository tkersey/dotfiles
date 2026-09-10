"""The lexical audit must distinguish no matches from a failed scan."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/lean_trust_audit.sh"
BASH = shutil.which("bash")


class TrustAuditTests(unittest.TestCase):
    def test_matches_clean_and_missing_targets_in_both_backends(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clean = root / "clean.lean"
            clean.write_text("theorem identity (n : Nat) : n = n := rfl\n")
            matching = root / "with space.lean"
            matching.write_text("theorem unfinished : True := by sorry\n")
            fallback = root / "fallback-bin"
            fallback.mkdir()
            for name in ("find", "grep"):
                executable = shutil.which(name)
                self.assertIsNotNone(executable)
                (fallback / name).symlink_to(executable)
            for backend in ("rg", "grep"):
                with self.subTest(backend=backend):
                    env = dict(os.environ)
                    if backend == "rg":
                        if shutil.which("rg") is None:
                            continue
                    else:
                        env["PATH"] = str(fallback)

                    def run(*paths):
                        return subprocess.run(
                            [BASH, str(SCRIPT), *map(str, paths)], env=env,
                            text=True, capture_output=True,
                        )

                    result = run(clean)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual("", result.stdout)
                    result = run(matching)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("sorry", result.stdout)
                    self.assertNotEqual(0, run(root / "missing.lean").returncode)
                    self.assertNotEqual(0, run(clean, root / "missing.lean").returncode)


if __name__ == "__main__":
    unittest.main()
