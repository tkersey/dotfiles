#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/policy_synthesis_receipt_gate.py"
ASSETS = ROOT / "assets"


def run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-S", str(TOOL), str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load(name: str) -> dict:
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


def put(root: Path, name: str, value: dict) -> Path:
    path = root / name
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def must_pass(name: str) -> None:
    result = run(ASSETS / name)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"verdict": "pass"' in result.stdout


def must_fail(path: Path, needle: str) -> None:
    result = run(path)
    assert result.returncode == 2, result.stdout + result.stderr
    assert needle in result.stdout, result.stdout


def main() -> int:
    must_pass("policy-synthesis-receipt.example.json")
    must_pass("policy-synthesis-receipt.rejected-radical.example.json")

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        value = load("policy-synthesis-receipt.example.json")
        value["policy_synthesis_receipt"]["passes"] = value["policy_synthesis_receipt"]["passes"][:2]
        must_fail(put(temp, "missing-lenses.json", value), "missing-lenses")

        value = load("policy-synthesis-receipt.example.json")
        value["policy_synthesis_receipt"]["radical_candidate"]["disposition"] = "skip"
        must_fail(put(temp, "bad-radical.json", value), "radical_candidate.disposition")

        value = load("policy-synthesis-receipt.example.json")
        value["policy_synthesis_receipt"]["convergence"]["independent_press_pass_clean"] = False
        must_fail(put(temp, "no-press.json", value), "requires-press-pass")

        value = load("policy-synthesis-receipt.example.json")
        value["policy_synthesis_receipt"]["passes"][-1]["material_changes"] = ["hidden late change"]
        must_fail(put(temp, "clean-with-change.json", value), "clean-with-material_changes")

        value = load("policy-synthesis-receipt.example.json")
        value["policy_synthesis_receipt"]["convergence"]["unresolved_errors"] = 1
        must_fail(put(temp, "unresolved.json", value), "unresolved-errors")

    print("policy synthesis receipt gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
