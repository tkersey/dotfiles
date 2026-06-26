#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

RESOLVE = Path(__file__).resolve().parents[1]
TOOL = RESOLVE / "tools/resolve_mutation_gate.py"
ASSETS = RESOLVE / "assets"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def json_body(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def main() -> int:
    valid = run("--chain", str(ASSETS / "rac-valid.example.yaml"))
    assert valid.returncode == 0, valid.stdout + valid.stderr
    body = json_body(valid)
    assert body["mutation_allowed"] is True, body
    assert body["reason"] == "compiled_review_authority", body
    assert body["missing"] == [], body
    assert body["legal_next_actions"] == [], body

    nonmutation = run("--chain", str(ASSETS / "rac-nonmutation.example.yaml"))
    assert nonmutation.returncode == 2, nonmutation.stdout + nonmutation.stderr
    body = json_body(nonmutation)
    assert body["mutation_allowed"] is False, body
    assert body["reason"] == "uncompiled_review_text", body
    for reason in ("confirmed_cex", "realization_allowed", "gate_mutation_allowed"):
        assert reason in body["missing"], body
    assert body["legal_next_actions"] == [
        "adjudicate_claim",
        "seal_or_repair_batch",
        "compile_or_repair_ceb_mbk_rc",
        "rebase_ac",
        "create_followup",
        "reject_finding",
        "block",
    ], body

    invalid = run("--chain", str(ASSETS / "rac-invalid.example.yaml"))
    assert invalid.returncode == 2, invalid.stdout + invalid.stderr
    body = json_body(invalid)
    for reason in ("artifact_state", "review_claim", "ceb_class", "mbk_transition", "proof_obligation"):
        assert reason in body["missing"], body

    text = run("--chain", str(ASSETS / "rac-nonmutation.example.yaml"), "--format", "text")
    assert text.returncode == 2, text.stdout + text.stderr
    assert "mutation-gate blocked" in text.stdout, text.stdout
    assert "uncompiled_review_text" in text.stdout, text.stdout

    with tempfile.TemporaryDirectory() as td:
        unsupported = Path(td) / "rac.txt"
        unsupported.write_text("not a RAC document\n", encoding="utf-8")
        result = run("--chain", str(unsupported))
        assert result.returncode == 3, result.stdout + result.stderr
        assert json_body(result)["reason"] == "could_not_evaluate_input"

    print("resolve mutation gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
