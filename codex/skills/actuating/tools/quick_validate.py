#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "references/pre-mutation-interlock.md",
        "tools/actuation_authority_gate.py",
        "tests/test_actuation_authority_gate.py",
        "assets/gcr-v2.allowed.example.json",
        "assets/gcr-v2.self-invalidating.example.json",
        "assets/apma-v1.example.json",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        print(json.dumps({"actuating_quick_validate": {"verdict": "fail", "missing": missing}}, indent=2))
        return 2
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tests/test_actuation_authority_gate.py")],
        text=True,
        capture_output=True,
        check=False,
    )
    verdict = "pass" if proc.returncode == 0 else "fail"
    print(json.dumps({
        "actuating_quick_validate": {
            "verdict": verdict,
            "test_returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    }, indent=2))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
