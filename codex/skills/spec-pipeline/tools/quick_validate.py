#!/usr/bin/env -S uv run python
"""Run the lightweight spec-pipeline auto-plan validation suite."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(TESTS), "-p", "test_*.py"],
        text=True,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
