#!/usr/bin/env -S uv run --with pyyaml python
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[2]
VALIDATOR = ROOT / "scripts/validate_synesthesia.py"
ADAPTER = REPO_ROOT / "codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py"


class SynesthesiaValidationTests(unittest.TestCase):
    def test_complete_package_validator_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), "--repo-root", str(REPO_ROOT)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_memory_adapter_exposes_digest_surface(self) -> None:
        spec = importlib.util.spec_from_file_location("synesthesia_memory_note", ADAPTER)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in (
            "build_digest_projection",
            "render_memory_digest",
            "generate_memory_digest",
            "inspect_digest",
        ):
            self.assertTrue(hasattr(module, name), name)

    def test_skill_version_is_3_4(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('version: "3.4.0"', text)
        self.assertIn("latest_synesthesia_digest.md", text)


if __name__ == "__main__":
    unittest.main()
