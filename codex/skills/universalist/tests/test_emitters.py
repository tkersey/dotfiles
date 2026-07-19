#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "scripts" / "emit_boundary_adapter.py"
SCAFFOLD = ROOT / "scripts" / "emit_scaffold.py"


class EmitterContractTest(unittest.TestCase):
    def run_script(self, script: Path, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(script), *args],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, expected, completed.stderr)
        return completed

    def test_typescript_decoder_is_fail_closed(self) -> None:
        output = self.run_script(ADAPTER, "decoder", "typescript").stdout
        self.assertIn("DecodeResult<CoreShape>", output)
        self.assertIn("VALIDATION_NOT_IMPLEMENTED", output)
        self.assertNotIn("input as CoreShape", output)
        self.assertNotIn("return input", output)

    def test_python_decoder_avoids_any_identity_cast(self) -> None:
        output = self.run_script(ADAPTER, "decoder", "python").stdout
        self.assertIn("value: object", output)
        self.assertIn("CoreShape | DecodeError", output)
        self.assertNotIn("typing import Any", output)
        self.assertNotIn("return value", output)

    def test_argument_contract_rejects_unknown_kind_or_language(self) -> None:
        self.run_script(ADAPTER, "typescript", "decoder", expected=2)
        self.run_script(ADAPTER, "decoder", "ruby", expected=2)

    def test_generated_python_is_syntactically_valid(self) -> None:
        output = self.run_script(ADAPTER, "decoder", "python").stdout
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "adapter.py"
            path.write_text(output, encoding="utf-8")
            subprocess.run([sys.executable, "-m", "py_compile", str(path)], check=True)

    def test_scaffold_matches_the_full_output_contract(self) -> None:
        output = self.run_script(SCAFFOLD, "boundary", "typescript").stdout
        for heading in (
            "## Track", "## Signal", "## Ordinary candidate", "## Universal shadow",
            "## Material architectural delta", "## Construction",
            "## Why this instead of nearby alternatives", "## Seam / files",
            "## Boundary and compatibility plan", "## Before -> After",
            "## Verification", "## Runtime-only leftovers", "## Next seam",
        ):
            self.assertIn(heading, output)


if __name__ == "__main__":
    unittest.main()
