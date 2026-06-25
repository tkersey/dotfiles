#!/usr/bin/env -S uv run --with pyyaml python
"""Run the complete skill-local Codebase Doctrine validation suite."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
CODEX_ROOT = ROOT.parents[1]
REPO = ROOT.parents[2]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"
SCHEMAS = ROOT / "schemas"
TESTS = ROOT / "tests"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *map(str, args)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    failures: list[str] = []
    checks: list[str] = []

    commands = [
        ("intent-direct", TOOLS / "intent_gate.py", ASSETS / "doctrine-intent-gate.direct.example.yaml"),
        ("intent-grill-gate", TOOLS / "intent_gate.py", ASSETS / "doctrine-intent-gate.grill.example.yaml"),
        (
            "grill-closure",
            TOOLS / "intent_gate.py",
            ASSETS / "grill-decision-packet.example.yaml",
            "--require-plan-allowed",
        ),
        ("intent", TOOLS / "intent_gate.py", ASSETS / "codebase-doctrine-intent.example.yaml"),
        (
            "doctrine",
            TOOLS / "doctrine_gate.py",
            ASSETS / "codebase-doctrine.example.yaml",
            "--require-saturated",
        ),
        (
            "packet",
            TOOLS / "packet_gate.py",
            ASSETS / "specialist-packet.example.yaml",
            "--assignment",
            ASSETS / "specialist-assignment.example.yaml",
        ),
        (
            "handoff",
            TOOLS / "handoff_gate.py",
            ASSETS / "codebase-skill-handoff.example.yaml",
            "--doctrine",
            ASSETS / "codebase-doctrine.example.yaml",
        ),
        ("survey", TOOLS / "mode_gate.py", ASSETS / "codebase-survey.example.yaml"),
        ("portfolio", TOOLS / "mode_gate.py", ASSETS / "codebase-portfolio.example.yaml"),
        ("audit", TOOLS / "mode_gate.py", ASSETS / "codebase-doctrine-audit.example.yaml"),
        ("delta", TOOLS / "mode_gate.py", ASSETS / "codebase-doctrine-delta.example.yaml"),
        (
            "workers",
            TOOLS / "worker_suite_check.py",
            "--agents-root",
            CODEX_ROOT / "agents",
        ),
    ]
    for row in commands:
        label, *args = row
        proc = run(*args)
        checks.append(label)
        if proc.returncode != 0:
            failures.append(f"{label}: {proc.stdout.strip()} {proc.stderr.strip()}")

    for path in sorted(SCHEMAS.glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"schema:{path.name}:{exc}")
        checks.append(f"schema:{path.name}")

    contract_lint = CODEX_ROOT / "skills/tune/tools/decision_contract_lint.py"
    if contract_lint.is_file():
        proc = run(contract_lint, ROOT / "references/decision-contract.yaml")
        checks.append("decision-contract")
        if proc.returncode != 0:
            failures.append(
                f"decision-contract: {proc.stdout.strip()} {proc.stderr.strip()}"
            )

    proc = run(
        "-m",
        "unittest",
        "discover",
        "-s",
        TESTS,
        "-p",
        "test_*.py",
    )
    checks.append("unit-tests")
    if proc.returncode != 0:
        failures.append(f"unit-tests: {proc.stdout.strip()} {proc.stderr.strip()}")

    result = {
        "codebase_doctrine_validation": {
            "verdict": "pass" if not failures else "fail",
            "version": "2.0.1",
            "checks": checks,
            "failures": failures,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
