#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run_test(path: Path) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "path": str(path.relative_to(ROOT)),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def main() -> int:
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "references/pre-mutation-interlock.md",
        "references/delivery-handoff.md",
        "references/terminal-closure-gate.md",
        "references/refactor-kernel-receipts.md",
        "references/decision-contract.yaml",
        "tools/actuation_delivery_gate.py",
        "tools/actuation_refactor_kernel_gate.py",
        "tools/actuation_terminal_gate.py",
        "tests/test_actuation_delivery_gate.py",
        "tests/test_actuation_refactor_kernel_gate.py",
        "tests/test_actuation_terminal_gate.py",
        "tests/test_aer_contract.py",
        "tests/test_review_mode_contract.py",
        "assets/apma-v1.example.json",
        "assets/delivery-context.ready.example.json",
        "assets/delivery-context.no-pr-intent.example.json",
        "assets/delivery-context.blocked.example.json",
        "assets/add-v1.handoff.example.json",
        "assets/add-v1.shipping-not-requested.example.json",
        "assets/add-v1.blocked.example.json",
        "assets/aer-v1.example.json",
        "assets/rko-v1.effective.example.json",
        "assets/atcg-v1.complete.example.json",
        "assets/terminal-context.proof-only.example.json",
        "assets/terminal-context.hylo-complete.example.json",
        "assets/terminal-context.regression.example.json",
        "assets/terminal-context.ship-continue.example.json",
        "assets/terminal-context.advisory-would-block.example.json",
        "assets/terminal-context.advisory-fused.example.json",
        "assets/terminal-context.fusion-missing.example.json",
        "assets/unsupported-coordination.example.json",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        print(json.dumps({"actuating_quick_validate": {"verdict": "fail", "missing": missing}}, indent=2))
        return 2
    tests = [
        run_test(ROOT / "tests/test_actuation_delivery_gate.py"),
        run_test(ROOT / "tests/test_actuation_refactor_kernel_gate.py"),
        run_test(ROOT / "tests/test_actuation_terminal_gate.py"),
        run_test(ROOT / "tests/test_aer_contract.py"),
        run_test(ROOT / "tests/test_review_mode_contract.py"),
    ]
    ok = all(row["returncode"] == 0 for row in tests)
    print(json.dumps({"actuating_quick_validate": {"verdict": "pass" if ok else "fail", "tests": tests}}, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
