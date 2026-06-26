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
        "realization_not_allowed",
        "incomplete_chain",
    ):
        assert reason in body["violations"], body

    missing = run(ASSETS / "does-not-exist.yaml")
    assert missing.returncode == 3, missing.stdout + missing.stderr

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        no_wrapper = root / "no-wrapper.json"
        no_wrapper.write_text(json.dumps({"chain_version": "RAC-v1"}), encoding="utf-8")
        result = run(no_wrapper)
        assert result.returncode == 3, result.stdout + result.stderr

        weak = root / "weak.json"
        weak.write_text(
            json.dumps(
                {
                    "resolve_authority_chain": {
                        "chain_version": "RAC-v1",
                        "chain_id": "",
                        "campaign_id": "c3-example",
                        "artifact_state": {"base_sha": "base", "head_sha": "", "dirty_fingerprint": "clean", "review_receipt": "review"},
                        "review_claim": {"claim_id": "claim"},
                        "acceptance": {"contract_id": "ac", "contract_fingerprint": "sha256:ac", "horizon_fingerprint": "sha256:h", "law_refs": [""], "relation": "contract_invalidating"},
                        "adjudication": {"cex_id": "cex", "validity": "confirmed", "liability": "none", "novelty": "duplicate", "disposition": "refuted"},
                        "batch": {"batch_id": "batch", "sealed": True, "mode": "terminal_holdout"},
                        "compression": {"ceb_id": "ceb", "class_id": "class", "class_status": "rejected", "quotient_witness_ref": "w", "mbk_id": "mbk", "rc_id": "rc", "transition_ref": "t", "proof_obligation_ref": "p"},
                        "realization": {"allowed": True},
                        "gate": {"current_artifact_state": "yes", "complete_chain": "yes", "mutation_allowed": "yes"},
                    }
                }
            ),
            encoding="utf-8",
        )
        result = run(weak)
        assert result.returncode == 2, result.stdout + result.stderr
        body = json_body(result)
        assert "missing_chain_identity" in body["missing"], body
        assert "missing_artifact_state" in body["missing"], body
        assert "missing_review_claim" in body["missing"], body
        assert "missing_law_refs" in body["missing"], body
        assert "outside_horizon" in body["violations"], body
        assert "invalid_cex" in body["violations"], body
        assert "unsealed_batch" in body["violations"], body
        assert "ceb_class_not_accepted" in body["violations"], body
        assert "realization_not_allowed" in body["violations"], body

        unsupported = Path(td) / "rac.txt"
        unsupported.write_text("not a RAC document\n", encoding="utf-8")
        result = run(unsupported)
        assert result.returncode == 3, result.stdout + result.stderr

    print("resolve authority-chain gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
