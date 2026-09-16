"""Exercise both lexical-audit backends without installing Lean."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/lean_trust_audit.sh"
BASH = shutil.which("bash")


class TrustAuditTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(BASH)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.sources = self.root / "sources with spaces"
        self.sources.mkdir()
        self.environments = {}
        for backend in ("rg", "grep"):
            if backend == "rg" and shutil.which("rg") is None:
                continue
            bin_dir = self.root / f"{backend}-bin"
            bin_dir.mkdir()
            for name in (("rg",) if backend == "rg" else ("find", "grep")):
                executable = shutil.which(name)
                self.assertIsNotNone(executable)
                (bin_dir / name).symlink_to(executable)
            self.environments[backend] = dict(os.environ, PATH=str(bin_dir))

    def run_scan(self, backend, *paths):
        return subprocess.run(
            [BASH, str(SCRIPT), *map(str, paths)],
            env=self.environments[backend], cwd=self.sources,
            text=True, capture_output=True, timeout=10,
        )

    def test_matches_clean_and_missing_targets_in_both_backends(self):
        clean = self.sources / "clean.lean"
        clean.write_text("theorem identity (n : Nat) : n = n := rfl\n")
        matching = self.sources / "with space.lean"
        matching.write_text("theorem unfinished : True := by sorry\n")
        for backend in self.environments:
            with self.subTest(backend=backend):
                result = self.run_scan(backend, clean)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual("", result.stdout)
                result = self.run_scan(backend, matching)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("sorry", result.stdout)
                self.assertNotEqual(0, self.run_scan(backend, "missing.lean").returncode)
                self.assertNotEqual(0, self.run_scan(backend, clean, "missing.lean").returncode)

    def test_review_features_in_both_backends(self):
        # These are lexical fixtures, not claims that each line is a Lean proof.
        fixtures = (
            "sorry", "admit", "axiom", "unsafe", "partial", "noncomputable",
            "native_decide", "bv_decide", "bv_decide?",
            "grind => bv_decide", 'bv_check "proof.lrat"',
            "decide +native", "decide\t+native",
            "@[implemented_by fast]", "@[csimp]", '@[extern "runtime_fn"]',
            "Lean.bv_decide", "(bv_check)",
        )
        target = self.sources / "features.lean"
        for backend in self.environments:
            for fixture in fixtures:
                with self.subTest(backend=backend, fixture=fixture):
                    target.write_text(fixture + "\n")
                    result = self.run_scan(backend, target)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn(fixture, result.stdout)

    def test_containing_identifiers_are_not_feature_uses(self):
        target = self.sources / "identifiers.lean"
        target.write_text(
            "def bv_decide_helper := 1\ndef prebv_check := 1\n"
            "def native_decide_helper := 1\ndef my_axiom := 1\n"
            "def externally := 1\ndef csimple := 1\n"
            "def implemented_by_helper := 1\n"
        )
        for backend in self.environments:
            with self.subTest(backend=backend):
                result = self.run_scan(backend, target)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual("", result.stdout)

    def test_excludes_dependencies_builds_and_non_lean_files(self):
        for relative in (
            ".lake/cache.lean", "lake-packages/dependency.lean", "build/output.lean",
            "nested/.lake/cache.lean", "nested/lake-packages/dependency.lean",
            "nested/build/output.lean", "notes.txt",
        ):
            target = self.sources / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("sorry\n")
        own_file = self.sources / "nested/source.lean"
        own_file.write_text("bv_decide\n")
        for backend in self.environments:
            with self.subTest(backend=backend):
                # Absolute roots must get the same exclusions as relative roots.
                for path in (self.sources, Path(".")):
                    result = self.run_scan(backend, path)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("bv_decide", result.stdout)
                    self.assertNotIn("sorry", result.stdout)

    def test_default_target_is_current_directory(self):
        target = self.sources / "source.lean"
        target.write_text("bv_decide\n")
        for backend in self.environments:
            with self.subTest(backend=backend):
                result = self.run_scan(backend)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("source.lean", result.stdout)
                self.assertIn("bv_decide", result.stdout)

    def test_help(self):
        for flag in ("-h", "--help"):
            with self.subTest(flag=flag):
                # Help uses cat, whereas scanning backends intentionally have a minimal PATH.
                result = subprocess.run(
                    [BASH, str(SCRIPT), flag], text=True, capture_output=True, timeout=10,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("lexical audit aid", result.stdout)


if __name__ == "__main__":
    unittest.main()
