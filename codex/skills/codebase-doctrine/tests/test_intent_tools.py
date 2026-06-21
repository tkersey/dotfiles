#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"


def run(tool: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / tool), *map(str, args)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    for fixture in (
        "doctrine-intent-gate.direct.example.json",
        "doctrine-intent-gate.grill.example.json",
        "codebase-doctrine-intent.example.json",
    ):
        result = run("intent_gate.py", ASSETS / fixture)
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout)["intent_gate"]["verdict"] == "pass"

    grill = run(
        "intent_gate.py",
        "--require-plan-allowed",
        ASSETS / "grill-decision-packet.example.yaml",
    )
    assert grill.returncode == 0, grill.stdout + grill.stderr

    doctrine = run(
        "doctrine_gate.py",
        "--require-intent",
        "--require-saturated",
        ASSETS / "codebase-doctrine.example.json",
    )
    assert doctrine.returncode == 0, doctrine.stdout + doctrine.stderr
    result = json.loads(doctrine.stdout)["doctrine_gate"]
    assert result["counts"]["intent_present"] == 1

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        bad_dig = json.loads(
            (ASSETS / "doctrine-intent-gate.grill.example.json").read_text()
        )
        bad_dig["doctrine_intent_gate"]["material_user_judgment_gaps"][0][
            "discoverable_from_artifacts"
        ] = "yes"
        path = temp / "bad-dig.json"
        path.write_text(json.dumps(bad_dig))
        result = run("intent_gate.py", path)
        assert result.returncode == 2
        assert "discoverable_from_artifacts:must-be-no" in result.stdout

        bad_grill = yaml.safe_load(
            (ASSETS / "grill-decision-packet.example.yaml").read_text()
        )
        bad_grill["grill_decision_packet"]["plan_allowed"] = False
        path = temp / "bad-grill.yaml"
        path.write_text(yaml.safe_dump(bad_grill))
        result = run("intent_gate.py", "--require-plan-allowed", path)
        assert result.returncode == 2
        assert "plan_allowed:not-true" in result.stdout

        bad_cdi = json.loads(
            (ASSETS / "codebase-doctrine-intent.example.json").read_text()
        )
        bad_cdi["codebase_doctrine_intent"]["source"]["grill_packet_digest"] = ""
        path = temp / "bad-cdi.json"
        path.write_text(json.dumps(bad_cdi))
        result = run("intent_gate.py", path)
        assert result.returncode == 2
        assert "grill_packet_digest:required-for-grill" in result.stdout

        mismatch = json.loads(
            (ASSETS / "codebase-doctrine.example.json").read_text()
        )
        mismatch["codebase_doctrine"]["artifact_state"]["intent_id"] = "CDI-other"
        path = temp / "intent-mismatch.json"
        path.write_text(json.dumps(mismatch))
        result = run("doctrine_gate.py", "--require-intent", path)
        assert result.returncode == 2
        assert "artifact_state.intent_id:mismatch" in result.stdout

    print("codebase-doctrine intent tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
