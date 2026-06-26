#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

RESOLVE = Path(__file__).resolve().parents[1]
TOOL = RESOLVE / "tools/resolve_authority_chain_gate.py"
ASSETS = RESOLVE / "assets"


def run(path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), str(path), *extra],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def json_body(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def main() -> int:
    valid = run(ASSETS / "rac-valid.example.yaml")
    assert valid.returncode == 0, valid.stdout + valid.stderr
    body = json_body(valid)
    assert body["status"] == "valid", body
    assert body["mutation_allowed"] is True, body
    assert body["missing"] == [], body
    assert body["violations"] == [], body
    assert body["chain_id"] == "RAC-example", body

    valid_text = run(ASSETS / "rac-valid.example.yaml", "--format", "text")
    assert valid_text.returncode == 0, valid_text.stdout + valid_text.stderr
    assert "RAC-v1 valid" in valid_text.stdout, valid_text.stdout
    assert "mutation_allowed=true" in valid_text.stdout, valid_text.stdout

    nonmutation = run(ASSETS / "rac-nonmutation.example.yaml")
    assert nonmutation.returncode == 0, nonmutation.stdout + nonmutation.stderr
    body = json_body(nonmutation)
    assert body["status"] == "valid", body
    assert body["mutation_allowed"] is False, body
    assert body["missing"] == [], body
    assert body["violations"] == [], body

    invalid = run(ASSETS / "rac-invalid.example.yaml")
    assert invalid.returncode == 2, invalid.stdout + invalid.stderr
    body = json_body(invalid)
    assert body["status"] == "invalid", body
    for reason in (
        "missing_artifact_state",
        "missing_review_claim",
        "missing_horizon",
        "missing_law_refs",
        "missing_ceb_class",
        "missing_mbk_or_rc",
        "missing_transition",
        "missing_proof_obligation",
    ):
        assert reason in body["missing"], body
    for reason in (
        "unrelated_or_rejected",
        "invalid_cex",
        "unsealed_batch",
        "artifact_state_stale",
        "mutation_gate_disagrees",
    ):
        assert reason in body["violations"], body

    missing = run(ASSETS / "does-not-exist.yaml")
    assert missing.returncode == 3, missing.stdout + missing.stderr

    with tempfile.TemporaryDirectory() as td:
        unsupported = Path(td) / "rac.txt"
        unsupported.write_text("not a RAC document\n", encoding="utf-8")
        result = run(unsupported)
        assert result.returncode == 3, result.stdout + result.stderr

    print("resolve authority-chain gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
